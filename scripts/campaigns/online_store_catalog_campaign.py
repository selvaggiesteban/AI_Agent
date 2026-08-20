import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_store_catalog_campaign(conventions=""):
    """
    Executes the 'Catálogo de Tienda Online' campaign:
    1. Analyzes product lists.
    2. Generates optimized product descriptions and categories.
    3. Sends the catalog plan via Gmail.
    """
    logger.info("Starting 'Catálogo de Tienda Online' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("store_catalog", {})

        if not config:
            logger.error("Configuration for 'store_catalog' not found.")
            return

        system_prompt = (
            f"You are an E-commerce Strategist and Catalog Expert. "
            f"Your goal is to optimize product descriptions for SEO and conversion. "
            f"Apply these project conventions: {conventions}"
        )

        prompt = (
            f"Optimize the following product list for an online store: {config.get('product_list', 'General IT hardware')}. "
            f"For each product, provide an optimized title, a 2-sentence description, and suggested categories. "
            f"Return a JSON object with a 'body_html' key containing a formatted table."
        )

        ai_result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        message_html = ai_result.get("body_html", "Error generating catalog optimization.")

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "Online Store Catalog Optimization"),
            body_html=message_html
        )

        if success:
            logger.info("'Catálogo de Tienda Online' campaign completed successfully.")
        else:
            logger.error("'Catálogo de Tienda Online' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Catálogo de Tienda Online' campaign: {e}")

if __name__ == "__main__":
    run_store_catalog_campaign()
