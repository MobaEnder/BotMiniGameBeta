import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data/users.json"

def load_data():
	if not os.path.exists(DATA_FILE):
		with open(DATA_FILE, "w") as f:
			json.dump({}, f)
	with open(DATA_FILE, "r") as f:
		return json.load(f)

def save_data(data):
	with open(DATA_FILE, "w") as f:
		json.dump(data, f, indent=4)

def get_user(user_id):
	data = load_data()
	user_id = str(user_id)
	if user_id not in data:
		data[user_id] = {
			"money": 0,
			"last_daily": "1970-01-01T00:00:00",
			"last_work": "1970-01-01T00:00:00"
		}
		save_data(data)
	return data[user_id]

def get_balance(user_id):
	user = get_user(user_id)
	return user.get("money", 0)

def update_balance(user_id, amount):
	data = load_data()
	user_id = str(user_id)
	user = get_user(user_id)
	user["money"] += amount
	data[user_id] = user
	save_data(data)
	return user["money"]

def set_last_time(user_id, key):
	data = load_data()
	user_id = str(user_id)
	user = get_user(user_id)
	user[key] = datetime.utcnow().isoformat()
	data[user_id] = user
	save_data(data)

def can_use_command(user_id, key, cooldown_hours):
	last_time_str = get_user(user_id).get(key, "1970-01-01T00:00:00")
	last_time = datetime.fromisoformat(last_time_str)
	return datetime.utcnow() - last_time >= timedelta(hours=cooldown_hours)

# ---------------------- Discord Cog ----------------------

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="daily", description="Nhận tiền thưởng hàng ngày")
	async def daily(self, interaction: discord.Interaction):
		if not can_use_command(interaction.user.id, "last_daily", 24):
			await interaction.response.send_message(
				"🕒 Bạn đã nhận thưởng hôm nay rồi, hãy quay lại sau 24 giờ!",
				ephemeral=True
			)
			return

		reward = random.randint(50, 150)
		update_balance(interaction.user.id, reward)
		set_last_time(interaction.user.id, "last_daily")
		balance = get_balance(interaction.user.id)

		await interaction.response.send_message(
			f"🎁 Bạn đã nhận được **{reward} xu** hôm nay!\n"
			f"💰 Số dư hiện tại của bạn là **{balance} xu**."
		)

	@app_commands.command(name="balance", description="Xem số dư hiện tại của bạn")
	async def balance(self, interaction: discord.Interaction):
		balance = get_balance(interaction.user.id)
		await interaction.response.send_message(
			f"💰 Số dư của bạn là **{balance} xu**."
		)

async def setup(bot):
	await bot.add_cog(Economy(bot))
