# cogs/economy.py
import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import datetime, timedelta
import motor.motor_asyncio

# MongoDB setup
MONGO_URI = os.getenv("MONGODB_URI")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
mongo_db = mongo_client["bot"]
mongo_users = mongo_db["users"]

# Cooldown file cho daily
DAILY_COOLDOWN_FILE = "data/daily_cooldown.json"

def load_daily_cooldown():
    if not os.path.exists(DAILY_COOLDOWN_FILE):
        with open(DAILY_COOLDOWN_FILE, "w") as f:
            json.dump({}, f)
    with open(DAILY_COOLDOWN_FILE, "r") as f:
        return json.load(f)

def save_daily_cooldown(data):
    with open(DAILY_COOLDOWN_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Lấy số dư từ MongoDB
async def get_balance(user_id):
    user_id = str(user_id)
    user_data = await mongo_users.find_one({"_id": user_id})
    if not user_data:
        await mongo_users.insert_one({"_id": user_id, "money": 0})
        return 0
    return user_data.get("money", 0)

# Cộng tiền vào tài khoản
async def add_money(user_id, amount):
    user_id = str(user_id)
    user_data = await mongo_users.find_one({"_id": user_id})
    if not user_data:
        await mongo_users.insert_one({"_id": user_id, "money": amount})
        return amount
    new_balance = user_data.get("money", 0) + amount
    await mongo_users.update_one({"_id": user_id}, {"$set": {"money": new_balance}})
    return new_balance

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="Nhận phần thưởng hàng ngày!")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        cooldown_data = load_daily_cooldown()
        now = datetime.utcnow()

        if user_id in cooldown_data:
            last_claimed = datetime.strptime(cooldown_data[user_id], "%Y-%m-%d %H:%M:%S")
            if now < last_claimed + timedelta(hours=24):
                remaining = (last_claimed + timedelta(hours=24)) - now
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                return await interaction.response.send_message(
                    f"📆 Bạn đã nhận quà hôm nay rồi!\nHãy quay lại sau **{hours} giờ {minutes} phút** nữa.",
                    ephemeral=True
                )

        # Thưởng hàng ngày
        reward = 1000
        new_balance = await add_money(user_id, reward)
        cooldown_data[user_id] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_daily_cooldown(cooldown_data)

        await interaction.response.send_message(
            f"🎁 Bạn đã nhận được **{reward} xu** hôm nay!\n💰 Số dư hiện tại: **{new_balance} xu**"
        )

    @app_commands.command(name="balance", description="Xem số dư của bạn.")
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        balance = await get_balance(user_id)
        await interaction.response.send_message(
            f"💳 Số dư hiện tại của bạn là: **{balance} xu**"
        )

async def setup(bot):
    await bot.add_cog(Economy(bot))
