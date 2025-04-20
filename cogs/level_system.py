import discord
from discord.ext import commands
import json
import os

LEVEL_DIR = "data"
LEVEL_FILE = os.path.join(LEVEL_DIR, "level.json")

# Tạo thư mục/tệp nếu chưa có
if not os.path.exists(LEVEL_DIR):
    os.makedirs(LEVEL_DIR)
if not os.path.exists(LEVEL_FILE):
    with open(LEVEL_FILE, "w") as f:
        json.dump({}, f)

def load_level_data():
    with open(LEVEL_FILE, "r") as f:
        return json.load(f)

def save_level_data(data):
    with open(LEVEL_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_exp(user_id, amount=30):
    uid = str(user_id)
    data = load_level_data()

    if uid not in data:
        data[uid] = {"level": 1, "xp": 0}

    user = data[uid]
    user["xp"] += amount

    while user["xp"] >= 600:
        user["xp"] -= 600
        user["level"] += 1

    if user["level"] < 1:
        user["level"] = 1

    data[uid] = user
    save_level_data(data)

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        if interaction.user:
            add_exp(interaction.user.id)

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
