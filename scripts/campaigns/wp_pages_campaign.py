import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_wp_pages_campaign(conventions=""):
    """
    Executes the 'Páginas de WordPress' campaign:
    1. Analyzes existing WP page structures.
    2. Suggests optimizations for conversion and UX.
    3. Sends results via Gmail.
    """
    logger.info("Starting 'Páginas de WordPress' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("wp_pages", {})

        if not config:
            logger.error("Configuration for 'wp_pages' not found.")
            return

        system_prompt = (
            f"You are a UX/UI Expert specializing in WordPress landing pages. "
            f"Your goal is to optimize conversion rates (CRO) and user experience. "
            f"Apply these project conventions: {conventions}"
        )

        prompt = (
            f"Analyze the following pages: {config.get('pages', 'General site structure')}. "
            f"Provide specific recommendations for improving the Hero section, CTA placement, "
            f"and mobile responsiveness. "
            f"Return a JSON object with a 'body_html' key."
        )

        ai_result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        message_html = ai_result.get("body_html", "Error generating WP page optimization report.")

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "WordPress Page Optimization Report"),
            body_html=message_html
        )

        if success:
            logger.info("'Páginas de WordPress' campaign completed successfully.")
        else:
            logger.error("'Páginas de WordPress' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Páginas de WordPress' campaign: {e}")

if __name__ == "__main__":
    run_wp_pages_campaign()
