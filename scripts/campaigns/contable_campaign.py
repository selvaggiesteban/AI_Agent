import os
import json
import pandas as pd
from core.integrations import GmailIntegration
from core.ai_engine import llm
from core.logger import logger
from core.paths import FINANCIAL_DATA_PATH

def parse_financial_data():
    """
    Parses the financial data CSV to calculate total earnings.
    Returns a dictionary with goals and current earnings.
    """
    try:
        df = pd.read_csv(FINANCIAL_DATA_PATH)
        # Expected column: 'Earnings'
        total_earnings = df['Earnings'].sum()
        return total_earnings
    except Exception as e:
        logger.error(f"Error parsing financial CSV: {e}")
        return 0

def generate_progress_bar_html(current, goal):
    """
    Generates an HTML fragment with a CSS-styled progress bar.
    """
    percentage = min(100, max(0, (current / goal) * 100)) if goal > 0 else 0

    html = f"""
    <div style="margin: 20px 0; font-family: sans-serif;">
        <div style="margin-bottom: 10px; font-weight: bold;">Progreso Financiero Mensual</div>
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; overflow: hidden; border: 1px solid #ccc;">
            <div style="width: {percentage:.1f}%; background-color: #4caf50; height: 25px; text-align: center; color: white; font-weight: bold; line-height: 25px;">
                {percentage:.1f}%
            </div>
        </div>
        <div style="margin-top: 5px; font-size: 14px; color: #666;">
            Total Actual: <b>${current:,.2f}</b> / Objetivo: <b>${goal:,.2f}</b>
        </div>
    </div>
    """
    return html

def run_contable_campaign(conventions=""):
    """
    Executes the 'Ejercicio contable 2026' campaign:
    1. Fetches financial data (goals, billing).
    2. Generates a personalized report using AI and sends it.
    """
    logger.info("Starting 'Ejercicio contable 2026' campaign...")

    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)["contable"]

        # Fetch real data from CSV
        current_earnings = parse_financial_data()

        # In a real scenario, goals might come from a config file or Google Sheet.
        # For now, we'll use the goal from the config if available, otherwise a default.
        monthly_goal = config.get("monthly_goal", 3000)

        financial_data = {
            "objetivo_diario": f"${(monthly_goal/30):.2f}",
            "objetivo_semanal": f"${(monthly_goal/4):.2f}",
            "objetivo_mensual": f"${monthly_goal:,.2f}",
            "facturacion_mensual": f"${current_earnings:,.2f}"
        }

        # Generate Progress Bar HTML
        progress_bar_html = generate_progress_bar_html(current_earnings, monthly_goal)

        # Generate Personalized Message with AI
        system_prompt = (
            f"You are the Financial Advisor for Esteban Selvaggi. "
            f"Your goal is to generate a concise, professional, and analytical financial summary. "
            f"Apply the following project conventions for tone and style:\n\n{conventions}"
        )

        prompt = (
            f"Generate a financial summary for the 'Ejercicio Contable 2026' based on the following data:\n"
            f"Daily Goal: {financial_data['objetivo_diario']}\n"
            f"Weekly Goal: {financial_data['objetivo_semanal']}\n"
            f"Monthly Goal: {financial_data['objetivo_mensual']}\n"
            f"Monthly Billing: {financial_data['facturacion_mensual']}\n\n"
            f"Return a JSON object with a 'body_html' key containing the formatted report in HTML."
        )

        try:
            ai_result = llm.generate_structured(
                prompt=prompt,
                system_instruction=system_prompt,
                model="gemini"
            )
            ai_message_html = ai_result.get("body_html", f"<p>{config['email_template'].format(**financial_data)}</p>")
        except Exception as e:
            logger.error(f"AI financial report generation failed: {e}")
            ai_message_html = f"<p>{config['email_template'].format(**financial_data)}</p>"

        # Combine AI message with the Progress Bar
        final_body_html = f"{ai_message_html}{progress_bar_html}"

        # Save files for attachments
        report_path = os.path.join("data/outputs", "financial_report.html")
        os.makedirs("data/outputs", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_body_html)

        csv_path = os.path.join("data/outputs", "financial_data_summary.csv")
        summary_df = pd.DataFrame([financial_data])
        summary_df.to_csv(csv_path, index=False)

        gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

        success = gmail.send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=config["email_subject"],
            body_html=final_body_html,
            attachments=[report_path, csv_path]
        )

        if success:
            logger.info("'Ejercicio contable 2026' campaign completed successfully.")
        else:
            logger.error("'Ejercicio contable 2026' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Ejercicio contable 2026' campaign: {e}")

if __name__ == "__main__":
    run_contable_campaign()
