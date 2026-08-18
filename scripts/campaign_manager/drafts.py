import imaplib
import smtplib
import json
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from datetime import datetime


DB_PATH = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\data\inputs\contacts.db"
ENV_PATH = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\.env"
IMAP_FOLDER = "[Gmail]/Borradores"
BATCH_SIZE = 100


def load_gmail_accounts():
    """Load Gmail accounts from .env (excluding Hostinger)."""
    accounts = []
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("EMAIL_ACCOUNTS="):
                raw = line.split("=", 1)[1].strip().strip("'\"")
                all_accounts = json.loads(raw)
                for acc in all_accounts:
                    if "gmail.com" in acc.get("imap_server", ""):
                        accounts.append({
                            "email": acc["email"],
                            "password": acc["password"],
                            "imap_server": acc["imap_server"],
                        })
                break
    return accounts


def get_account_for_sender(sender_email, accounts):
    """Get the IMAP credentials for a specific sender email."""
    for acc in accounts:
        if acc["email"] == sender_email:
            return acc
    return None


def build_draft_message(sender_email, to_addr, subject, body_html, bcc_list):
    """Build a MIME message for a Gmail draft."""
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    if bcc_list:
        msg["Bcc"] = ", ".join(bcc_list)
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    return msg


def create_gmail_draft(sender_email, sender_password, subject, body_html, bcc_list):
    """
    Create a draft in Gmail via IMAP APPEND.

    Args:
        sender_email: Sender email address.
        sender_password: Gmail App Password.
        subject: Email subject.
        body_html: HTML body content.
        bcc_list: List of up to 100 recipient emails.

    Returns:
        dict with status, message, batch_size.
    """
    if not bcc_list:
        return {"status": "error", "message": "No recipients", "batch_size": 0}

    msg = build_draft_message(sender_email, sender_email, subject, body_html, bcc_list)
    raw = msg.as_string()

    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(sender_email, sender_password)
        status, data = imap.append(IMAP_FOLDER, "\\Draft", None, raw.encode("utf-8"))
        imap.logout()

        if status == "OK":
            return {"status": "ok", "message": f"Draft created for {sender_email}", "batch_size": len(bcc_list)}
        else:
            return {"status": "error", "message": f"IMAP APPEND failed: {data}", "batch_size": len(bcc_list)}
    except Exception as e:
        return {"status": "error", "message": str(e), "batch_size": len(bcc_list)}


def chunk_recipients(recipients, chunk_size=BATCH_SIZE):
    """Split a list of emails into chunks of chunk_size."""
    return [recipients[i:i + chunk_size] for i in range(0, len(recipients), chunk_size)]


def group_by_sender(df_contacts):
    """
    Group contacts by their assigned sender.

    Args:
        df_contacts: DataFrame with columns 'primary_email' and 'sender'.

    Returns:
        dict: {sender_email: [email1, email2, ...]}
    """
    grouped = {}
    for sender, group in df_contacts.groupby("sender"):
        if sender and str(sender).strip():
            emails = group["primary_email"].dropna().tolist()
            emails = [e for e in emails if e and str(e).strip()]
            if emails:
                grouped[str(sender).strip()] = emails
    return grouped


def create_campaign_drafts(sender_email, sender_password, subject, body_html, recipients):
    """
    Create all drafts for a campaign, chunking recipients into batches of 100.

    Args:
        sender_email: Sender email.
        sender_password: App Password.
        subject: Campaign subject.
        body_html: Campaign body.
        recipients: List of recipient emails.

    Returns:
        list of dicts with draft results.
    """
    chunks = chunk_recipients(recipients)
    results = []
    for i, chunk in enumerate(chunks):
        result = create_gmail_draft(sender_email, sender_password, subject, body_html, chunk)
        result["batch_number"] = i + 1
        result["total_batches"] = len(chunks)
        results.append(result)
    return results


def create_full_campaign(grouped_recipients, subject, body_html):
    """
    Create all drafts for a full campaign (all senders, all batches).

    Args:
        grouped_recipients: dict {sender_email: [recipients]}
        subject: Campaign subject.
        body_html: Campaign body.

    Returns:
        dict: {sender_email: [draft_results]}
    """
    accounts = load_gmail_accounts()
    all_results = {}

    for sender_email, recipients in grouped_recipients.items():
        account = get_account_for_sender(sender_email, accounts)
        if not account:
            all_results[sender_email] = [{
                "status": "error",
                "message": f"Account not found for {sender_email}",
                "batch_size": len(recipients),
            }]
            continue

        results = create_campaign_drafts(
            sender_email=sender_email,
            sender_password=account["password"],
            subject=subject,
            body_html=body_html,
            recipients=recipients,
        )
        all_results[sender_email] = results

    return all_results


if __name__ == "__main__":
    accounts = load_gmail_accounts()
    print(f"Gmail accounts loaded: {len(accounts)}")
    for a in accounts:
        print(f"  - {a['email']}")
