import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data/users.json"

MINER_COOLDOWN = 3600  # 1 giờ

ORES = [
		{"name": "🪨 Đá", "value": 5, "rarity": "common", "weight": 40},
		{"name": "⛏️ Than đá", "value": 15, "rarity": "common", "weight": 30},
		{"name": "🪙 Sắt", "value": 30, "rarity": "uncommon", "weight": 15},
		{"name": "🔋 Đồng", "value": 50, "rarity": "uncommon", "weight": 7},
		{"name": "💎 Kim cương", "value": 150, "rarity": "rare", "weight": 4},
		{"name": "🧪 Ngọc huyền bí", "value": 300, "rarity": "epic", "weight": 2},
]

FAIL_CHANCE = 0.1  # 10% tỉ lệ đào trượt

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
				data[uid] = {
						"money": 0,
						"last_mine": "1970-01-01T00:00:00"
				}
				save_data(data)
		return data[uid]

def update_user(user_id, key, value):
		data = load_data()
		uid = str(user_id)
		user = get_user(user_id)
		user[key] = value
		data[uid] = user
		save_data(data)

def update_money(user_id, amount):
		data = load_data()
		uid = str(user_id)
		user = get_user(user_id)
		user["money"] += amount
		data[uid] = user
		save_data(data)
		return user["money"]

def can_mine(user_id):
		user = get_user(user_id)
		last_time = datetime.fromisoformat(user.get("last_mine", "1970-01-01T00:00:00"))
		return datetime.utcnow() - last_time >= timedelta(seconds=MINER_COOLDOWN)

class Mining(commands.Cog):
		def __init__(self, bot):
				self.bot = bot

		@app_commands.command(name="miner", description="Đào quặng để kiếm tiền! Có thể tìm thấy kho báu!")
		async def miner(self, interaction: discord.Interaction):
				user = get_user(interaction.user.id)

				if not can_mine(interaction.user.id):
						return await interaction.response.send_message(
								"⛏️ Bạn đã đào gần đây rồi! Hãy nghỉ ngơi trước khi quay lại (cooldown 1h).",
								ephemeral=True
						)

				update_user(interaction.user.id, "last_mine", datetime.utcnow().isoformat())

				if random.random() < FAIL_CHANCE:
						return await interaction.response.send_message("💥 Bạn đào trúng mỏ trống và không tìm thấy gì!")

				ore = random.choices(
						ORES,
						weights=[o["weight"] for o in ORES],
						k=1
				)[0]

				new_balance = update_money(interaction.user.id, ore["value"])

				rarity_note = f"🌟 Đây là quặng **{ore['rarity']}**!" if ore["rarity"] != "common" else ""
				await interaction.response.send_message(
						f"⛏️ Bạn đã đào được {ore['name']} và bán với giá **{ore['value']} xu**!\n"
						f"{rarity_note}\n"
						f"💰 Số dư hiện tại: {new_balance} xu."
				)

async def setup(bot):
		await bot.add_cog(Mining(bot))
