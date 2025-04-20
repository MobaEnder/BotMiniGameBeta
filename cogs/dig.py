# cogs/dig.py
import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import asyncio
from datetime import datetime, timedelta

DATA_FILE = "data/users.json"
COOLDOWN_FILE = "data/dig_cooldown.json"

def load_data():
		if not os.path.exists(DATA_FILE):
				with open(DATA_FILE, "w") as f:
						json.dump({}, f)
		with open(DATA_FILE, "r") as f:
				return json.load(f)

def save_data(data):
		with open(DATA_FILE, "w") as f:
				json.dump(data, f, indent=4)

def update_money(user_id, amount):
		data = load_data()
		user_id = str(user_id)
		if user_id not in data:
				data[user_id] = {"money": 0}
		data[user_id]["money"] += amount
		save_data(data)
		return data[user_id]["money"]

def load_cooldown():
		if not os.path.exists(COOLDOWN_FILE):
				with open(COOLDOWN_FILE, "w") as f:
						json.dump({}, f)
		with open(COOLDOWN_FILE, "r") as f:
				return json.load(f)

def save_cooldown(data):
		with open(COOLDOWN_FILE, "w") as f:
				json.dump(data, f, indent=4)

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
										f"⛏️ Bạn cần chờ **{minutes} phút {seconds} giây** nữa để đào tiếp.", ephemeral=True
								)

				# Tạo phần thưởng
				reward = random.randint(100, 500)
				new_balance = update_money(user_id, reward)

				cooldown_data[user_id] = now.strftime("%Y-%m-%d %H:%M:%S")
				save_cooldown(cooldown_data)

				await interaction.response.send_message(
						f"🏝️ Bạn đã đào được **{reward} xu**!\n💰 Số dư hiện tại: **{new_balance} xu**"
				)

async def setup(bot):
		await bot.add_cog(Dig(bot))
