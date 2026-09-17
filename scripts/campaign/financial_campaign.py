import os
import json
import pandas as pd
from core.integrations import GmailIntegration
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
        <div style="margin-bottom: 10px; font-weight: bold;">Monthly Financial Progress</div>
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; overflow: hidden; border: 1px solid #ccc;">
            <div style="width: {percentage:.1f}%; background-color: #4caf50; height: 25px; text-align: center; color: white; font-weight: bold; line-height: 25px;">
                {percentage:.1f}%
            </div>
        </div>
        <div style="margin-top: 5px; font-size: 14px; color: #666;">
            Current Total: <b>${current:,.2f}</b> / Goal: <b>${goal:,.2f}</b>
        </div>
    </div>
    """
    return html

def generate_key_data_html(data):
    """
    Generates a simple HTML fragment with the key financial data.
    """
    return f"""
    <div style="margin: 20px 0; font-family: sans-serif; line-height: 1.6;">
        <div style="margin-bottom: 15px; font-weight: bold; font-size: 16px;">Financial Summary</div>
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
                <td style="padding: 5px 0; color: #666;">Daily Goal:</td>
                <td style="padding: 5px 0; text-align: right; font-weight: bold;">{data['daily_goal']}</td>
            </tr>
            <tr>
                <td style="padding: 5px 0; color: #666;">Weekly Goal:</td>
                <td style="padding: 5px 0; text-align: right; font-weight: bold;">{data['weekly_goal']}</td>
            </tr>
            <tr>
                <td style="padding: 5px 0; color: #666;">Monthly Goal:</td>
                <td style="padding: 5px 0; text-align: right; font-weight: bold;">{data['monthly_goal']}</td>
            </tr>
            <tr style="border-top: 1px solid #eee;">
                <td style="padding: 5px 0; color: #000; font-weight: bold;">Monthly Billing:</td>
                <td style="padding: 5px 0; text-align: right; font-weight: bold; color: #4caf50;">{data['monthly_billing']}</td>
            </tr>
        </table>
    </div>
    """

def run_financial_campaign(conventions=""):
    """
    Executes the 'Financial Exercise 2026' campaign:
    1. Fetches financial data (goals, billing).
    2. Generates a simple data report and sends it.
    """
    logger.info("Starting 'Financial Exercise 2026' campaign...")

    try:
        with open("data/campaign_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)["contable"]

        # Fetch real data from CSV
        current_earnings = parse_financial_data()

        # In a real scenario, goals might come from a config file or Google Sheet.
        # For now, we'll use the goal from the config if available, otherwise a default.
        monthly_goal = config.get("monthly_goal", 3000)

        financial_data = {
            "daily_goal": f"${(monthly_goal/30):.2f}",
            "weekly_goal": f"${(monthly_goal/4):.2f}",
            "monthly_goal": f"${monthly_goal:,.2f}",
            "monthly_billing": f"${current_earnings:,.2f}"
        }

        # Generate Progress Bar HTML
        progress_bar_html = generate_progress_bar_html(current_earnings, monthly_goal)

        # Generate Key Data HTML (No AI)
        data_message_html = generate_key_data_html(financial_data)

        # Combine data message with the Progress Bar
        final_body_html = f"{data_message_html}{progress_bar_html}"

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
            logger.info("'Financial Exercise 2026' campaign completed successfully.")
        else:
            logger.error("'Financial Exercise 2026' campaign failed to send email.")

    except Exception as e:
        logger.exception(f"Critical error in 'Financial Exercise 2026' campaign: {e}")

if __name__ == "__main__":
    run_financial_campaign()
