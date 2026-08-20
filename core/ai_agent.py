import os
import sys
import time
import threading
from datetime import datetime
from core.logger import logger
from core.integrations import TelegramIntegration
from scripts.campaigns.trabajo_campaign import run_trabajo_campaign
from scripts.campaigns.posicionamiento_campaign import run_posicionamiento_campaign
from scripts.campaigns.contable_campaign import run_contable_campaign
from scripts.campaigns.chatbot_wordpress_campaign import run_chatbot_wp_campaign
from scripts.campaigns.deep_seo_audit_campaign import run_deep_seo_audit_campaign
from scripts.campaigns.wp_pages_campaign import run_wp_pages_campaign
from scripts.campaigns.ai_ads_campaign import run_ai_ads_campaign
from scripts.campaigns.online_store_catalog_campaign import run_store_catalog_campaign
from scripts.campaigns.ai_automation_campaign import run_ai_automation_campaign
from scripts.campaigns.ai_email_marketing_campaign import run_ai_email_marketing_campaign
from core.ai_engine import llm

def load_conventions():
    """
    Loads conventions and rules from project documentation files.
    """
    conventions = []
    files = [
        "AGENTS.md",
        "ENRICH_RULES.md",
        "ESTEBAN.md"
    ]

    for file_name in files:
        path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    conventions.append(f"--- {file_name} ---\\n{content}")
            except Exception as e:
                logger.error(f"Could not read convention file {file_name}: {e}")

    return "\\n\\n".join(conventions)

def decode_instruction(text, conventions):
    """
    Uses the AI engine to decode a natural language instruction from Telegram
    into a specific agent action.
    """
    logger.info(f"Decoding instruction: {text}")

    system_prompt = (
        "You are the Instruction Decoder for Esteban Selvaggi's AI Agent. "
        "Your goal is to map a natural language instruction to one of the following actions: "
        "1. RUN_TRABAJO: Run the 'Trabajo' campaign report. "
        "2. RUN_POSICIONAMIENTO: Run the 'Posicionamiento web' SEO audits. "
        "3. RUN_CONTABLE: Run the 'Ejercicio contable 2026' report. "
        "4. RUN_CHATBOT_WP: Run the 'Chatbot WordPress' implementation plan. "
        "5. RUN_DEEP_SEO: Run the 'Deep Auditoría SEO' technical report. "
        "6. RUN_WP_PAGES: Run the 'Páginas de WordPress' optimization report. "
        "7. RUN_AI_ADS: Run the 'Creador de anuncios con IA' generator. "
        "8. RUN_STORE_CATALOG: Run the 'Catálogo de Tienda Online' optimizer. "
        "9. RUN_AI_AUTOMATION: Run the 'Automatizaciones con IA' roadmap. "
        "10. RUN_EMAIL_MARKETING: Run the 'E-mail marketing con IA' sequence. "
        "11. RUN_ALL: Run all campaigns. "
        "12. UNKNOWN: The instruction is unclear. "
        f"\\n\\nProject Conventions:\\n{conventions}"
    )

    prompt = f"Instruction: {text}\\n\\nReturn a JSON object with the key 'action' and the value as one of the listed action keys."

    try:
        result = llm.generate_structured(
            prompt=prompt,
            system_instruction=system_prompt,
            model="gemini"
        )
        return result.get("action", "UNKNOWN")
    except Exception as e:
        logger.error(f"Error decoding instruction: {e}")
        return "UNKNOWN"

def should_run_now():
    """
    Checks if the agent should run based on the requirements:
    - Days: Monday, Wednesday, Friday.
    - Times: 09:00 and 17:00.
    """
    now = datetime.now()
    weekday = now.strftime("%a") # Mon, Tue, ...
    hour = now.hour
    minute = now.minute

    allowed_days = ["Mon", "Wed", "Fri"]
    allowed_hours = [9, 17]

    if weekday in allowed_days and hour in allowed_hours and 0 <= minute < 10:
        return True

    return False

def run_all_campaigns(conventions=None):
    """
    Orchestrates the execution of all defined campaigns.
    """
    logger.info("=== AI Agent Execution Started ===")

    if conventions is None:
        conventions = load_conventions()

    logger.info("Project conventions applied.")

    # 1. Trabajo Campaign
    try:
        run_trabajo_campaign(conventions=conventions)
    except Exception as e:
        logger.error(f"Trabajo campaign failed: {e}")

    # 2. Posicionamiento Campaign
    try:
        run_posicionamiento_campaign(conventions=conventions)
    except Exception as e:
        logger.error(f"Posicionamiento campaign failed: {e}")

    # 3. Contable Campaign
    try:
        run_contable_campaign(conventions=conventions)
    except Exception as e:
        logger.error(f"Contable campaign failed: {e}")

    logger.info("=== AI Agent Execution Finished ===")

def execute_action(action, chat_id, tg, conventions):
    """
    Helper to execute an action and notify the user via Telegram.
    Runs in a separate thread to avoid blocking the listener.
    """
    def wrapper():
        try:
            if action == "RUN_TRABAJO":
                tg.send_message(chat_id, "🚀 Executing 'Trabajo' campaign...")
                run_trabajo_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Trabajo' campaign completed.")
            elif action == "RUN_POSICIONAMIENTO":
                tg.send_message(chat_id, "🚀 Executing 'Posicionamiento web' campaign...")
                run_posicionamiento_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Posicionamiento web' campaign completed.")
            elif action == "RUN_CONTABLE":
                tg.send_message(chat_id, "🚀 Executing 'Ejercicio contable 2026' campaign...")
                run_contable_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Ejercicio contable' campaign completed.")
            elif action == "RUN_CHATBOT_WP":
                tg.send_message(chat_id, "🚀 Executing 'Chatbot WordPress' campaign...")
                run_chatbot_wp_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Chatbot WordPress' campaign completed.")
            elif action == "RUN_DEEP_SEO":
                tg.send_message(chat_id, "🚀 Executing 'Deep Auditoría SEO' campaign...")
                run_deep_seo_audit_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Deep Auditoría SEO' campaign completed.")
            elif action == "RUN_WP_PAGES":
                tg.send_message(chat_id, "🚀 Executing 'Páginas de WordPress' campaign...")
                run_wp_pages_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Páginas de WordPress' campaign completed.")
            elif action == "RUN_AI_ADS":
                tg.send_message(chat_id, "🚀 Executing 'Creador de anuncios con IA' campaign...")
                run_ai_ads_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Creador de anuncios con IA' campaign completed.")
            elif action == "RUN_STORE_CATALOG":
                tg.send_message(chat_id, "🚀 Executing 'Catálogo de Tienda Online' campaign...")
                run_store_catalog_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Catálogo de Tienda Online' campaign completed.")
            elif action == "RUN_AI_AUTOMATION":
                tg.send_message(chat_id, "🚀 Executing 'Automatizaciones con IA' campaign...")
                run_ai_automation_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'Automatizaciones con IA' campaign completed.")
            elif action == "RUN_EMAIL_MARKETING":
                tg.send_message(chat_id, "🚀 Executing 'E-mail marketing con IA' campaign...")
                run_ai_email_marketing_campaign(conventions=conventions)
                tg.send_message(chat_id, "✅ 'E-mail marketing con IA' campaign completed.")
            elif action == "RUN_ALL":
                tg.send_message(chat_id, "🚀 Executing ALL campaigns...")
                run_all_campaigns(conventions=conventions)
                tg.send_message(chat_id, "✅ All campaigns completed.")
            else:
                tg.send_message(chat_id, "❓ Sorry, I couldn't decode that instruction. Try 'Run all campaigns' or 'Run SEO audits'.")
        except Exception as e:
            logger.exception(f"Error executing action {action}: {e}")
            tg.send_message(chat_id, f"❌ An error occurred during execution: {str(e)}")

    threading.Thread(target=wrapper, daemon=True).start()

def listen_telegram():
    """
    Polls Telegram for new messages, decodes them, and executes instructions.
    Optimized for 24/7 operation.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment.")
        return

    tg = TelegramIntegration(token)
    conventions = load_conventions()
    offset = None

    logger.info("Telegram listener started (24/7 Mode). Waiting for instructions...")

    while True:
        try:
            updates = tg.get_updates(offset=offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"]

                        logger.info(f"Received message from {chat_id}: {text}")
                        action = decode_instruction(text, conventions)
                        execute_action(action, chat_id, tg, conventions)

            time.sleep(10) # Poll every 10 seconds
        except Exception as e:
            logger.error(f"Unexpected error in Telegram listener loop: {e}")
            time.sleep(30) # Backoff on error

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--now":
            logger.info("Manual trigger detected. Running campaigns immediately...")
            run_all_campaigns()
        elif sys.argv[1] == "--listen":
            listen_telegram()
    else:
        # Default behavior: check schedule and then enter listen mode
        if should_run_now():
            run_all_campaigns()

        # Always enter listen mode to support 24/7 operation
        listen_telegram()
