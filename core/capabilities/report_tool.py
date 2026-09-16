from core.tools import Tool
from typing import Any, Dict
from core.logger import logger

class ReportGeneratorTool(Tool):
    """
    Generates professional HTML reports based on provided data.
    """
    def __init__(self):
        super().__init__()
        self.name = "ReportGenerator"
        self.description = "Converts raw data into formatted HTML report fragments (e.g., financial tables, progress bars)."

    def execute(self, data: Dict[str, Any], report_type: str = "financial", **kwargs) -> str:
        """
        Generates HTML based on the report type.
        """
        try:
            if report_type == "financial":
                return self._generate_financial_html(data)
            else:
                return f"<p>Report type {report_type} not implemented yet.</p>"
        except Exception as e:
            logger.error(f"Error in ReportGeneratorTool: {e}")
            return f"<p>Error generating report: {e}</p>"

    def _generate_financial_html(self, data: Dict[str, Any]) -> str:
        # Progress Bar HTML
        percentage = data.get('percentage', 0)
        current = data.get('raw_earnings', 0)
        goal = data.get('raw_goal', 0)

        progress_bar = f"""
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

        # Data Table HTML
        table = f"""
        <div style="margin: 20px 0; font-family: sans-serif; line-height: 1.6;">
            <div style="margin-bottom: 15px; font-weight: bold; font-size: 16px;">Resumen Financiero</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr><td style="padding: 5px 0; color: #666;">Objetivo Diario:</td><td style="padding: 5px 0; text-align: right; font-weight: bold;">{data.get('objetivo_diario', 'N/A')}</td></tr>
                <tr><td style="padding: 5px 0; color: #666;">Objetivo Semanal:</td><td style="padding: 5px 0; text-align: right; font-weight: bold;">{data.get('objetivo_semanal', 'N/A')}</td></tr>
                <tr><td style="padding: 5px 0; color: #666;">Objetivo Mensual:</td><td style="padding: 5px 0; text-align: right; font-weight: bold;">{data.get('objetivo_mensual', 'N/A')}</td></tr>
                <tr style="border-top: 1px solid #eee;">
                    <td style="padding: 5px 0; color: #000; font-weight: bold;">Facturación Mensual:</td>
                    <td style="padding: 5px 0; text-align: right; font-weight: bold; color: #4caf50;">{data.get('facturacion_mensual', 'N/A')}</td>
                </tr>
            </table>
        </div>
        """

        return f"{table}{progress_bar}"
