"""
handlers/info.py — Services and pricing information handlers.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards import back_to_menu

router = Router()

SERVICES_TEXT = (
    "📋 *SERVICES*\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🎯 *Resume Review & Optimization*\n"
    "_Full rewrite tailored for ATS & recruiters_\n"
    "· Keyword targeting & formatting\n"
    "· 2 revision rounds included\n\n"
    "🎤 *Interview Preparation*\n"
    "_1-hour mock interview with real feedback_\n"
    "· Behavioral & role-specific questions\n"
    "· Personal improvement plan\n\n"
    "🗺 *Career Strategy Session*\n"
    "_90-min deep-dive into your career path_\n"
    "· SMART goal setting\n"
    "· Step-by-step action plan\n\n"
    "🚀 *Full Coaching Package*\n"
    "_4-week intensive program_\n"
    "· Resume · LinkedIn · Interviews · Strategy\n"
    "· Weekly 1-on-1 calls with Anna\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "_All sessions via Zoom or Google Meet_ 🌐"
)

PRICES_TEXT = (
    "💰 *PRICING*\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🎯  Resume Review            *$97*\n"
    "🎤  Interview Prep           *$147*\n"
    "🗺  Career Strategy          *$197*\n"
    "🚀  Full Package _(4 weeks)_   *$497*\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "✅  Telegram support included in every plan\n"
    "🔒  Satisfaction guaranteed\n\n"
    "_Ready to invest in your future?_\n"
    "Tap *📅 Book Now* below! 👇"
)


@router.message(F.text == "📋 Services")
async def show_services(message: Message) -> None:
    """Display list of coaching services."""
    await message.answer(
        text=SERVICES_TEXT,
        parse_mode="Markdown",
        reply_markup=back_to_menu,
    )


@router.message(F.text == "💰 Prices")
async def show_prices(message: Message) -> None:
    """Display the price list."""
    await message.answer(
        text=PRICES_TEXT,
        parse_mode="Markdown",
        reply_markup=back_to_menu,
    )


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery) -> None:
    """Handle 'Back to Menu' inline button — just acknowledge it."""
    await callback.answer()
    await callback.message.answer(
        text="Choose an option below 👇",
    )
