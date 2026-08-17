import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def perform_seo_audit(domain, conventions=""):
    """
    Simulates an SEO audit for a domain.
    In a real scenario, this would call GSC/GA4 APIs.
    """
    # Combine project conventions with the specific prompt
    system_prompt = f"You are a professional SEO auditor. Be concise. Apply these project conventions: {conventions}"
    prompt = f"Generate a very brief 3-point SEO audit summary for the website {domain}. Focus on technical SEO, content, and backlinks. Return as a simple string."

    try:
        # Use the LLMRouter to get a summary
        result = llm.generate_structured(
            prompt=prompt,
            system_instruction=system_prompt,
            model="gemini"
        )
        return result.get("summary", "Audit completed: check GSC for details.")
    except Exception as e:
        logger.error(f"SEO audit failed for {domain}: {e}")
        return "Audit unavailable."

def run_posicionamiento_campaign(conventions=""):
    """
    Executes the 'Posicionamiento web' campaign:
    1. Loops through a list of domains.
    2. Performs a brief SEO audit for each.
    3. Sends a consolidated report via Gmail.
    """
    logger.info("Starting 'Posicionamiento web' campaign...")

    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)["posicionamiento"]

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

        audits_results = []
        for domain in config["domains"]:
            logger.info(f"Auditing {domain}...")
            audit = perform_seo_audit(domain, conventions)
            audits_results.append(f"<b>{domain}</b>: {audit}")

        consolidated_audits = "<br><br>".join(audits_results)
        message = config["email_template"].format(seo_audits=consolidated_audits)

        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config["email_subject"],
            body_html=f"<p>{message}</p>"
        )

        if success:
            logger.info("'Posicionamiento web' campaign completed successfully.")
        else:
            logger.error("'Posicionamiento web' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Posicionamiento web' campaign: {e}")

if __name__ == "__main__":
    run_posicionamiento_campaign()
