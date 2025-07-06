import os
from dotenv import load_dotenv

env = os.getenv("ENV", "docker").lower()
env_file = {
    "local": ".env.local",
    "docker": ".env.docker",
    "prod": ".env.production"
}.get(env, ".env.docker")
load_dotenv(env_file)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
BOT_ROOT = os.getenv("BOT_ROOT_PATH", os.getcwd())
