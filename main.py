import discord
from discord.ext import commands
import asyncio
import os
import json

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Đảm bảo thư mục data tồn tại
LEVEL_DIR = "data"
LEVEL_FILE = os.path.join(LEVEL_DIR, "level.json")

# Tạo thư mục và tệp nếu chưa tồn tại
if not os.path.exists(LEVEL_DIR):
    os.makedirs(LEVEL_DIR)

if not os.path.exists(LEVEL_FILE):
    with open(LEVEL_FILE, "w") as f:
        json.dump({}, f)

# Load và lưu dữ liệu level
def load_level_data():
    with open(LEVEL_FILE, "r") as f:
        return json.load(f)

def save_level_data(data):
    with open(LEVEL_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Cộng EXP và xử lý lên cấp
def add_exp(user_id, amount=30):
    uid = str(user_id)
    data = load_level_data()

    if uid not in data:
        data[uid] = {"level": 1, "xp": 0}

    user = data[uid]
    user["xp"] += amount

    # Tăng cấp nếu đạt 600 xp
    while user["xp"] >= 600:
        user["xp"] -= 600
        user["level"] += 1

    # Đảm bảo không bị tụt cấp
    if user["level"] < 1:
        user["level"] = 1

    data[uid] = user
    save_level_data(data)

# Cộng EXP khi người dùng sử dụng bất kỳ slash command nào
@bot.listen("on_app_command_completion")
async def on_command_used(interaction, command):
    if interaction.user:
        add_exp(interaction.user.id)

@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Slash commands synced: {len(synced)} lệnh.")
    except Exception as e:
        print("Lỗi sync:", e)

async def main():
    async with bot:
        # Load các cogs
        cogs = [
            "cogs.baucua", "cogs.economy", "cogs.leaderboard", "cogs.transfer",
            "cogs.jobs", "cogs.help", "cogs.profile", "cogs.fishing",
            "cogs.miner", "cogs.taixiu_low", "cogs.taixiu_big", "cogs.rank",
            "cogs.level_system", "cogs.ping", "cogs.dig", "cogs.race",
            "cogs.xungxeng", "cogs.lodemienbac", "cogs.snakegame", "cogs.goboms",
            "cogs.chickenfight_low", "cogs.chickenfight_big", "cogs.bongda"
        ]
        for cog in cogs:
            try:
                await bot.load_extension(cog)
                print(f"Loaded cog: {cog}")
            except Exception as e:
                print(f"Failed to load cog {cog}: {e}")

        # Kiểm tra token trước khi khởi động
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN environment variable is not set!")
        await bot.start(token)

# Chạy bot
asyncio.run(main())
