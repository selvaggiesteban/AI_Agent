import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_ai_email_marketing_campaign(conventions=""):
    """
    Executes the 'E-mail marketing con IA' campaign:
    1. Analyzes target audience and goals.
    2. Generates a sequence of high-converting emails.
    3. Sends the sequence plan via Gmail.
    """
    logger.info("Starting 'E-mail marketing con IA' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("email_marketing", {})

        if not config:
            logger.error("Configuration for 'email_marketing' not found.")
            return

        system_prompt = (
            f"You are an Email Marketing Strategist specializing in AI-driven personalization. "
            f"Your goal is to maximize open rates and conversions. "
            f"Apply these project conventions: {conventions}"
        )

        prompt = (
            f"Generate an email sequence for the following goal: {config.get('marketing_goal', 'Lead generation for IT services')}. "
            f"Target Audience: {config.get('audience', 'Business owners in Argentina')}. "
            f"Provide a 5-email sequence with subject lines and bodies. "
            f"Return a JSON object with a 'body_html' key."
        )

        ai_result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        message_html = ai_result.get("body_html", "Error generating email sequence.")

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "AI-Driven Email Marketing Sequence"),
            body_html=message_html
        )

        if success:
            logger.info("'E-mail marketing con IA' campaign completed successfully.")
        else:
            logger.error("'E-mail marketing con IA' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'E-mail marketing con IA' campaign: {e}")

if __name__ == "__main__":
    run_ai_email_marketing_campaign()
