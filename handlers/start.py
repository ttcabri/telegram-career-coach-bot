"""
handlers/start.py — /start command and main menu entry point.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import main_menu

router = Router()

WELCOME_MESSAGE = (
    "👋 *Hi! Welcome to Anna's Career Studio*\n\n"
    "I'm her AI assistant — here to help you take the next big step in your career 🚀\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Anna is a certified career coach who has helped 200+ professionals:\n\n"
    "→ Land jobs at top companies\n"
    "→ Craft resumes that get callbacks\n"
    "→ Ace interviews with confidence\n"
    "→ Build a clear career roadmap\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "_What would you like to do today?_ 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Handle /start — clear any active state and show the main menu."""
    # Clear any ongoing FSM state (booking form, AI chat, etc.)
    await state.clear()

    await message.answer(
        text=WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=main_menu,
    )
