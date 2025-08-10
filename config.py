import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
BOT_NAME = os.getenv("BOT_NAME")
IMGUR_BASE_URL = os.getenv("IMGUR_BASE_URL")
DEFAULT_PROFILE_IMAGE = os.getenv("DEFAULT_PROFILE_IMAGE")