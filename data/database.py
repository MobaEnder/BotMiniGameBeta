# database.py
import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["discord_bot"]  # Tên database, bạn có thể đổi
users_col = db["users"]
level_col = db["levels"]
dig_cooldown_col = db["dig_cooldowns"]
