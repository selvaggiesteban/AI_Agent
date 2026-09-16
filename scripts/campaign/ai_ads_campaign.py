import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_ai_ads_campaign(conventions=""):
    """
    Executes the 'Creador de anuncios con IA' campaign:
    1. Takes product/service descriptions.
    2. Generates high-converting ad copies for Facebook, Instagram, and Google Ads.
    3. Sends the copies via Gmail.
    """
    logger.info("Starting 'Creador de anuncios con IA' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("ai_ads", {})

        if not config:
            logger.error("Configuration for 'ai_ads' not found.")
            return

        system_prompt = (
            f"You are a Direct Response Copywriter specializing in high-conversion AI ads. "
            f"Your goal is to create compelling hooks and strong CTAs. "
            f"Apply these project conventions: {conventions}"
        )

        prompt = (
            f"Generate ad copies for the following product/service: {config.get('product_description', 'Professional IT Services')}. "
            f"Provide 3 variants for Facebook, 3 for Instagram (Story/Feed), and 2 for Google Ads. "
            f"Return a JSON object with a 'body_html' key containing a formatted table of the copies."
        )

        ai_result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        message_html = ai_result.get("body_html", "Error generating ad copies.")

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "AI Generated Ad Copies"),
            body_html=message_html
        )

        if success:
            logger.info("'Creador de anuncios con IA' campaign completed successfully.")
        else:
            logger.error("'Creador de anuncios con IA' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Creador de anuncios con IA' campaign: {e}")

if __name__ == "__main__":
    run_ai_ads_campaign()
