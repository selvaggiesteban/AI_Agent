import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
from core.tools import Tool
from core.integrations import GoogleIntegration, GmailIntegration
from core.logger import logger
from core.ai_engine import llm

class SEOTool(Tool):
    """
    Provides capabilities for SEO auditing and positioning analysis.
    """
    def __init__(self):
        super().__init__(
            name="SEOTool",
            description="Analyzes SEO metrics from GSC/GA4 and generates audits for specified domains."
        )

    def execute(self, domains: List[str] = None, conventions: str = "") -> str:
        """
        Performs SEO audits for the given domains. If no domains are provided, uses the config file.
        """
        try:
            if domains is None:
                with open("data/campaign_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f).get("posicionamiento", {})
                    domains = config.get("domains", [])
                    email_subject = config.get("email_subject", "SEO Audit Report")
                    email_template = config.get("email_template", "SEO Audits:\n{seo_audits}")
            else:
                # If domains are provided manually, we use a generic template
                email_subject = "Manual SEO Audit Report"
                email_template = "SEO Audits:\n{seo_audits}"

            if not domains:
                return "No domains found to audit."

            # Initialize integrations
            google = GoogleIntegration(os.environ.get("GOOGLE_CREDENTIALS_PATH"))
            gmail = GmailIntegration(os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD"))

            audits_results = []
            audit_data_for_csv = []

            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            for domain in domains:
                logger.info(f"Auditing {domain}...")

                # 1. Fetch GSC Metrics
                gsc_url = f"sc-domain:{domain}" if not domain.startswith("http") else domain
                gsc_data = google.get_gsc_metrics(gsc_url, start_date, end_date)

                # 2. Fetch GA4 Metrics (Mocked as per legacy script)
                ga4_data = {"activeUsers": "N/A", "sessions": "N/A"}

                metrics_summary = (
                    f"GSC (last 30 days): Clicks={gsc_data.get('clicks', 0)}, "
                    f"Impressions={gsc_data.get('impressions', 0)}, CTR={gsc_data.get('ctr', 'N/A')}. "
                    f"Top Queries: {', '.join(gsc_data.get('top_queries', []))}. "
                    f"GA4: Active Users={ga4_data['activeUsers']}, Sessions={ga4_data['sessions']}."
                )

                system_prompt = f"You are a professional SEO auditor. Be concise and actionable. Apply these project conventions: {conventions}"
                prompt = f"Based on these metrics for {domain}: {metrics_summary}\n\nGenerate a very brief 3-point SEO audit summary. Return as a simple string."

                try:
                    result = llm.generate_structured(
                        prompt=prompt,
                        system_instruction=system_prompt,
                        model="gemini"
                    )
                    audit = result.get("summary", "Audit completed: metrics fetched successfully.")
                except Exception as e:
                    logger.error(f"SEO audit AI summary failed for {domain}: {e}")
                    audit = f"Metrics fetched: {metrics_summary}"

                audits_results.append(f"<b>{domain}</b>: {audit}")
                audit_data_for_csv.append({"domain": domain, "audit": audit})

            consolidated_audits = "<br><br>".join(audits_results)
            message = email_template.format(seo_audits=consolidated_audits)

            # Save files for attachments
            report_path = os.path.join("data/outputs", "seo_report.html")
            os.makedirs("data/outputs", exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"<html><body>{message}</body></html>")

            csv_path = os.path.join("data/outputs", "seo_audits.csv")
            pd.DataFrame(audit_data_for_csv).to_csv(csv_path, index=False)

            success = gmail.send_email(
                to_email=os.environ.get("GMAIL_USER"),
                subject=email_subject,
                body_html=f"<p>{message}</p>",
                attachments=[report_path, csv_path]
            )

            if success:
                return f"SEO audits completed and report sent to {os.environ.get('GMAIL_USER')}."
            else:
                return "SEO audits completed but email failed to send."

        except Exception as e:
            logger.exception(f"Error in SEOTool: {e}")
            return f"SEOTool failed: {str(e)}"
