from pymongo import MongoClient
import os
from datetime import datetime

# Lấy URI từ biến môi trường hoặc chỉnh URI thẳng ở đây
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["test"]
collection = db["users"]

def get_user(user_id):
    user = collection.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "money": 0,
            "last_daily": "1970-01-01T00:00:00",
            "last_work": "1970-01-01T00:00:00",
            "exp": 0,
            "level": 1
        }
        collection.insert_one(user)
    return user

def get_balance(user_id):
    user = get_user(user_id)
    return user.get("money", 0)

def update_balance(user_id, amount):
    user = get_user(user_id)
    new_balance = max(0, user.get("money", 0) + amount)
    collection.update_one({"_id": user_id}, {"$set": {"money": new_balance}})
    return new_balance

def set_last_time(user_id, key, time_str):
    user = get_user(user_id)
    collection.update_one({"_id": user_id}, {"$set": {key: time_str}})

def get_last_time(user_id, key):
    user = get_user(user_id)
    return user.get(key, "1970-01-01T00:00:00")

def add_exp(user_id, amount):
    user = get_user(user_id)
    exp = user.get("exp", 0) + amount
    level = user.get("level", 1)
    next_level_exp = 100 * level

    while exp >= next_level_exp:
        exp -= next_level_exp
        level += 1
        next_level_exp = 100 * level

    collection.update_one(
        {"_id": user_id},
        {"$set": {"exp": exp, "level": level}}
    )
    return exp, level

def get_level_info(user_id):
    user = get_user(user_id)
    exp = user.get("exp", 0)
    level = user.get("level", 1)
    next_level_exp = 100 * level
    return {"level": level, "exp": exp, "next_level_exp": next_level_exp}
