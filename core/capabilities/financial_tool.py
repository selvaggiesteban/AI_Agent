import pandas as pd
from core.tools import Tool
from core.paths import FINANCIAL_DATA_PATH
from core.logger import logger
from typing import Dict, Any

class FinancialAnalyzerTool(Tool):
    """
    Analyzes financial data from CSV and calculates progress against goals.
    """
    def __init__(self):
        super().__init__()
        self.name = "FinancialAnalyzer"
        self.description = "Analyzes financial CSV data to calculate current earnings and progress against monthly goals."

    def execute(self, monthly_goal: float = 3000.0, **kwargs) -> Dict[str, Any]:
        """
        Parses the financial CSV and returns metrics.
        """
        try:
            df = pd.read_csv(FINANCIAL_DATA_PATH)
            total_earnings = df['Earnings'].sum()

            financial_data = {
                "objetivo_diario": f"${(monthly_goal/30):.2f}",
                "objetivo_semanal": f"${(monthly_goal/4):.2f}",
                "objetivo_mensual": f"${monthly_goal:,.2f}",
                "facturacion_mensual": f"${total_earnings:,.2f}",
                "raw_earnings": total_earnings,
                "raw_goal": monthly_goal,
                "percentage": min(100, max(0, (total_earnings / monthly_goal) * 100)) if monthly_goal > 0 else 0
            }

            logger.info(f"Financial analysis complete: {financial_data['percentage']:.1f}% of goal reached.")
            return financial_data

        except Exception as e:
            logger.error(f"Error in FinancialAnalyzerTool: {e}")
            return {"error": str(e)}
