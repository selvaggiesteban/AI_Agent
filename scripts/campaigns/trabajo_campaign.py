import os
import json
from core.integrations import GoogleIntegration, TrelloIntegration, GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_trabajo_campaign():
    """
    Executes the 'Trabajo' campaign:
    1. Fetches goals from Google Sheets.
    2. Fetches Trello cards in 'En Proceso'.
    3. Formats and sends the daily report.
    """
    logger.info("Starting 'Trabajo' campaign...")

    try:
        # Load config
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)["trabajo"]

        # Initialize integrations
        google = GoogleIntegration(os.environ.get("GOOGLE_CREDENTIALS_PATH"))
        trello = TrelloIntegration(os.environ.get("TRELLO_API_KEY"), os.environ.get("TRELLO_TOKEN"))
        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

        # 1. Fetch Goals from Google Sheet
        sheet_data = google.get_sheet_data(config["google_sheet_id"], config["google_sheet_range"])
        # Assume structure: Row 1: Header, Row 2: Daily, Row 3: Weekly, Row 4: Monthly
        goals = {"objetivo_diario": "N/A", "objetivo_semanal": "N/A", "objetivo_mensual": "N/A"}
        if len(sheet_data) >= 4:
            goals["objetivo_diario"] = sheet_data[1][0] if len(sheet_data[1]) > 0 else "N/A"
            goals["objetivo_semanal"] = sheet_data[2][0] if len(sheet_data[2]) > 0 else "N/A"
            goals["objetivo_mensual"] = sheet_data[3][0] if len(sheet_data[3]) > 0 else "N/A"

        # 2. Fetch Trello Cards
        cards = trello.get_board_cards(config["trello_board_id"], "En Proceso")
        cards_text = "\n".join([f"- {c['name']}" for c in cards]) if cards else "No hay tareas en proceso."

        # 3. Format Message
        message = config["email_template"].format(
            objetivo_diario=goals["objetivo_diario"],
            objetivo_semanal=goals["objetivo_semanal"],
            objetivo_mensual=goals["objetivo_mensual"],
            trello_cards=cards_text
        )

        # 4. Send via Gmail (as a draft for safety, or direct send)
        # In this context, we use direct send as per typical agent automation
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"), # Sending to himself as a report
            subject=config["email_subject"],
            body_html=f"<p>{message.replace('\\n', '<br>')}</p>"
        )

        if success:
            logger.info("'Trabajo' campaign completed successfully.")
        else:
            logger.error("'Trabajo' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Trabajo' campaign: {e}")

if __name__ == "__main__":
    run_trabajo_campaign()
