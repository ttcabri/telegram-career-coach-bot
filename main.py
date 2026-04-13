"""
main.py — Entry point for the Telegram Career Coach Bot.

Run with: python main.py
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, TelegramObject

import config
from handlers import ai_chat, booking, commands, info, start
from services.guard import check_flood

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class FloodMiddleware(BaseMiddleware):
    """Drop messages that arrive too fast from the same user (flood control)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            result = check_flood(event.from_user.id)
            if not result.allowed:
                # Silently drop the message — no response to flooder
                return
        return await handler(event, data)


async def main() -> None:
    # Validate that all required environment variables are set
    config.validate_config()

    # Initialize bot and dispatcher with in-memory FSM storage
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Flood protection middleware (runs before any handler)
    dp.message.middleware(FloodMiddleware())

    # Register all routers (order matters — more specific handlers first)
    dp.include_router(commands.router)
    dp.include_router(start.router)
    dp.include_router(info.router)
    dp.include_router(booking.router)
    dp.include_router(ai_chat.router)

    logger.info("Bot is starting...")

    try:
        # Drop pending updates so the bot starts fresh
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
