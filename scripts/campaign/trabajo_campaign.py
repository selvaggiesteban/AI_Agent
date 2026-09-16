import os
import json
from core.integrations import GoogleIntegration, TrelloIntegration, GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_trabajo_campaign(conventions=""):
    """
    Executes the 'Trabajo' campaign:
    1. Fetches goals from Google Sheets.
    2. Fetches Trello cards in 'En Proceso'.
    3. Generates a personalized report using AI and sends it.
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

        # 3. Generate Personalized Message with AI
        system_prompt = (
            f"You are the Professional Assistant for Esteban Selvaggi. "
            f"Your goal is to generate a daily productivity report that is motivating, professional, and concise. "
            f"Use a tone that reflects the following project conventions:\n\n{conventions}"
        )

        prompt = (
            f"Generate a daily report based on the following data:\n"
            f"Daily Goal: {goals['objetivo_diario']}\n"
            f"Weekly Goal: {goals['objetivo_semanal']}\n"
            f"Monthly Goal: {goals['objetivo_mensual']}\n"
            f"Tasks in Process: {cards_text}\n\n"
            f"Return a JSON object with a 'body_html' key containing the formatted report in HTML."
        )

        try:
            ai_result = llm.generate_structured(
                prompt=prompt,
                system_instruction=system_prompt,
                model="gemini"
            )
            message_html = ai_result.get("body_html", f"<p>{config['email_template'].format(objetivo_diario=goals['objetivo_diario'], objetivo_semanal=goals['objetivo_semanal'], objetivo_mensual=goals['objetivo_mensual'], trello_cards=cards_text)}</p>")
        except Exception as e:
            logger.error(f"AI report generation failed: {e}")
            message_html = f"<p>{config['email_template'].format(objetivo_diario=goals['objetivo_diario'], objetivo_semanal=goals['objetivo_semanal'], objetivo_mensual=goals['objetivo_mensual'], trello_cards=cards_text)}</p>"

        # 4. Send via Gmail
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config["email_subject"],
            body_html=message_html
        )

        if success:
            logger.info("'Trabajo' campaign completed successfully.")
        else:
            logger.error("'Trabajo' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Trabajo' campaign: {e}")

if __name__ == "__main__":
    run_trabajo_campaign()
