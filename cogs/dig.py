# cogs/dig.py
import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
from datetime import datetime, timedelta
import motor.motor_asyncio

# MongoDB setup
MONGO_URI = os.getenv("MONGODB_URI")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
mongo_db = mongo_client["bot"]
mongo_users = mongo_db["users"]

# Cooldown file
COOLDOWN_FILE = "data/dig_cooldown.json"

def load_cooldown():
    if not os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, "w") as f:
            json.dump({}, f)
    with open(COOLDOWN_FILE, "r") as f:
        return json.load(f)

def save_cooldown(data):
    with open(COOLDOWN_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Hàm cập nhật tiền bằng MongoDB
async def update_money_mongo(user_id, amount):
    user_id = str(user_id)
    user_data = await mongo_users.find_one({"_id": user_id})
    if not user_data:
        await mongo_users.insert_one({"_id": user_id, "money": 0})
        user_data = {"money": 0}
    new_money = user_data["money"] + amount
    await mongo_users.update_one({"_id": user_id}, {"$set": {"money": new_money}})
    return new_money

class Dig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dig", description="Đào kho báu để kiếm xu!")
    async def dig(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        cooldown_data = load_cooldown()
        now = datetime.utcnow()

        if user_id in cooldown_data:
            last_used = datetime.strptime(cooldown_data[user_id], "%Y-%m-%d %H:%M:%S")
            if now < last_used + timedelta(minutes=20):
                remaining = (last_used + timedelta(minutes=20)) - now
                minutes = remaining.seconds // 60
                seconds = remaining.seconds % 60
                return await interaction.response.send_message(
                    f"⛏️ Bạn cần chờ **{minutes} phút {seconds} giây** nữa để đào tiếp.",
                    ephemeral=True
                )

        # Tạo phần thưởng
        reward = random.randint(100, 500)
        new_balance = await update_money_mongo(user_id, reward)

        cooldown_data[user_id] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_cooldown(cooldown_data)

        await interaction.response.send_message(
            f"🏝️ Bạn đã đào được **{reward} xu**!\n💰 Số dư hiện tại: **{new_balance} xu**"
        )

async def setup(bot):
    await bot.add_cog(Dig(bot))
