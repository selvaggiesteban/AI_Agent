import csv
import json
import os
from datetime import datetime

# CSVs Directory
WORK_DIR = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\Trabajo"

# Output file
OUTPUT_FILE = os.path.join(WORK_DIR, "work_data.json")

def read_csv(filename):
    """Reads a CSV and returns a list of dictionaries"""
    filepath = os.path.join(WORK_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [WARN] File not found: {filename}")
        return []

    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean empty keys
            cleaned = {k.strip(): v.strip() if v else None for k, v in row.items() if k and k.strip()}
            if cleaned:
                rows.append(cleaned)
    return rows

def safe_int(value, default=0):
    """Converts a string to int, handling thousands separators"""
    if not value:
        return default
    # Remove dot thousands separators and convert
    cleaned = str(value).replace(".", "")
    try:
        return int(cleaned)
    except ValueError:
        return default

def parse_campaigns(rows):
    """Parses the campaigns CSV"""
    campaigns = []
    for row in rows:
        campaign = {
            "title": row.get("Title"),
            "geographic_coverage": row.get("Geographic Coverage"),
            "list": row.get("List"),
            "subject": row.get("Subject"),
            "date": row.get("Date"),
            "message": row.get("Message"),
            "status": row.get("Status"),
            "emails_sent": safe_int(row.get("Emails Sent")),
            "unique_contacts": safe_int(row.get("Unique Contacts")),
            "failures": safe_int(row.get("Failures")),
            "duration": row.get("Duration"),
            "accounts_used": safe_int(row.get("Accounts Used")),
            "enriched": row.get("Enriched"),
            "log_file": row.get("Log file")
        }
        campaigns.append(campaign)
    return campaigns

def parse_chat(rows):
    """Parses the chat CSV"""
    chats = []
    for row in rows:
        chat = {
            "id": row.get("ID"),
            "channel": row.get("Channel"),
            "list": row.get("List"),
            "message": row.get("Message"),
            "sender": row.get("Sender"),
            "recipient": row.get("Recipient"),
            "reply": row.get("Reply"),
            "datetime": row.get("Date / Time"),
            "status": row.get("Status")
        }
        chats.append(chat)
    return chats

def safe_float(value, default=0.0):
    """Converts a string to float, handling thousands separators"""
    if not value:
        return default
    # Remove dot thousands separators and convert
    cleaned = str(value).replace(".", "")
    try:
        return float(cleaned) / 1000 if len(cleaned) > 6 else float(cleaned)
    except ValueError:
        return default

def parse_coverage(rows):
    """Parses the geographic coverage CSV"""
    coverages = []
    for row in rows:
        coverage = {
            "order": safe_int(row.get("order")),
            "id": row.get("id"),
            "desc": row.get("desc"),
            "north": safe_float(row.get("north")),
            "west": safe_float(row.get("west")),
            "south": safe_float(row.get("south")),
            "east": safe_float(row.get("east")),
            "cells": safe_int(row.get("cells")),
            "queries": row.get("queries"),
            "density": safe_int(row.get("density"))
        }
        coverages.append(coverage)
    return coverages

def parse_time_control(rows):
    """Parses the time control CSV"""
    schedules = []
    for row in rows:
        schedule = {
            "price": int(row.get("Price", 0) or 0),
            "service": row.get("Service"),
            "date": row.get("Date"),
            "hours": {}
        }
        hours_cols = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        for h in hours_cols:
            schedule["hours"][h] = row.get(h, "FALSE") == "TRUE"
        schedules.append(schedule)
    return schedules

def parse_emails(rows):
    """Parses the emails CSV"""
    emails = []
    for row in rows:
        email = {
            "provider": row.get("Provider"),
            "user": row.get("User"),
            "password": row.get("Password"),
            "app_password": row.get("App Password"),
            "oauth_client_id": row.get("OAuth Client ID")
        }
        emails.append(email)
    return emails

def parse_ai(rows):
    """Parses the AI CSV"""
    ai_data = []
    for row in rows:
        agent_full = row.get("AI_Agent", "")
        # Separate agent and email
        parts = agent_full.split(" ", 1)
        agent = parts[0] if parts else agent_full
        email = parts[1] if len(parts) > 1 else ""

        weeks = {}
        for k, v in row.items():
            if k and k.startswith("Week"):
                weeks[k] = v == "TRUE"

        ai_entry = {
            "agent": agent,
            "email": email,
            "weeks": weeks
        }
        ai_data.append(ai_entry)
    return ai_data

def parse_keywords(rows):
    """Parses the keywords CSV"""
    return [row.get("keyword", list(row.values())[0] if row else "") for row in rows if row]

def parse_objectives(rows):
    """Parses the objectives CSV"""
    objectives = []
    for row in rows:
        objective = {
            "month_year": row.get("Month / Year"),
            "working_days": int(row.get("Working Days", 0) or 0),
            "cpi": row.get("CPI"),
            "price_per_session": int(row.get("Price per Session", 0) or 0),
            "available_sessions": int(row.get("Available Sessions", 0) or 0),
            "target_sold_sessions": int(row.get("Target Sold Sessions", 0) or 0),
            "earnings": row.get("Earnings")
        }
        objectives.append(objective)
    return objectives

def parse_web_pages(rows):
    """Parses the web pages CSV"""
    pages = []
    for row in rows:
        page = {
            "site": row.get("Site"),
            "keyword": row.get("Keyword"),
            "geographic_coverage": row.get("Geographic Coverage"),
            "campaign": row.get("Campaign"),
            "url_es": row.get("URL_ES"),
            "url_en": row.get("URL_EN"),
            "links_sent": row.get("Links Sent"),
            "target_sold_sessions": row.get("Target Sold Sessions"),
            "datetime": row.get("Date / Time")
        }
        pages.append(page)
    return pages

def parse_scrap(rows):
    """Parses the scraping CSV"""
    scraps = []
    for row in rows:
        scrap = {
            "title": row.get("Title"),
            "geographic_coverage": row.get("Geographic Coverage"),
            "keywords": row.get("Keywords"),
            "date": row.get("Date"),
            "status": row.get("Status"),
            "rows": int(row.get("Rows", 0) or 0),
            "unique_emails": int(row.get("Unique Emails", 0) or 0),
            "location": row.get("Location"),
            "duration": row.get("Duration"),
            "log_file": row.get("Log File")
        }
        scraps.append(scrap)
    return scraps

def main():
    print("=" * 60)
    print("CSV -> JSON CONVERTER")
    print("=" * 60)

    # Read all CSVs
    print("\n[1/10] Reading WORK - CAMPAIGNS.csv...")
    campaigns_raw = read_csv("WORK - CAMPAIGNS.csv")
    print(f"  -> {len(campaigns_raw)} rows")

    print("[2/10] Reading WORK - CHAT.csv...")
    chat_raw = read_csv("WORK - CHAT.csv")
    print(f"  -> {len(chat_raw)} rows")

    print("[3/10] Reading WORK - GEOGRAPHIC COVERAGE.csv...")
    coverage_raw = read_csv("WORK - GEOGRAPHIC COVERAGE.csv")
    print(f"  -> {len(coverage_raw)} rows")

    print("[4/10] Reading WORK - TIME CONTROL.csv...")
    schedule_raw = read_csv("WORK - TIME CONTROL.csv")
    print(f"  -> {len(schedule_raw)} rows")

    print("[5/10] Reading WORK - E-MAILS.csv...")
    emails_raw = read_csv("WORK - E-MAILS.csv")
    print(f"  -> {len(emails_raw)} rows")

    print("[6/10] Reading WORK - AI.csv...")
    ai_raw = read_csv("WORK - AI.csv")
    print(f"  -> {len(ai_raw)} rows")

    print("[7/10] Reading WORK - KEYWORDS.csv...")
    keywords_raw = read_csv("WORK - KEYWORDS.csv")
    print(f"  -> {len(keywords_raw)} rows")

    print("[8/10] Reading WORK - OBJECTIVES.csv...")
    objectives_raw = read_csv("WORK - OBJECTIVES.csv")
    print(f"  -> {len(objectives_raw)} rows")

    print("[9/10] Reading WORK - WEB PAGES.csv...")
    pages_raw = read_csv("WORK - WEB PAGES.csv")
    print(f"  -> {len(pages_raw)} rows")

    print("[10/10] Reading WORK - SCRAP.csv...")
    scrap_raw = read_csv("WORK - SCRAP.csv")
    print(f"  -> {len(scrap_raw)} rows")

    # Parse each section
    print("\nParsing data...")
    data = {
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "source": "WORK - 10 CSVs",
            "total_campaigns": len(campaigns_raw),
            "total_chats": len(chat_raw),
            "total_coverages": len(coverage_raw),
            "total_schedules": len(schedule_raw),
            "total_account_emails": len(emails_raw),
            "total_ai_agents": len(ai_raw),
            "total_keywords": len(keywords_raw),
            "total_objectives": len(objectives_raw),
            "total_web_pages": len(pages_raw),
            "total_scraps": len(scrap_raw)
        },
        "campaigns": parse_campaigns(campaigns_raw),
        "chat": parse_chat(chat_raw),
        "geographic_coverage": parse_coverage(coverage_raw),
        "time_control": parse_time_control(schedule_raw),
        "account_emails": parse_emails(emails_raw),
        "ai_agents": parse_ai(ai_raw),
        "keywords": parse_keywords(keywords_raw),
        "objectives": parse_objectives(objectives_raw),
        "web_pages": parse_web_pages(pages_raw),
        "scraping": parse_scrap(scrap_raw)
    }

    # Save JSON
    print(f"\nSaving JSON to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Summary
    file_size = os.path.getsize(OUTPUT_FILE)
    print("\n" + "=" * 60)
    print("COMPLETED")
    print("=" * 60)
    print(f"File: {OUTPUT_FILE}")
    print(f"Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"\nSections:")
    print(f"  - campaigns:            {len(data['campaigns'])} records")
    print(f"  - chat:                {len(data['chat'])} records")
    print(f"  - geographic_coverage:  {len(data['geographic_coverage'])} records")
    print(f"  - time_control:        {len(data['time_control'])} records")
    print(f"  - account_emails:      {len(data['account_emails'])} records")
    print(f"  - ai_agents:           {len(data['ai_agents'])} records")
    print(f"  - keywords:            {len(data['keywords'])} records")
    print(f"  - objectives:           {len(data['objectives'])} records")
    print(f"  - web_pages:           {len(data['web_pages'])} records")
    print(f"  - scraping:            {len(data['scraping'])} records")

if __name__ == "__main__":
    main()
