import discord
from discord.ext import commands
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

LEVEL_FILE = "data/level.json"

# Load và lưu dữ liệu level
def load_level_data():
		if not os.path.exists(LEVEL_FILE):
				with open(LEVEL_FILE, "w") as f:
						json.dump({}, f)
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
				await bot.load_extension("cogs.baucua")
				await bot.load_extension("cogs.economy")
				await bot.load_extension("cogs.leaderboard")
				await bot.load_extension("cogs.transfer")
				await bot.load_extension("cogs.jobs")
				await bot.load_extension("cogs.help")
				await bot.load_extension("cogs.profile")
				await bot.load_extension("cogs.fishing")
				await bot.load_extension("cogs.miner")
				await bot.load_extension("cogs.taixiu_low")
				await bot.load_extension("cogs.taixiu_big")
				await bot.load_extension("cogs.rank")
				await bot.load_extension("cogs.level_system")
				await bot.load_extension("cogs.ping")
				await bot.load_extension("cogs.dig")
				await bot.load_extension("cogs.race")
				await bot.load_extension("cogs.xungxeng")
				await bot.load_extension("cogs.lodemienbac")
				await bot.load_extension("cogs.snakegame")
				await bot.load_extension("cogs.goboms")
				await bot.load_extension("cogs.chickenfight_low")
				await bot.load_extension("cogs.chickenfight_big")
				await bot.load_extension("cogs.bongda")
				await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
