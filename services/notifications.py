"""
services/notifications.py — Send booking notifications to the bot owner.
"""

import logging
from datetime import datetime

from aiogram import Bot

import config

logger = logging.getLogger(__name__)


async def notify_owner(bot: Bot, name: str, request: str, contact: str) -> None:
    """
    Send a formatted booking notification to the bot owner via Telegram.

    Args:
        bot: The aiogram Bot instance.
        name: Client's name.
        request: Client's coaching request description.
        contact: Client's phone number or Telegram username.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    message = (
        "🔔 *NEW BOOKING REQUEST*\n\n"
        f"👤 *Name:* {name}\n"
        f"📝 *Request:* {request}\n"
        f"📞 *Contact:* {contact}\n"
        f"⏰ *Time:* {timestamp}\n\n"
        "Reply to this message to contact the client."
    )

    try:
        await bot.send_message(
            chat_id=config.OWNER_CHAT_ID,
            text=message,
            parse_mode="Markdown",
        )
        logger.info(f"Owner notified about booking from {name}")
    except Exception as e:
        # Log the error but don't crash — the booking is already saved
        logger.error(f"Failed to notify owner: {e}")
