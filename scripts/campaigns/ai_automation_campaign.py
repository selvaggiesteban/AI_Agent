import os
import json
from core.integrations import GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_ai_automation_campaign(conventions=""):
    """
    Executes the 'Automatizaciones con IA' campaign:
    1. Identifies manual workflows.
    2. Proposes AI-driven automation paths.
    3. Sends the automation roadmap via Gmail.
    """
    logger.info("Starting 'Automatizaciones con IA' campaign...")
    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f).get("ai_automation", {})

        if not config:
            logger.error("Configuration for 'ai_automation' not found.")
            return

        system_prompt = (
            f"You are an AI Automation Architect. Your goal is to replace manual toil with intelligent workflows. "
            f"Apply these project conventions: {conventions}"
        )

        prompt = (
            f"Analyze the following manual workflows: {config.get('manual_workflows', 'General business operations')}. "
            f"Propose a set of AI automations using LLMs, RPA (Playwright), and API integrations. "
            f"Return a JSON object with a 'body_html' key containing a structured roadmap."
        )

        ai_result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        message_html = ai_result.get("body_html", "Error generating automation roadmap.")

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config.get("email_subject", "AI Automation Roadmap"),
            body_html=message_html
        )

        if success:
            logger.info("'Automatizaciones con IA' campaign completed successfully.")
        else:
            logger.error("'Automatizaciones con IA' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Automatizaciones con IA' campaign: {e}")

if __name__ == "__main__":
    run_ai_automation_campaign()
