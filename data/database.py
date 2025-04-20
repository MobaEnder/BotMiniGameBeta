# data/database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["test"]  # tên database bạn đặt bên Railway
users_collection = db["users"]  # tên collection đã tạo sẵn

# Hàm lấy thông tin người dùng
def get_user(user_id):
    user = users_collection.find_one({"_id": str(user_id)})
    if user is None:
        user = {
            "_id": str(user_id),
            "balance": 0,
            "xp": 0,
            "level": 1,
            "quote": "",
        }
        users_collection.insert_one(user)
    return user

# Hàm cập nhật thông tin người dùng
def update_user(user_id, update_data):
    users_collection.update_one({"_id": str(user_id)}, {"$set": update_data})
