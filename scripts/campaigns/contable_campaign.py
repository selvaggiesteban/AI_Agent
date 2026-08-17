import os
import json
from core.integrations import GmailIntegration
from core.logger import logger

def run_contable_campaign():
    """
    Executes the 'Ejercicio contable 2026' campaign:
    1. Fetches financial data (goals, billing).
    2. Formats and sends the report.
    """
    logger.info("Starting 'Ejercicio contable 2026' campaign...")

    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)["contable"]

        # Mock data fetching - in reality, this would read from a DB or Google Sheet
        financial_data = {
            "objetivo_diario": "$100",
            "objetivo_semanal": "$700",
            "objetivo_mensual": "$3000",
            "facturacion_mensual": "$2500"
        }

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

        message = config["email_template"].format(**financial_data)

        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config["email_subject"],
            body_html=f"<p>{message.replace('\\n', '<br>')}</p>"
        )

        if success:
            logger.info("'Ejercicio contable 2026' campaign completed successfully.")
        else:
            logger.error("'Ejercicio contable 2026' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Ejercicio contable 2026' campaign: {e}")

if __name__ == "__main__":
    run_contable_campaign()
