"""
handlers/ai_chat.py — AI-powered Q&A via Claude API (Anthropic).

Flow: Ask AI button → user types question → Claude generates response
"""

import logging

import anthropic
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from handlers.commands import record_ai_query, record_user
from keyboards import ai_back_to_menu, main_menu
from services.guard import AI_DAILY_LIMIT, BlockReason, check_ai_message, get_remaining

logger = logging.getLogger(__name__)
router = Router()

# Claude model to use for AI responses
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# System prompt that defines Anna's assistant persona
SYSTEM_PROMPT = (
    "You are a helpful assistant for Anna, a certified career coach. "
    "Your role is to answer questions about career development, resume writing, "
    "job interviews, LinkedIn optimization, and job search strategies. "
    "Be warm, professional, and encouraging. Keep answers concise — 3 to 5 sentences maximum. "
    "If someone asks about booking a session, suggest they use the 'Book Now' option. "
    "Do not provide medical, legal, or financial advice."
)


class AIChatStates(StatesGroup):
    """FSM state for waiting for the user's AI question."""
    waiting = State()


# ── Trigger: Ask AI button ────────────────────────────────────────────────────

@router.message(F.text == "💬 Ask AI")
async def ai_chat_start(message: Message, state: FSMContext) -> None:
    """Enter AI chat mode and prompt the user to ask a question."""
    remaining = get_remaining(message.from_user.id)

    if remaining == 0:
        await _send_limit_reached(message)
        return

    await state.set_state(AIChatStates.waiting)

    await message.answer(
        "💬 *Anna's AI Career Assistant*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ask me anything about:\n\n"
        "→ Resume & LinkedIn profile\n"
        "→ Job interviews & preparation\n"
        "→ Career change strategies\n"
        "→ Salary negotiation tips\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"_Questions left today: {remaining}/{AI_DAILY_LIMIT}_\n\n"
        "_Type your question below_ 👇",
        parse_mode="Markdown",
    )


# ── Handle user question ──────────────────────────────────────────────────────

@router.message(AIChatStates.waiting)
async def ai_chat_respond(message: Message, state: FSMContext) -> None:
    """Run guard checks, then send question to Claude and return the response."""

    # Guard: content + rate limit
    result = check_ai_message(message.from_user.id, message.text or "")

    if not result.allowed:
        await _handle_blocked(message, state, result.reason, result.remaining_today)
        return

    await state.clear()

    # Show typing indicator while generating response
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message.text}],
        )

        answer = response.content[0].text
        remaining = result.remaining_today
        record_ai_query(message.from_user.id)

        footer = f"\n\n━━━━━━━━━━━━━━━━━━━━\n_Questions left today: {remaining}/{AI_DAILY_LIMIT}_"

        await message.answer(
            text=f"💬 {answer}{footer}",
            reply_markup=ai_back_to_menu,
        )

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        await message.answer(
            "⚠️ _AI is temporarily unavailable._\n\n"
            "Please try again in a moment,\n"
            "or tap *📅 Book Now* to reach Anna directly 🙏",
            parse_mode="Markdown",
            reply_markup=main_menu,
        )


# ── "Ask Another Question" inline button ─────────────────────────────────────

@router.callback_query(F.data == "ask_again")
async def ask_again(callback: CallbackQuery, state: FSMContext) -> None:
    """Re-enter AI chat mode from the inline button."""
    await callback.answer()
    remaining = get_remaining(callback.from_user.id)
    if remaining == 0:
        await _send_limit_reached(callback.message)
        return
    await state.set_state(AIChatStates.waiting)
    await callback.message.answer(
        f"_Questions left today: {remaining}/{AI_DAILY_LIMIT}_\n\nType your next question 👇",
        parse_mode="Markdown",
    )


# ── Guard response helpers ────────────────────────────────────────────────────

_book_now_btn = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="📅 Book Now", callback_data="book_now_from_ai")]]
)


async def _send_limit_reached(message: Message) -> None:
    """Notify user they've used up their daily AI quota."""
    await message.answer(
        "⛔ *Daily AI limit reached*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"You've used all *{AI_DAILY_LIMIT} questions* for today.\n\n"
        "Want personalized help? Book a 1-on-1\n"
        "session with Anna — she'll answer\n"
        "everything directly! 👇",
        parse_mode="Markdown",
        reply_markup=_book_now_btn,
    )


async def _handle_blocked(
    message: Message,
    state: FSMContext,
    reason: BlockReason,
    remaining: int | None,
) -> None:
    """Route to the right response based on why the message was blocked."""

    if reason == BlockReason.RATE_LIMITED:
        await state.clear()
        await _send_limit_reached(message)

    elif reason == BlockReason.TOO_SHORT:
        # Stay in waiting state — let user try again
        await message.answer(
            "✏️ _Please write a bit more — at least 5 characters._\n"
            "Ask a full question and I'll be happy to help! 💬",
            parse_mode="Markdown",
        )

    elif reason == BlockReason.TOO_LONG:
        await message.answer(
            "📝 _Your message is too long (max 500 characters)._\n\n"
            "Try to summarize your question in a few sentences 👇",
            parse_mode="Markdown",
        )

    elif reason == BlockReason.REPEATED:
        await message.answer(
            "🔁 _You already asked that! Try rephrasing\n"
            "or ask something new_ 👇",
            parse_mode="Markdown",
        )

    elif reason == BlockReason.INJECTION:
        await state.clear()
        await message.answer(
            "🛡 _I can only answer career-related questions._\n\n"
            "Ask me about resumes, interviews, or career strategy!",
            parse_mode="Markdown",
            reply_markup=main_menu,
        )


@router.callback_query(F.data == "book_now_from_ai")
async def book_now_from_ai(callback: CallbackQuery, state: FSMContext) -> None:
    """Redirect to booking flow when tapped from the limit message."""
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "📅 *Booking a session with Anna*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Step 1 of 3  ●○○\n\n"
        "What's your name? 👤",
        parse_mode="Markdown",
    )
    from handlers.booking import BookingStates
    await state.set_state(BookingStates.name)
