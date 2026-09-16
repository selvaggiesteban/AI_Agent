import os
from core.tools import Tool
from core.integrations import GmailIntegration, TelegramIntegration
from core.logger import logger
from typing import List, Optional

class NotificationTool(Tool):
    """
    Sends notifications via Gmail and Telegram.
    """
    def __init__(self):
        super().__init__()
        self.name = "NotificationTool"
        self.description = "Sends messages and reports via Gmail and Telegram."

        # Initialize integrations
        self.gmail = GmailIntegration(
            os.environ.get("GMAIL_USER"),
            os.environ.get("GMAIL_APP_PASSWORD")
        )
        self.telegram = TelegramIntegration(
            os.environ.get("TELEGRAM_BOT_TOKEN")
        )

    def execute(self, channel: str, recipient: str, subject: str = "AI Agent Notification", body: str = "", attachments: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Sends a notification through the specified channel.
        """
        try:
            if channel.lower() == "gmail":
                success = self.gmail.send_email(
                    to_email=recipient,
                    subject=subject,
                    body_html=body,
                    attachments=attachments
                )
            elif channel.lower() == "telegram":
                # recipient for telegram is chat_id
                success = self.telegram.send_message(
                    chat_id=int(recipient),
                    text=body
                )
            else:
                logger.error(f"Unsupported notification channel: {channel}")
                return False

            if success:
                logger.info(f"Notification sent successfully via {channel} to {recipient}")
            return success

        except Exception as e:
            logger.error(f"Error in NotificationTool: {e}")
            return False
