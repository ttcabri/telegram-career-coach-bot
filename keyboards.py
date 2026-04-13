"""
keyboards.py — All keyboard definitions in one place.
Keeps handler code clean and keyboards easy to update.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ── Reply Keyboard (persistent bottom menu) ──────────────────────────────────

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Services"),
            KeyboardButton(text="💰 Prices"),
        ],
        [
            KeyboardButton(text="📅 Book Now"),
            KeyboardButton(text="💬 Ask AI"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an option or type a message...",
)

# ── Inline Keyboards ──────────────────────────────────────────────────────────

# "Back to menu" button shown after info pages
back_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
)

# Booking confirmation — shown after user enters all details
booking_confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm Booking", callback_data="booking_confirm"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="booking_cancel"),
        ]
    ]
)

# Keyboard shown during booking steps — single escape button
booking_cancel_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚫 Cancel Booking")]],
    resize_keyboard=True,
    input_field_placeholder="Type your answer or cancel...",
)

# "Back to menu" shown after AI response
ai_back_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_menu")],
        [InlineKeyboardButton(text="💬 Ask Another Question", callback_data="ask_again")],
    ]
)
