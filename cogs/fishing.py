import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data/users.json"

FISH_TYPES = [
	{"name": "🐟 Cá thường", "value": 10},
	{"name": "🐠 Cá nhiệt đới", "value": 20},
	{"name": "🦑 Mực", "value": 30},
	{"name": "🦀 Cua", "value": 25},
	{"name": "🐬 Cá heo (hiếm)", "value": 80, "rarity": "rare"},
	{"name": "🦈 Cá mập (siêu hiếm)", "value": 150, "rarity": "epic"},
	{"name": "🐉 Cá thần thoại (huyền thoại)", "value": 500, "rarity": "legendary"},
]

RANDOM_EVENTS = [
	{"message": "🌧️ Trời mưa, cá ít xuất hiện hơn...", "modifier": 0.8},
	{"message": "🌞 Trời nắng đẹp, cá xuất hiện nhiều hơn!", "modifier": 1.2},
	{"message": "💥 Bạn vô tình làm rơi cần câu, mất một ít thời gian!", "modifier": 0.5},
	{"message": "🍀 May mắn! Bạn thấy một đàn cá bơi qua!", "modifier": 1.5},
]

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
	uid = str(user_id)
	if uid not in data:
		data[uid] = {"money": 0, "last_fish": "1970-01-01T00:00:00"}
		save_data(data)
	return data[uid]

def update_money(user_id, amount):
	data = load_data()
	uid = str(user_id)
	user = get_user(user_id)
	user["money"] += amount
	data[uid] = user
	save_data(data)
	return user["money"]

def can_fish(user_id):
	user = get_user(user_id)
	last_time = datetime.fromisoformat(user.get("last_fish", "1970-01-01T00:00:00"))
	return datetime.utcnow() - last_time >= timedelta(hours=1)

def update_last_fish(user_id):
	data = load_data()
	uid = str(user_id)
	user = get_user(user_id)
	user["last_fish"] = datetime.utcnow().isoformat()
	data[uid] = user
	save_data(data)

class Fishing(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="fish", description="Câu cá để kiếm tiền và tìm cá hiếm!")
	async def fish(self, interaction: discord.Interaction):
		if not can_fish(interaction.user.id):
			return await interaction.response.send_message(
				"🕒 Bạn vừa câu cá gần đây! Hãy thử lại sau **1 giờ**.", ephemeral=True
			)

		event = random.choice(RANDOM_EVENTS)
		modifier = event["modifier"]

		fish = random.choices(
			FISH_TYPES,
			weights=[60, 30, 20, 20, 7, 2, 1],
			k=1
		)[0]

		final_value = int(fish["value"] * modifier)
		new_balance = update_money(interaction.user.id, final_value)
		update_last_fish(interaction.user.id)

		rarity_note = ""
		if "rarity" in fish:
			rarity_note = f"🎉 Bạn đã bắt được cá **{fish['rarity']}**!"

		await interaction.response.send_message(
			f"{event['message']}\n"
			f"🎣 Bạn câu được {fish['name']} và bán được **{final_value} xu**!\n"
			f"{rarity_note}\n"
			f"💰 Số dư hiện tại: {new_balance} xu."
		)

async def setup(bot):
	await bot.add_cog(Fishing(bot))
