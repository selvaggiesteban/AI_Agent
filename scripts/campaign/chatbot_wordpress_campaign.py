import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_chatbot_wp_campaign(conventions=""):
    """
    Executes the 'Chatbot WordPress' campaign:
    1. Analyzes chatbot configuration goals.
    2. Generates a setup plan and optimization suggestions using AI.
    3. Sends the result via Gmail.
    """
    logger.info("Starting 'Chatbot WordPress' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("chatbot_wp", {})

        if not config:
            logger.error("Configuration for 'chatbot_wp' not found in campaign_config.json")
            return

        system_prompt = (
            f"You are a WordPress Automation Expert specializing in AI Chatbots. "
            f"Your goal is to provide technical setup plans and optimization strategies. "
            f"Apply these project conventions: {conventions}"
        )

        prompt = (
            f"Based on the following requirements: {config.get('requirements', 'General chatbot optimization')}, "
            f"generate a detailed implementation plan for a WordPress AI Chatbot. "
            f"Include tool recommendations, integration steps, and expected outcomes. "
            f"Return a JSON object with a 'body_html' key."
        )

        ai_result = llm.generate_structured(
            prompt=prompt,
            system_instruction=system_prompt,
            model="gemini"
        )

        message_html = ai_result.get("body_html", "Error generating chatbot plan.")

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "WordPress Chatbot Implementation Plan"),
            body_html=message_html
        )

        if success:
            logger.info("'Chatbot WordPress' campaign completed successfully.")
        else:
            logger.error("'Chatbot WordPress' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Chatbot WordPress' campaign: {e}")

if __name__ == "__main__":
    run_chatbot_wp_campaign()
