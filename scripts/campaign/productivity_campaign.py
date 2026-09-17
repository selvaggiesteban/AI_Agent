import os
import json
from core.integrations import GoogleIntegration, TrelloIntegration, GmailIntegration
from core.logger import logger
from core.ai_engine import llm

def run_productivity_campaign(conventions=""):
    """
    Executes the 'Productivity' campaign:
    1. Fetches goals from Google Sheets.
    2. Fetches Trello cards in 'In Process'.
    3. Generates a personalized report using AI and sends it.
    """
    logger.info("Starting 'Productivity' campaign...")

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
        goals = {"daily_goal": "N/A", "weekly_goal": "N/A", "monthly_goal": "N/A"}
        if len(sheet_data) >= 4:
            goals["daily_goal"] = sheet_data[1][0] if len(sheet_data[1]) > 0 else "N/A"
            goals["weekly_goal"] = sheet_data[2][0] if len(sheet_data[2]) > 0 else "N/A"
            goals["monthly_goal"] = sheet_data[3][0] if len(sheet_data[3]) > 0 else "N/A"

        # 2. Fetch Trello Cards
        cards = trello.get_board_cards(config["trello_board_id"], "En Proceso")
        cards_text = "\n".join([f"- {c['name']}" for c in cards]) if cards else "No tasks in process."

        # 3. Generate Personalized Message with AI
        system_prompt = (
            f"You are the Professional Assistant for Esteban Selvaggi. "
            f"Your goal is to generate a daily productivity report that is motivating, professional, and concise. "
            f"Use a tone that reflects the following project conventions:\n\n{conventions}"
        )

        prompt = (
            f"Generate a daily report based on the following data:\n"
            f"Daily Goal: {goals['daily_goal']}\n"
            f"Weekly Goal: {goals['weekly_goal']}\n"
            f"Monthly Goal: {goals['monthly_goal']}\n"
            f"Tasks in Process: {cards_text}\n\n"
            f"Return a JSON object with a 'body_html' key containing the formatted report in HTML."
        )

        try:
            ai_result = llm.generate_structured(
                prompt=prompt,
                system_instruction=system_prompt,
                model="gemini"
            )
            message_html = ai_result.get("body_html", f"<p>{config['email_template'].format(daily_goal=goals['daily_goal'], weekly_goal=goals['weekly_goal'], monthly_goal=goals['monthly_goal'], trello_cards=cards_text)}</p>")
        except Exception as e:
            logger.error(f"AI report generation failed: {e}")
            message_html = f"<p>{config['email_template'].format(daily_goal=goals['daily_goal'], weekly_goal=goals['weekly_goal'], monthly_goal=goals['monthly_goal'], trello_cards=cards_text)}</p>"

        # 4. Send via Gmail
        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config["email_subject"],
            body_html=message_html
        )

        if success:
            logger.info("'Productivity' campaign completed successfully.")
        else:
            logger.error("'Productivity' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Productivity' campaign: {e}")

if __name__ == "__main__":
    run_productivity_campaign()
