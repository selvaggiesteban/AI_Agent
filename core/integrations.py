import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

# Try to import Google API clients
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
except ImportError:
    pass

# Try to import Trello
try:
    import pytrello
except ImportError:
    pass

from core.logger import logger

class GoogleIntegration:
    """Wrapper for Google Sheets and Gmail APIs."""
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.send'
        ]
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        try:
            self.creds = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes
            )
            logger.info("Google API authenticated successfully.")
        except Exception as e:
            logger.error(f"Google API Authentication failed: {e}")

    def get_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """Reads data from a Google Sheet."""
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            return result.get('values', [])
        except Exception as e:
            logger.error(f"Error reading Google Sheet: {e}")
            return []

    def update_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]):
        """Writes data to a Google Sheet."""
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            body = {'values': values}
            sheet.values().update(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption="RAW", body=body
            ).execute()
            logger.info(f"Google Sheet {spreadsheet_id} updated.")
        except Exception as e:
            logger.error(f"Error updating Google Sheet: {e}")

class TrelloIntegration:
    """Wrapper for Trello API."""
    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.client = pytrello.TrelloClient(api_key=api_key, token=token)

    def get_board_cards(self, board_id: str, list_name: str = "En Proceso") -> List[Dict[str, Any]]:
        """Fetches cards from a specific list on a Trello board."""
        try:
            board = self.client.get_board(board_id)
            all_lists = board.all_lists()
            target_list = next((l for l in all_lists if l.name == list_name), None)

            if not target_list:
                logger.warning(f"List '{list_name}' not found on board {board_id}.")
                return []

            cards = target_list.list_cards()
            return [{"id": c.id, "name": c.name, "desc": c.desc} for c in cards]
        except Exception as e:
            logger.error(f"Error fetching Trello cards: {e}")
            return []

    def create_card(self, list_id: str, name: str, desc: str = ""):
        """Creates a new card in Trello."""
        try:
            trello_list = self.client.get_list(list_id)
            card = trello_list.add_card(name, desc=desc)
            logger.info(f"Trello card created: {card.name}")
            return card
        except Exception as e:
            logger.error(f"Error creating Trello card: {e}")
            return None

class GmailIntegration:
    """Wrapper for Gmail sending and drafts."""
    def __init__(self, sender_email: str, app_password: str):
        self.sender_email = sender_email
        self.app_password = app_password

    def send_email(self, to_email: str, subject: str, body_html: str):
        """Sends a direct email via SMTP."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body_html, 'html'))

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.sender_email, self.app_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False

    def create_draft(self, subject: str, body_html: str, recipients: List[str]):
        """Creates a Gmail draft using IMAP APPEND (similar to scripts/campaign_manager/drafts.py)."""
        import imaplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.utils import formatdate

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = self.sender_email
            msg["Subject"] = subject
            msg["Date"] = formatdate(localtime=True)
            msg["Bcc"] = ", ".join(recipients)
            msg.attach(MIMEText(body_html, "html", "utf-8"))
            raw = msg.as_string()

            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(self.sender_email, self.app_password)
            status, data = imap.append("[Gmail]/Borradores", "\\Draft", None, raw.encode("utf-8"))
            imap.logout()

            if status == "OK":
                logger.info(f"Gmail draft created for {len(recipients)} recipients.")
                return True
            else:
                logger.error(f"IMAP APPEND failed: {data}")
                return False
        except Exception as e:
            logger.error(f"Error creating Gmail draft: {e}")
            return False

class TelegramIntegration:
    """Wrapper for Telegram Bot API."""
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def get_updates(self, offset=None):
        """Fetches new messages from Telegram."""
        import requests
        params = {"offset": offset, "timeout": 30}
        try:
            response = requests.get(f"{self.base_url}/getUpdates", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching Telegram updates: {e}")
            return {}

    def send_message(self, chat_id: int, text: str):
        """Sends a message to a specific chat."""
        import requests
        params = {"chat_id": chat_id, "text": text}
        try:
            response = requests.post(f"{self.base_url}/sendMessage", params=params)
            response.raise_for_status()
            logger.info(f"Telegram message sent to {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
