import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_PLAN = "free"

PLANS = {
    "free": {"name": "FREE"},
    "plus": {"name": "PLUS", "price": 8},
    "pro": {"name": "PRO", "price": 18}
}
