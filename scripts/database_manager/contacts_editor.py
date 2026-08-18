import streamlit as st
import sqlite3
import pandas as pd
import re
import sys
import os
from datetime import datetime

sys.path.insert(0, r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\campaign_manager")
from drafts import load_gmail_accounts, create_full_campaign, group_by_sender, chunk_recipients
from campaign_ui import (
    get_connection, get_dashboard_stats, get_campaigns_list,
    get_campaign_recipients, get_campaign_recipient_count,
    get_contacts_for_selection, get_list_values, register_campaign,
    get_sender_stats, get_campaigns_by_month,
)

st.set_page_config(page_title="Contacts DB", layout="wide")

DB_PATH = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\data\inputs\contacts.db"

CAMPAIGN_SEP = " || "


@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def parse_campaigns(campaigns_str):
    if not campaigns_str:
        return []
    entries = []
    parts = campaigns_str.split(CAMPAIGN_SEP)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "Subj:" in part:
            subj_m = re.search(r"Subj:([^|/]+)", part)
            date_m = re.search(r"Date:([^|/]+)", part)
            sender_m = re.search(r"From:([^|/]+)", part) or re.search(r"Sender:([^|/]+)", part)
            type_m = re.search(r"Type:([^|/]+)", part)
            snip_m = re.search(r"Snip:([^|/]+)", part) or re.search(r"Preview:([^|/]+)", part)
            entries.append({
                "type": type_m.group(1).strip() if type_m else "unknown",
                "subject": subj_m.group(1).strip() if subj_m else "",
                "sender": sender_m.group(1).strip() if sender_m else "",
                "date": date_m.group(1).strip() if date_m else "",
                "preview": (snip_m.group(1).strip()[:100] if snip_m else ""),
            })
        else:
            fields = part.split(",")
            if len(fields) >= 4:
                entries.append({
                    "type": "old",
                    "subject": fields[2].strip() if len(fields) > 2 else "",
                    "sender": fields[3].strip() if len(fields) > 3 else "",
                    "date": fields[4].strip() if len(fields) > 4 else "",
                    "preview": "",
                })
    return entries


def load_contacts(page, page_size, search, filters):
    conn = get_connection()
    query = """
        SELECT m.ROWID as rowid, m.id, m.title, m.sector, m.address, m.city, m.province, m.country, m.entity_type,
               l.primary_email, l.secondary_emails, l.website, l.google_maps, l.phone,
               c.sender, c.deliverability, c.email_last_response, c.last_subject_received, c.smtp_processed, c.date_added
        FROM main m
        JOIN lead l ON m.ROWID = l.ROWID
        JOIN contact c ON m.ROWID = c.ROWID
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (l.primary_email LIKE ? OR m.title LIKE ? OR m.sector LIKE ? OR m.city LIKE ? OR m.country LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s, s])

    if filters.get("sender"):
        query += " AND c.sender = ?"
        params.append(filters["sender"])

    if filters.get("deliverability"):
        query += " AND c.deliverability = ?"
        params.append(filters["deliverability"])

    count_query = query.replace("SELECT m.ROWID as rowid, m.id, m.title, m.sector, m.address, m.city, m.province, m.country, m.entity_type,\n               l.primary_email, l.secondary_emails, l.website, l.google_maps, l.phone,\n               c.sender, c.deliverability, c.email_last_response, c.last_subject_received, c.smtp_processed, c.date_added", "SELECT COUNT(*)")
    total = pd.read_sql_query(count_query, conn, params=params).iloc[0, 0]

    query += " ORDER BY m.ROWID DESC LIMIT ? OFFSET ?"
    params.extend([page_size, (page - 1) * page_size])

    df = pd.read_sql_query(query, conn, params=params)
    return df, total


def update_field(table, rowid, field, value):
    conn = get_connection()
    conn.execute(f"UPDATE {table} SET {field} = ? WHERE ROWID = ?", (value, rowid))
    conn.commit()


def delete_contact(rowid):
    conn = get_connection()
    conn.execute("DELETE FROM main WHERE ROWID = ?", (rowid,))
    conn.execute("DELETE FROM lead WHERE ROWID = ?", (rowid,))
    conn.execute("DELETE FROM contact WHERE ROWID = ?", (rowid,))
    conn.execute("DELETE FROM campaign WHERE contact_rowid = ?", (rowid,))
    conn.commit()


def tab_contacts(conn):
    stats_cols = st.columns(5)
    total = pd.read_sql_query("SELECT COUNT(*) as c FROM main", conn).iloc[0, 0]
    with_sender = pd.read_sql_query('SELECT COUNT(*) as c FROM contact WHERE sender IS NOT NULL AND sender != ""', conn).iloc[0, 0]
    with_deliverability = pd.read_sql_query('SELECT COUNT(*) as c FROM contact WHERE deliverability IS NOT NULL AND deliverability != ""', conn).iloc[0, 0]
    with_campaigns = pd.read_sql_query("SELECT COUNT(DISTINCT contact_rowid) as c FROM campaign WHERE contact_rowid IS NOT NULL", conn).iloc[0, 0]
    with_email = pd.read_sql_query('SELECT COUNT(*) as c FROM lead WHERE primary_email IS NOT NULL AND primary_email != ""', conn).iloc[0, 0]

    stats_cols[0].metric("Total", f"{total:,}")
    stats_cols[1].metric("Con sender", f"{with_sender:,}")
    stats_cols[2].metric("Con deliverability", f"{with_deliverability:,}")
    stats_cols[3].metric("Con campaigns", f"{with_campaigns:,}")
    stats_cols[4].metric("Con email", f"{with_email:,}")

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("Buscar (email, title, sector, city, country)")
    with col2:
        senders = pd.read_sql_query('SELECT DISTINCT sender FROM contact WHERE sender IS NOT NULL AND sender != "" ORDER BY sender', conn)["sender"].tolist()
        sender_filter = st.selectbox("Sender", [""] + senders)
    with col3:
        deliv = pd.read_sql_query('SELECT DISTINCT deliverability FROM contact WHERE deliverability IS NOT NULL AND deliverability != "" ORDER BY deliverability', conn)["deliverability"].tolist()
        deliv_filter = st.selectbox("Deliverability", [""] + deliv)
    with col4:
        page_size = st.selectbox("Filas", [25, 50, 100, 200], index=1)

    filters = {}
    if sender_filter:
        filters["sender"] = sender_filter
    if deliv_filter:
        filters["deliverability"] = deliv_filter

    if "page" not in st.session_state:
        st.session_state.page = 1

    df, total_filtered = load_contacts(st.session_state.page, page_size, search, filters)

    total_pages = max(1, (total_filtered + page_size - 1) // page_size)

    st.write(f"Mostrando {len(df)} de {total_filtered:,} contactos (Pagina {st.session_state.page}/{total_pages})")

    nav_cols = st.columns([1, 1, 1, 1])
    with nav_cols[0]:
        if st.button("Anterior") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()
    with nav_cols[1]:
        if st.button("Siguiente") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()
    with nav_cols[2]:
        page_input = st.number_input("Ir a pagina", min_value=1, max_value=total_pages, value=st.session_state.page)
        if st.button("Ir"):
            st.session_state.page = page_input
            st.rerun()

    st.divider()

    if not df.empty:
        display_cols = ["rowid", "primary_email", "title", "sector", "sender", "deliverability", "city", "country"]
        existing = [c for c in display_cols if c in df.columns]
        display_df = df[existing].copy()
        st.dataframe(display_df, width="stretch", hide_index=True)

        st.divider()
        st.subheader("Editar contacto")

        selected_rowid = st.selectbox("Seleccionar ROWID", df["rowid"].tolist(), format_func=lambda x: f"ROWID {x}")

        if selected_rowid:
            contact = df[df["rowid"] == selected_rowid].iloc[0]

            with st.form("edit_form"):
                edit_cols = st.columns(2)
                fields = {}

                main_fields = ["title", "sector", "entity_type", "address", "city", "province", "country"]
                lead_fields = ["primary_email", "secondary_emails", "website", "phone"]
                contact_fields = ["sender", "deliverability", "email_last_response", "last_subject_received"]

                all_fields = main_fields + lead_fields + contact_fields

                for i, field in enumerate(all_fields):
                    with edit_cols[i % 2]:
                        val = contact.get(field, "") or ""
                        fields[field] = st.text_area(field, value=str(val), height=68)

                submitted = st.form_submit_button("Guardar cambios")
                if submitted:
                    for field, value in fields.items():
                        if field in main_fields:
                            update_field("main", selected_rowid, field, value)
                        elif field in lead_fields:
                            update_field("lead", selected_rowid, field, value)
                        elif field in contact_fields:
                            update_field("contact", selected_rowid, field, value)
                    st.success("Contacto actualizado")
                    st.rerun()

            with st.expander("Eliminar contacto"):
                if st.button(f"Eliminar ROWID {selected_rowid}", type="primary"):
                    delete_contact(selected_rowid)
                    st.success("Contacto eliminado")
                    st.rerun()


def tab_asuntos(conn):
    st.subheader("Asuntos de campanas")

    df_campaigns = pd.read_sql_query(
        """SELECT ca.contact_rowid, ca.subject, ca.sender, ca.date, ca.type, ca.list_val,
                  l.primary_email, m.city, m.country, m.sector
           FROM campaign ca
           JOIN main m ON ca.contact_rowid = m.ROWID
           JOIN lead l ON ca.contact_rowid = l.ROWID
           WHERE ca.subject IS NOT NULL AND ca.subject != '' AND ca.contact_rowid IS NOT NULL""",
        conn,
    )

    if df_campaigns.empty:
        st.info("No hay asuntos para mostrar")
        return

    subjects = sorted(df_campaigns["subject"].unique().tolist())
    senders = sorted(df_campaigns["sender"].unique().tolist())
    types = sorted(df_campaigns["type"].unique().tolist())

    stats_cols = st.columns(4)
    stats_cols[0].metric("Asuntos unicos", f"{len(subjects):,}")
    stats_cols[1].metric("Total entradas", f"{len(df_campaigns):,}")
    stats_cols[2].metric("Emails unicos", f"{df_campaigns['primary_email'].nunique():,}")
    stats_cols[3].metric("Types", ", ".join(types[:5]))

    st.divider()

    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    with fcol1:
        search_subj = st.text_input("Buscar asunto", key="search_subj")
    with fcol2:
        sender_filter = st.selectbox("Sender", [""] + senders, key="sender_subj")
    with fcol3:
        type_filter = st.selectbox("Type", [""] + types, key="type_subj")
    with fcol4:
        page_size = st.selectbox("Filas", [25, 50, 100], index=1, key="page_subj")

    filtered = df_campaigns.copy()
    if search_subj:
        filtered = filtered[filtered["subject"].str.contains(search_subj, case=False, na=False)]
    if sender_filter:
        filtered = filtered[filtered["sender"] == sender_filter]
    if type_filter:
        filtered = filtered[filtered["type"] == type_filter]

    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    if "page_subj" not in st.session_state:
        st.session_state.page_subj = 1
    page = st.session_state.page_subj
    start = (page - 1) * page_size
    page_df = filtered.iloc[start:start + page_size]

    st.write(f"Mostrando {len(page_df)} de {len(filtered):,} entradas (Pagina {page}/{total_pages})")

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        if st.button("Anterior", key="prev_subj") and page > 1:
            st.session_state.page_subj -= 1
            st.rerun()
    with pcol2:
        if st.button("Siguiente", key="next_subj") and page < total_pages:
            st.session_state.page_subj += 1
            st.rerun()

    st.divider()

    show_df = page_df[["subject", "primary_email", "type", "sender", "date", "city", "country"]].copy()
    show_df["date"] = show_df["date"].apply(lambda x: str(x)[:19] if x else "")
    st.dataframe(show_df, width="stretch", hide_index=True)

    with st.expander("Ver top 10 asuntos por frecuencia"):
        top_subj = df_campaigns["subject"].value_counts().head(10)
        st.dataframe(top_subj.reset_index().rename(columns={"subject": "asunto", "count": "frecuencia"}), hide_index=True)


def tab_listas(conn):
    st.subheader("Listas de contactos")

    df_lists = pd.read_sql_query(
        """SELECT DISTINCT ca.list_val, l.primary_email, m.title, m.city, m.country, m.sector, c.sender, c.deliverability
           FROM campaign ca
           JOIN main m ON ca.contact_rowid = m.ROWID
           JOIN lead l ON ca.contact_rowid = l.ROWID
           JOIN contact c ON ca.contact_rowid = c.ROWID
           WHERE ca.list_val IS NOT NULL AND ca.list_val != '' AND ca.contact_rowid IS NOT NULL""",
        conn,
    )

    if df_lists.empty:
        st.info("No hay listas para mostrar")
        return

    all_lists = sorted(df_lists["list_val"].unique().tolist())

    stats_cols = st.columns(3)
    stats_cols[0].metric("Listas unicas", f"{len(all_lists):,}")
    stats_cols[1].metric("Contactos con lista", f"{len(df_lists):,}")
    stats_cols[2].metric("Total contactos", f"{pd.read_sql_query('SELECT COUNT(*) as c FROM main', conn).iloc[0, 0]:,}")

    st.divider()

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        search_list = st.text_input("Buscar lista", key="search_list")
    with fcol2:
        page_size = st.selectbox("Filas", [25, 50, 100], index=1, key="page_list")

    filtered = df_lists.copy()
    if search_list:
        filtered = filtered[filtered["list_val"].str.contains(search_list, case=False, na=False)]

    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    if "page_list" not in st.session_state:
        st.session_state.page_list = 1
    page = st.session_state.page_list
    start = (page - 1) * page_size
    page_df = filtered.iloc[start:start + page_size]

    st.write(f"Mostrando {len(page_df)} de {len(filtered):,} contactos (Pagina {page}/{total_pages})")

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        if st.button("Anterior", key="prev_list") and page > 1:
            st.session_state.page_list -= 1
            st.rerun()
    with pcol2:
        if st.button("Siguiente", key="next_list") and page < total_pages:
            st.session_state.page_list += 1
            st.rerun()

    st.divider()

    show_df = page_df[["list_val", "primary_email", "title", "sender", "city", "country", "deliverability"]].copy()
    st.dataframe(show_df, width="stretch", hide_index=True)

    with st.expander("Ver top 10 listas por frecuencia"):
        top_lists = df_lists["list_val"].value_counts().head(10)
        st.dataframe(top_lists.reset_index().rename(columns={"list_val": "lista", "count": "frecuencia"}), hide_index=True)


def tab_dashboard(conn):
    st.subheader("Dashboard de Campanas")

    stats = get_dashboard_stats(conn)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total contactos", f"{stats['total_contacts']:,}")
    col2.metric("Campanas creadas", f"{stats['total_campaigns']:,}")
    col3.metric("Borradores generados", f"{stats['total_drafts']:,}")
    col4.metric("Asuntos unicos", f"{stats['total_subjects']:,}")

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Emails por sender")
        df_senders = get_sender_stats(conn)
        if not df_senders.empty:
            st.bar_chart(df_senders.set_index("sender"))
        else:
            st.info("No hay datos de senders")

    with col6:
        st.subheader("Campanas por mes")
        df_months = get_campaigns_by_month(conn)
        if not df_months.empty:
            st.bar_chart(df_months.set_index("month"))
        else:
            st.info("No hay campanas registradas")


def tab_campanas(conn):
    st.subheader("Campanas")

    df_campaigns = get_campaigns_list(conn)

    if df_campaigns.empty:
        st.info("No hay campanas creadas. Andi a la pestana Crear Campana.")
        return

    stats_cols = st.columns(3)
    stats_cols[0].metric("Campanas totales", f"{len(df_campaigns):,}")

    st.divider()

    for _, camp in df_campaigns.iterrows():
        campaign_rowid = int(camp["campaign_rowid"])
        recipient_count = get_campaign_recipient_count(conn, campaign_rowid)

        with st.expander(f"{camp['title'] or 'Sin titulo'} | {camp['subject'] or 'Sin asunto'} | {camp['date'] or ''}"):
            info_cols = st.columns(4)
            info_cols[0].metric("Asunto", camp["subject"] or "-")
            info_cols[1].metric("Sender", camp["sender"] or "-")
            info_cols[2].metric("Destinatarios", f"{recipient_count:,}")
            info_cols[3].metric("Tipo", camp["type"] or "-")

            if recipient_count > 0:
                df_recipients = get_campaign_recipients(conn, campaign_rowid)
                st.dataframe(df_recipients, width="stretch", hide_index=True)

                csv = df_recipients.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Descargar destinatarios CSV",
                    csv,
                    file_name=f"campaign_{campaign_rowid}_recipients.csv",
                    mime="text/csv",
                    key=f"dl_{campaign_rowid}",
                )


def tab_create_campaign(conn):
    st.subheader("Crear Campana")

    if "campaign_step" not in st.session_state:
        st.session_state.campaign_step = 1
    if "campaign_data" not in st.session_state:
        st.session_state.campaign_data = {}

    step = st.session_state.campaign_step

    st.write(f"Paso {step} de 4")
    progress = st.progress((step - 1) / 4)

    if step == 1:
        _step1_metadata(conn)
    elif step == 2:
        _step2_recipients(conn)
    elif step == 3:
        _step3_review(conn)
    elif step == 4:
        _step4_create(conn)


def _step1_metadata(conn):
    st.write("**Paso 1: Datos de la campana**")

    with st.form("campaign_metadata"):
        campaign_name = st.text_input("Nombre de campana *", placeholder="Ej: Campana España Julio 2026")
        subject = st.text_input("Asunto del email *", placeholder="Ej: Consultoria estrategica de marketing")
        body_html = st.text_area(
            "Mensaje (HTML) *",
            height=300,
            placeholder="<h2>Hola,</h2><p>Somos una agencia de marketing digital...</p>",
        )

        if body_html:
            with st.expander("Preview del mensaje"):
                st.components.v1.html(body_html, height=200, scrolling=True)

        submitted = st.form_submit_button("Siguiente: Seleccionar destinatarios")

        if submitted:
            if not campaign_name or not subject or not body_html:
                st.error("Todos los campos son obligatorios")
            else:
                st.session_state.campaign_data = {
                    "name": campaign_name,
                    "subject": subject,
                    "body": body_html,
                }
                st.session_state.campaign_step = 2
                st.rerun()


def _step2_recipients(conn):
    st.write("**Paso 2: Seleccionar destinatarios**")

    data = st.session_state.campaign_data
    st.info(f"Campana: **{data['name']}** | Asunto: **{data['subject']}**")

    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    with fcol1:
        search = st.text_input("Buscar email/titulo", key="camp_search")
    with fcol2:
        senders = pd.read_sql_query(
            'SELECT DISTINCT sender FROM contact WHERE sender IS NOT NULL AND sender != "" ORDER BY sender', conn
        )["sender"].tolist()
        sender_filter = st.selectbox("Filtrar por sender", [""] + senders, key="camp_sender")
    with fcol3:
        lists = get_list_values(conn)
        list_filter = st.selectbox("Filtrar por lista", [""] + lists, key="camp_list")
    with fcol4:
        sector_filter = st.text_input("Filtrar por sector", key="camp_sector")

    filters = {}
    if search:
        filters["search"] = search
    if sender_filter:
        filters["sender"] = sender_filter
    if list_filter:
        filters["list_val"] = list_filter
    if sector_filter:
        filters["sector"] = sector_filter

    df_contacts = get_contacts_for_selection(conn, filters if filters else None)

    if df_contacts.empty:
        st.warning("No se encontraron contactos con los filtros aplicados")
    else:
        grouped = group_by_sender(df_contacts)
        total_recipients = len(df_contacts)
        total_senders = len(grouped)

        stat_cols = st.columns(3)
        stat_cols[0].metric("Contactos encontrados", f"{total_recipients:,}")
        stat_cols[1].metric("Senders unicos", f"{total_senders:,}")
        batches_needed = sum(len(chunk_recipients(emails)) for emails in grouped.values())
        stat_cols[2].metric("Borradores a crear", f"{batches_needed:,}")

        st.dataframe(
            df_contacts[["primary_email", "sender", "title", "city", "country"]].head(100),
            width="stretch",
            hide_index=True,
        )

        if len(df_contacts) > 100:
            st.caption(f"Mostrando primeros 100 de {len(df_contacts)} contactos")

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("Volver al paso 1"):
            st.session_state.campaign_step = 1
            st.rerun()
    with bcol2:
        if st.button("Siguiente: Revisar envio", type="primary", disabled=df_contacts.empty):
            st.session_state.campaign_data["recipients_df"] = df_contacts
            st.session_state.campaign_data["grouped"] = grouped
            st.session_state.campaign_data["total_recipients"] = total_recipients
            st.session_state.campaign_data["total_batches"] = batches_needed
            st.session_state.campaign_step = 3
            st.rerun()


def _step3_review(conn):
    st.write("**Paso 3: Revisar envio**")

    data = st.session_state.campaign_data

    st.subheader("Resumen de la campana")
    info_cols = st.columns(2)
    info_cols[0].metric("Nombre", data["name"])
    info_cols[0].metric("Asunto", data["subject"])
    info_cols[1].metric("Destinatarios", f"{data['total_recipients']:,}")
    info_cols[1].metric("Borradores Gmail", f"{data['total_batches']:,}")

    st.divider()
    st.subheader("Borradores por sender")

    grouped = data["grouped"]
    for sender_email, recipients in grouped.items():
        chunks = chunk_recipients(recipients)
        with st.expander(f"{sender_email} | {len(recipients)} destinatarios | {len(chunks)} borradores"):
            for i, chunk in enumerate(chunks):
                st.write(f"  Batch {i+1}: {len(chunk)} emails")

    st.divider()

    with st.expander("Preview del mensaje HTML"):
        st.components.v1.html(data["body"], height=300, scrolling=True)

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("Volver al paso 2"):
            st.session_state.campaign_step = 2
            st.rerun()
    with bcol2:
        if st.button("Crear borradores en Gmail", type="primary"):
            st.session_state.campaign_step = 4
            st.rerun()


def _step4_create(conn):
    st.write("**Paso 4: Creando borradores**")

    data = st.session_state.campaign_data

    if "drafts_created" not in st.session_state:
        st.session_state.drafts_created = False

    if not st.session_state.drafts_created:
        progress_bar = st.progress(0)
        status_text = st.empty()

        results = create_full_campaign(
            grouped_recipients=data["grouped"],
            subject=data["subject"],
            body_html=data["body"],
        )

        total_batches = data["total_batches"]
        completed = 0
        all_results = []

        for sender_email, batch_results in results.items():
            for result in batch_results:
                completed += 1
                progress_bar.progress(completed / total_batches)
                status_text.text(f"Creando borrador {completed}/{total_batches}: {sender_email}")
                all_results.append({"sender": sender_email, **result})

        st.session_state.draft_results = all_results
        st.session_state.drafts_created = True
        st.rerun()
    else:
        results = st.session_state.draft_results

        ok_count = sum(1 for r in results if r["status"] == "ok")
        error_count = sum(1 for r in results if r["status"] == "error")

        res_cols = st.columns(2)
        res_cols[0].metric("Borradores creados", f"{ok_count:,}", delta="exito")
        if error_count > 0:
            res_cols[1].metric("Errores", f"{error_count:,}", delta="error")
        else:
            res_cols[1].metric("Errores", "0")

        st.divider()

        df_results = pd.DataFrame(results)
        st.dataframe(df_results, width="stretch", hide_index=True)

        st.divider()
        st.subheader("Registrar campana en la base de datos")

        st.info(
            "Los borradores se crearon en Gmail. Una vez que el remitente envie los emails "
            "desde Gmail, registre la campana aqui para guardar el historial en la DB."
        )

        if st.button("Registrar campana", type="primary"):
            recipients_df = data["recipients_df"]
            primary_sender = list(data["grouped"].keys())[0] if data["grouped"] else ""

            campaign_rowid = register_campaign(
                conn=conn,
                campaign_name=data["name"],
                subject=data["subject"],
                body_preview=data["body"][:200],
                sender=primary_sender,
                recipients_df=recipients_df,
            )

            st.success(f"Campana registrada con ID: {campaign_rowid}")
            st.session_state.campaign_step = 1
            st.session_state.campaign_data = {}
            st.session_state.drafts_created = False
            if "draft_results" in st.session_state:
                del st.session_state.draft_results
            st.rerun()


def main():
    st.title("Contacts DB")
    conn = get_connection()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Dashboard", "Contactos", "Crear Campana", "Campanas", "Asuntos", "Listas"]
    )

    with tab1:
        tab_dashboard(conn)
    with tab2:
        tab_contacts(conn)
    with tab3:
        tab_create_campaign(conn)
    with tab4:
        tab_campanas(conn)
    with tab5:
        tab_asuntos(conn)
    with tab6:
        tab_listas(conn)


if __name__ == "__main__":
    main()
