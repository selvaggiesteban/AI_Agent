import sqlite3
import pandas as pd
from datetime import datetime


DB_PATH = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\data\inputs\contacts.db"


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def get_dashboard_stats(conn):
    """Get stats for the Dashboard tab."""
    stats = {}
    stats["total_contacts"] = conn.execute("SELECT COUNT(*) FROM main").fetchone()[0]
    stats["total_campaigns"] = conn.execute(
        "SELECT COUNT(*) FROM campaign WHERE campaign_id IS NULL AND contact_rowid IS NULL"
    ).fetchone()[0]
    stats["total_drafts"] = conn.execute(
        "SELECT COUNT(*) FROM campaign WHERE campaign_id IS NOT NULL"
    ).fetchone()[0]
    stats["total_subjects"] = conn.execute(
        "SELECT COUNT(DISTINCT subject) FROM campaign WHERE subject IS NOT NULL AND subject != ''"
    ).fetchone()[0]
    stats["senders_used"] = conn.execute(
        "SELECT COUNT(DISTINCT sender) FROM campaign WHERE sender IS NOT NULL AND sender != ''"
    ).fetchone()[0]
    return stats


def get_campaigns_list(conn):
    """Get list of campaigns (metadata rows where campaign_id IS NULL)."""
    query = """
        SELECT ROWID as campaign_rowid, title, subject, sender, date, type, list_val
        FROM campaign
        WHERE campaign_id IS NULL AND contact_rowid IS NULL
        ORDER BY date DESC
    """
    return pd.read_sql_query(query, conn)


def get_campaign_recipients(conn, campaign_rowid):
    """Get all recipients for a specific campaign."""
    query = """
        SELECT c.sender, l.primary_email, m.title, m.city, m.country, m.sector
        FROM campaign ca
        JOIN main m ON ca.contact_rowid = m.ROWID
        JOIN lead l ON ca.contact_rowid = l.ROWID
        JOIN contact c ON ca.contact_rowid = c.ROWID
        WHERE ca.campaign_id = ?
    """
    return pd.read_sql_query(query, conn, params=(campaign_rowid,))


def get_campaign_recipient_count(conn, campaign_rowid):
    """Count recipients for a campaign."""
    result = conn.execute(
        "SELECT COUNT(*) FROM campaign WHERE campaign_id = ?", (campaign_rowid,)
    ).fetchone()
    return result[0] if result else 0


def get_contacts_for_selection(conn, filters=None):
    """Get contacts for campaign creation with optional filters."""
    query = """
        SELECT m.ROWID as rowid, m.title, m.sector, m.city, m.country,
               l.primary_email, c.sender
        FROM main m
        JOIN lead l ON m.ROWID = l.ROWID
        JOIN contact c ON m.ROWID = c.ROWID
        WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
          AND c.sender IS NOT NULL AND c.sender != ''
    """
    params = []

    if filters:
        if filters.get("sender"):
            query += " AND c.sender = ?"
            params.append(filters["sender"])
        if filters.get("sector"):
            query += " AND m.sector LIKE ?"
            params.append(f"%{filters['sector']}%")
        if filters.get("city"):
            query += " AND m.city LIKE ?"
            params.append(f"%{filters['city']}%")
        if filters.get("country"):
            query += " AND m.country LIKE ?"
            params.append(f"%{filters['country']}%")
        if filters.get("list_val"):
            query += " AND m.ROWID IN (SELECT contact_rowid FROM campaign WHERE list_val = ? AND contact_rowid IS NOT NULL)"
            params.append(filters["list_val"])
        if filters.get("search"):
            query += " AND (l.primary_email LIKE ? OR m.title LIKE ?)"
            s = f"%{filters['search']}%"
            params.extend([s, s])

    return pd.read_sql_query(query, conn, params=params)


def get_list_values(conn):
    """Get distinct list values from campaign table."""
    query = "SELECT DISTINCT list_val FROM campaign WHERE list_val IS NOT NULL AND list_val != '' ORDER BY list_val"
    df = pd.read_sql_query(query, conn)
    return df["list_val"].tolist()


def register_campaign(conn, campaign_name, subject, body_preview, sender, recipients_df):
    """
    Register a campaign in the database.

    Creates:
    - 1 metadata row in campaign (contact_rowid=NULL, campaign_id=NULL)
    - N recipient rows in campaign (campaign_id=metadata_rowid)

    Args:
        conn: SQLite connection.
        campaign_name: Name/title of the campaign.
        subject: Email subject.
        body_preview: First 200 chars of body for preview.
        sender: Primary sender (for metadata row).
        recipients_df: DataFrame with columns [rowid, primary_email, sender].

    Returns:
        int: campaign_rowid of the created campaign.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.execute(
        """INSERT INTO campaign (contact_rowid, title, list_val, subject, sender, date, type, campaign_id)
           VALUES (NULL, ?, NULL, ?, ?, ?, 'email', NULL)""",
        (campaign_name, subject, sender, now),
    )
    campaign_rowid = cursor.lastrowid

    for _, row in recipients_df.iterrows():
        contact_rowid = int(row["rowid"])
        recipient_sender = row.get("sender", sender)
        conn.execute(
            """INSERT INTO campaign (contact_rowid, title, list_val, subject, sender, date, type, campaign_id)
               VALUES (?, ?, NULL, ?, ?, ?, 'email', ?)""",
            (contact_rowid, campaign_name, subject, recipient_sender, now, campaign_rowid),
        )

    conn.commit()
    return campaign_rowid


def get_sender_stats(conn):
    """Get email count per sender for dashboard."""
    query = """
        SELECT c.sender, COUNT(*) as count
        FROM contact c
        WHERE c.sender IS NOT NULL AND c.sender != ''
        GROUP BY c.sender
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


def get_campaigns_by_month(conn):
    """Get campaign count by month for dashboard chart."""
    query = """
        SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
        FROM campaign
        WHERE campaign_id IS NULL AND contact_rowid IS NULL AND date IS NOT NULL
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """
    return pd.read_sql_query(query, conn)
