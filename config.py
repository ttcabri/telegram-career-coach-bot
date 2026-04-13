"""
config.py — Load environment variables from .env file.
All settings are accessed as module-level constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot token from @BotFather
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# Anthropic API key for Claude AI responses
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

# Owner's Telegram chat ID for booking notifications
OWNER_CHAT_ID: int = int(os.getenv("OWNER_CHAT_ID", "0"))

# Google Sheets spreadsheet ID (from the sheet URL)
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")

# Validate required settings on startup
def validate_config() -> None:
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not OWNER_CHAT_ID:
        missing.append("OWNER_CHAT_ID")
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
