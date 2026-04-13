"""
handlers/booking.py — FSM booking form for coaching session requests.

Flow: Book Now → name → request description → contact → confirm/cancel
"""

import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from handlers.commands import record_booking, record_user
from keyboards import booking_cancel_menu, booking_confirm, main_menu
from services import notifications, sheets

logger = logging.getLogger(__name__)
router = Router()


class BookingStates(StatesGroup):
    """FSM states for the booking conversation flow."""
    name = State()
    request = State()
    contact = State()
    confirm = State()


# ── Step 1: Start booking ─────────────────────────────────────────────────────

@router.message(F.text == "📅 Book Now")
async def booking_start(message: Message, state: FSMContext) -> None:
    """Initiate the booking form — ask for the client's name."""
    await state.set_state(BookingStates.name)
    await message.answer(
        "📅 *Booking a session with Anna*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Step 1 of 3  ●○○\n\n"
        "What's your name? 👤",
        parse_mode="Markdown",
        reply_markup=booking_cancel_menu,
    )


@router.message(F.text == "🚫 Cancel Booking")
async def booking_cancel_reply(message: Message, state: FSMContext) -> None:
    """Handle cancel button press at any step of the booking form."""
    await state.clear()
    await message.answer(
        "No worries! Booking cancelled. 😊\n"
        "_You can start again anytime._",
        parse_mode="Markdown",
        reply_markup=main_menu,
    )


# ── Step 2: Collect name ──────────────────────────────────────────────────────

@router.message(BookingStates.name)
async def booking_get_name(message: Message, state: FSMContext) -> None:
    """Save the name and ask for the coaching request."""
    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(BookingStates.request)

    await message.answer(
        f"Nice to meet you, *{name}!* 👋\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Step 2 of 3  ●●○\n\n"
        "What would you like to work on with Anna?\n"
        "_Describe your situation and goal:_ 📝",
        parse_mode="Markdown",
        reply_markup=booking_cancel_menu,
    )


# ── Step 3: Collect request description ──────────────────────────────────────

@router.message(BookingStates.request)
async def booking_get_request(message: Message, state: FSMContext) -> None:
    """Save the request and ask for contact details."""
    await state.update_data(request=message.text.strip())
    await state.set_state(BookingStates.contact)

    await message.answer(
        "Almost there! 🙌\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Step 3 of 3  ●●●\n\n"
        "How can Anna reach you?\n"
        "_Phone number or Telegram @username:_ 📞",
        parse_mode="Markdown",
        reply_markup=booking_cancel_menu,
    )


# ── Step 4: Collect contact + show summary ────────────────────────────────────

@router.message(BookingStates.contact)
async def booking_get_contact(message: Message, state: FSMContext) -> None:
    """Save the contact and show a booking summary for confirmation."""
    await state.update_data(contact=message.text.strip())
    await state.set_state(BookingStates.confirm)

    data = await state.get_data()
    summary = (
        "📋 *Booking Summary*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤  *Name:*      {data['name']}\n"
        f"📝  *Request:*   {data['request']}\n"
        f"📞  *Contact:*   {data['contact']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_Submit this request to Anna?_"
    )

    await message.answer(
        text=summary,
        parse_mode="Markdown",
        reply_markup=booking_confirm,
    )


# ── Step 5a: Confirmed ────────────────────────────────────────────────────────

@router.callback_query(BookingStates.confirm, F.data == "booking_confirm")
async def booking_confirmed(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Save booking to Google Sheets, notify owner, and thank the client."""
    await callback.answer()
    data = await state.get_data()
    await state.clear()

    name = data["name"]
    request = data["request"]
    contact = data["contact"]

    # Save to Google Sheets (graceful failure — bot continues if Sheets is not configured)
    saved = sheets.save_booking(name=name, request=request, contact=contact)
    if not saved:
        logger.warning("Booking saved locally but could not write to Google Sheets.")

    # Track stats
    record_booking()
    record_user(callback.from_user.id)

    # Notify the bot owner
    await notifications.notify_owner(bot=bot, name=name, request=request, contact=contact)

    await callback.message.answer(
        f"🎉 *You're all set, {name}!*\n\n"
        "Your request has been sent to Anna.\n"
        "She'll reach out within *24 hours* ⏰\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_While you wait — feel free to ask me\n"
        "anything about your career!_ 💬",
        parse_mode="Markdown",
        reply_markup=main_menu,
    )


# ── Step 5b: Cancelled ────────────────────────────────────────────────────────

@router.callback_query(BookingStates.confirm, F.data == "booking_cancel")
async def booking_cancelled(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel the booking and return to the main menu."""
    await callback.answer()
    await state.clear()

    await callback.message.answer(
        "No worries! Request cancelled. 😊\n"
        "_You can book anytime you're ready._",
        parse_mode="Markdown",
        reply_markup=main_menu,
    )
