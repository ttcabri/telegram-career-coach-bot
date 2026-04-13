"""
services/guard.py — Bot protection layer.

Handles:
  - Per-user daily rate limiting for AI queries
  - Message content filtering (too short, too long, repeated, jailbreak)
  - Flood control (too many messages too fast)
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto


# ── Config ────────────────────────────────────────────────────────────────────

AI_DAILY_LIMIT = 5          # max AI questions per user per day
MIN_MESSAGE_LEN = 5         # chars
MAX_MESSAGE_LEN = 500       # chars
FLOOD_INTERVAL = 2.0        # seconds between allowed messages

# Prompt injection / jailbreak patterns (case-insensitive)
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "forget your instructions",
    "disregard your instructions",
    "override your instructions",
    "you are now",
    "pretend you are",
    "act as if you are",
    "act as a",
    "jailbreak",
    "system prompt",
    "bypass",
    "dan mode",
    "developer mode",
    "do anything now",
]


# ── Filter result ─────────────────────────────────────────────────────────────

class BlockReason(Enum):
    TOO_SHORT = auto()
    TOO_LONG = auto()
    REPEATED = auto()
    INJECTION = auto()
    RATE_LIMITED = auto()
    FLOOD = auto()


@dataclass
class GuardResult:
    allowed: bool
    reason: BlockReason | None = None
    remaining_today: int | None = None  # only set for RATE_LIMITED


# ── Internal state (in-memory, resets on bot restart) ─────────────────────────

# { user_id: {"date": date, "count": int} }
_rate_data: dict = defaultdict(lambda: {"date": None, "count": 0})

# { user_id: last_message_text }
_last_message: dict[int, str] = {}

# { user_id: last_message_timestamp }
_last_time: dict[int, float] = {}


# ── Public API ────────────────────────────────────────────────────────────────

def check_flood(user_id: int) -> GuardResult:
    """
    Allow at most one message per FLOOD_INTERVAL seconds per user.
    Call this for every incoming message (not just AI queries).
    """
    now = time.monotonic()
    last = _last_time.get(user_id, 0)
    _last_time[user_id] = now

    if now - last < FLOOD_INTERVAL:
        return GuardResult(allowed=False, reason=BlockReason.FLOOD)
    return GuardResult(allowed=True)


def check_ai_message(user_id: int, text: str) -> GuardResult:
    """
    Full guard check for an AI query:
      1. Content filters (short / long / repeated / injection)
      2. Daily rate limit
    Returns GuardResult with details on why it was blocked.
    """
    # 1. Too short
    if len(text.strip()) < MIN_MESSAGE_LEN:
        return GuardResult(allowed=False, reason=BlockReason.TOO_SHORT)

    # 2. Too long
    if len(text) > MAX_MESSAGE_LEN:
        return GuardResult(allowed=False, reason=BlockReason.TOO_LONG)

    # 3. Repeated message
    if _last_message.get(user_id) == text.strip():
        return GuardResult(allowed=False, reason=BlockReason.REPEATED)

    # 4. Prompt injection keywords
    lower = text.lower()
    if any(pattern in lower for pattern in INJECTION_PATTERNS):
        return GuardResult(allowed=False, reason=BlockReason.INJECTION)

    # 5. Daily rate limit
    today = date.today()
    record = _rate_data[user_id]
    if record["date"] != today:
        record["date"] = today
        record["count"] = 0

    if record["count"] >= AI_DAILY_LIMIT:
        return GuardResult(
            allowed=False,
            reason=BlockReason.RATE_LIMITED,
            remaining_today=0,
        )

    # ✅ All checks passed — record the message and increment counter
    record["count"] += 1
    _last_message[user_id] = text.strip()

    remaining = AI_DAILY_LIMIT - record["count"]
    return GuardResult(allowed=True, remaining_today=remaining)


def get_remaining(user_id: int) -> int:
    """Return how many AI questions this user has left today."""
    today = date.today()
    record = _rate_data[user_id]
    if record["date"] != today:
        return AI_DAILY_LIMIT
    return max(0, AI_DAILY_LIMIT - record["count"])
