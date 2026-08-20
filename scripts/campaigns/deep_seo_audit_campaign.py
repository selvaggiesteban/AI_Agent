import os
import json
from core.integrations import GoogleIntegration, GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def perform_deep_audit(google, domain, conventions=""):
    """
    Performs a comprehensive technical SEO audit.
    """
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    gsc_data = google.get_gsc_metrics(f"sc-domain:{domain}", start_date, end_date)

    system_prompt = (
        f"You are a Senior Technical SEO Auditor. Your goal is to provide a deep-dive technical analysis. "
        f"Be critical, detailed, and prioritize findings by impact. "
        f"Apply these project conventions: {conventions}"
    )

    prompt = (
        f"Perform a deep technical SEO audit for {domain}. "
        f"Metrics for last 90 days: {gsc_data}. "
        f"Analyze potential issues with Core Web Vitals, Indexability, and Semantic Structure. "
        f"Provide a structured report with 'Issue', 'Impact', and 'Fix'. "
        f"Return a JSON object with a 'body_html' key."
    )

    try:
        result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        return result.get("body_html", "Deep audit failed.")
    except Exception as e:
        logger.error(f"Deep audit AI failed for {domain}: {e}")
        return "Deep audit unavailable."

def run_deep_seo_audit_campaign(conventions=""):
    """
    Executes the 'Deep Auditoría SEO' campaign.
    """
    logger.info("Starting 'Deep Auditoría SEO' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("deep_seo", {})

        if not config:
            logger.error("Configuration for 'deep_seo' not found.")
            return

        google = GoogleIntegration(os.environ.get("GOOGLE_CREDENTIALS_PATH"))
        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

        reports = []
        for domain in config.get("domains", []):
            logger.info(f"Deep auditing {domain}...")
            report = perform_deep_audit(google, domain, conventions)
            reports.append(f"<h2>Audit for {domain}</h2>{report}")

        final_body = "<br><hr><br>".join(reports)
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "Deep Technical SEO Audit Report"),
            body_html=final_body
        )

        if success:
            logger.info("'Deep Auditoría SEO' campaign completed successfully.")
        else:
            logger.error("'Deep Auditoría SEO' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Deep Auditoría SEO' campaign: {e}")

if __name__ == "__main__":
    run_deep_seo_audit_campaign()
