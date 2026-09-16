from core.tools import registry
from .financial_tool import FinancialAnalyzerTool
from .report_tool import ReportGeneratorTool
from .notification_tool import NotificationTool
from .seo_tool import SEOTool
from .productivity_tool import ProductivityTool

def register_capabilities():
    """
    Registers all available system capabilities into the global tool registry.
    """
    registry.register(FinancialAnalyzerTool())
    registry.register(ReportGeneratorTool())
    registry.register(NotificationTool())
    registry.register(SEOTool())
    registry.register(ProductivityTool())

# Auto-register upon import
register_capabilities()
