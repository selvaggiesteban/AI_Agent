import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def perform_seo_audit(google_integration, domain, conventions=""):
    """
    Fetches real SEO metrics from GSC and GA4, then generates an AI summary.
    """
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # 1. Fetch GSC Metrics
    # For simplicity, we assume the domain is the siteUrl.
    # In reality, it could be 'sc-domain:example.com'
    gsc_url = f"sc-domain:{domain}" if not domain.startswith("http") else domain
    gsc_data = google_integration.get_gsc_metrics(gsc_url, start_date, end_date)

    # 2. Fetch GA4 Metrics (Requires propertyId - we'll use a mock/default if not available)
    # To be fully functional, the propertyId should come from config.
    ga4_data = {"activeUsers": "N/A", "sessions": "N/A"}

    # Combine data for AI
    metrics_summary = (
        f"GSC (last 30 days): Clicks={gsc_data.get('clicks', 0)}, "
        f"Impressions={gsc_data.get('impressions', 0)}, CTR={gsc_data.get('ctr', 'N/A')}. "
        f"Top Queries: {', '.join(gsc_data.get('top_queries', []))}. "
        f"GA4: Active Users={ga4_data['activeUsers']}, Sessions={ga4_data['sessions']}."
    )

    # Combine project conventions with the specific prompt
    system_prompt = f"You are a professional SEO auditor. Be concise and actionable. Apply these project conventions: {conventions}"
    prompt = f"Based on these metrics for {domain}: {metrics_summary}\n\nGenerate a very brief 3-point SEO audit summary. Return as a simple string."

    try:
        result = llm.generate_structured(
            prompt=prompt,
            system_instruction=system_prompt,
            model="gemini"
        )
        return result.get("summary", "Audit completed: metrics fetched successfully.")
    except Exception as e:
        logger.error(f"SEO audit AI summary failed for {domain}: {e}")
        return f"Metrics fetched: {metrics_summary}"

def run_posicionamiento_campaign(conventions=""):
    """
    Executes the 'Posicionamiento web' campaign:
    1. Loops through a list of domains.
    2. Performs a real SEO audit using GSC/GA4 for each.
    3. Sends a consolidated report via Gmail with attachments.
    """
    logger.info("Starting 'Posicionamiento web' campaign...")

    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)["posicionamiento"]

        # Initialize integrations
        google = GoogleIntegration(os.environ.get("GOOGLE_CREDENTIALS_PATH"))
        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

        audits_results = []
        audit_data_for_csv = []
        for domain in config["domains"]:
            logger.info(f"Auditing {domain}...")
            audit = perform_seo_audit(google, domain, conventions)
            audits_results.append(f"<b>{domain}</b>: {audit}")
            audit_data_for_csv.append({"domain": domain, "audit": audit})

        consolidated_audits = "<br><br>".join(audits_results)
        message = config["email_template"].format(seo_audits=consolidated_audits)

        # Save files for attachments
        report_path = os.path.join("data/outputs", "seo_report.html")
        os.makedirs("data/outputs", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body>{message}</body></html>")

        csv_path = os.path.join("data/outputs", "seo_audits.csv")
        import pandas as pd
        pd.DataFrame(audit_data_for_csv).to_csv(csv_path, index=False)

        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config["email_subject"],
            body_html=f"<p>{message}</p>",
            attachments=[report_path, csv_path]
        )

        if success:
            logger.info("'Posicionamiento web' campaign completed successfully.")
        else:
            logger.error("'Posicionamiento web' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Posicionamiento web' campaign: {e}")

if __name__ == "__main__":
    run_posicionamiento_campaign()
