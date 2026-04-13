"""
handlers/commands.py — Utility commands: /help, /stats, /cancel.
"""

import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import config
from keyboards import main_menu
from services.guard import AI_DAILY_LIMIT, get_remaining

logger = logging.getLogger(__name__)
router = Router()

# Track bot start time and basic counters (in-memory)
_start_time = datetime.now()
_stats = {"bookings": 0, "ai_queries": 0, "users": set()}


def record_booking() -> None:
    _stats["bookings"] += 1


def record_ai_query(user_id: int) -> None:
    _stats["ai_queries"] += 1
    _stats["users"].add(user_id)


def record_user(user_id: int) -> None:
    _stats["users"].add(user_id)


# ── /help ─────────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Show available commands and bot features."""
    record_user(message.from_user.id)
    await message.answer(
        "ℹ️ *How to use this bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Menu buttons:*\n"
        "📋 *Services* — view coaching packages\n"
        "💰 *Prices* — see pricing plans\n"
        "📅 *Book Now* — request a session\n"
        "💬 *Ask AI* — get AI career advice\n\n"
        "*Commands:*\n"
        "/start — restart the bot\n"
        "/help — show this message\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_During booking — tap_ *🚫 Cancel Booking*\n"
        "_to exit the form at any time._\n\n"
        f"_AI limit: {AI_DAILY_LIMIT} questions per day per user_",
        parse_mode="Markdown",
        reply_markup=main_menu,
    )


# ── /stats (owner only) ───────────────────────────────────────────────────────

@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Show bot statistics — only available to the owner."""
    if message.from_user.id != config.OWNER_CHAT_ID:
        await message.answer("⛔ This command is for the bot owner only.")
        return

    uptime = datetime.now() - _start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes = remainder // 60

    await message.answer(
        "📊 *Bot Statistics*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅  Bookings received:    *{_stats['bookings']}*\n"
        f"💬  AI queries handled:   *{_stats['ai_queries']}*\n"
        f"👥  Unique users:         *{len(_stats['users'])}*\n\n"
        f"⏱  Uptime: *{hours}h {minutes}m*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_Counters reset on bot restart_",
        parse_mode="Markdown",
    )


# ── /cancel ───────────────────────────────────────────────────────────────────

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Cancel any active form and return to the main menu."""
    current = await state.get_state()
    await state.clear()

    if current:
        await message.answer(
            "✅ Action cancelled.\n_Returning to main menu._",
            parse_mode="Markdown",
            reply_markup=main_menu,
        )
    else:
        await message.answer(
            "Nothing to cancel — use the menu below 👇",
            reply_markup=main_menu,
        )
