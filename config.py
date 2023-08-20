import os
from os import path
from dotenv import load_dotenv

if path.exists('config.env'):
    load_dotenv("config.env")

API_ID = int(os.getenv('API_ID'))  
API_HASH = str(os.getenv("API_HASH"))
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
START_IMG = str(os.getenv('START_IMG'))
MONGO_DB_URL = str(os.getenv("MONGO_DB_URL"))
WAIFU_CHANNEL = int(os.getenv("WAIFU_CHANNEL"))
GODS = list(os.getenv('GODS').split(" "))