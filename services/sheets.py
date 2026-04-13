"""
services/sheets.py — Save booking requests to Google Sheets.

Setup required:
1. Create a Google Cloud project and enable the Google Sheets API.
2. Create a Service Account and download credentials.json to the project root.
3. Share your Google Sheet with the service account email (client_email in credentials.json).
4. Set GOOGLE_SHEET_ID in your .env file.
"""

import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

import config

logger = logging.getLogger(__name__)

# Google API scopes needed to read/write Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Header row for the bookings sheet
SHEET_HEADERS = ["Timestamp", "Name", "Request", "Contact", "Status"]


def _get_sheet():
    """Authenticate and return the first worksheet of the configured spreadsheet."""
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID)
    return spreadsheet.sheet1


def _ensure_headers(sheet) -> None:
    """Add header row if the sheet is empty."""
    if not sheet.row_values(1):
        sheet.append_row(SHEET_HEADERS)


def save_booking(name: str, request: str, contact: str) -> bool:
    """
    Append a new booking row to Google Sheets.

    Args:
        name: Client's name.
        request: Client's coaching request.
        contact: Client's contact (phone or @username).

    Returns:
        True if saved successfully, False on error.
    """
    try:
        sheet = _get_sheet()
        _ensure_headers(sheet)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [timestamp, name, request, contact, "New"]
        sheet.append_row(row)

        logger.info(f"Booking saved to Google Sheets: {name}")
        return True

    except FileNotFoundError:
        logger.error(
            "credentials.json not found. "
            "Follow the setup instructions in services/sheets.py to configure Google Sheets."
        )
        return False
    except Exception as e:
        logger.error(f"Failed to save booking to Google Sheets: {e}")
        return False
