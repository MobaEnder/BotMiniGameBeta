# cogs/lodemienbac.py

import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

USER_FILE = "data/users.json"

def load_users():
	if not os.path.exists(USER_FILE):
		with open(USER_FILE, "w") as f:
			json.dump({}, f)
	with open(USER_FILE, "r") as f:
		return json.load(f)

def save_users(data):
	with open(USER_FILE, "w") as f:
		json.dump(data, f, indent=4)

def get_user_data(user_id):
	data = load_users()
	return data.get(str(user_id), {})

def get_lode_cooldown(user_id):
	user = get_user_data(user_id)
	last_time = datetime.fromisoformat(user.get("last_lode", "1970-01-01T00:00:00"))
	time_passed = datetime.utcnow() - last_time
	cooldown = timedelta(minutes=1)
	return None if time_passed >= cooldown else cooldown - time_passed

class Lode(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="lodemienbac", description="🎯 Đoán số từ 1-10, có 3 lần đoán. Trúng x4 số tiền!")
	@app_commands.describe(
		bet="Số tiền bạn muốn cược",
		so1="Số đầu tiên bạn chọn (1-10)",
		so2="Số thứ hai bạn chọn (1-10)",
		so3="Số thứ ba bạn chọn (1-10)"
	)
	async def lodemienbac(
		self,
		interaction: discord.Interaction,
		bet: int,
		so1: int,
		so2: int,
		so3: int
	):
		await interaction.response.defer()

		user = interaction.user
		user_id = str(user.id)
		users = load_users()

		if user_id not in users:
			await interaction.followup.send("❌ Bạn chưa có tài khoản!", ephemeral=True)
			return

		if not all(1 <= s <= 10 for s in [so1, so2, so3]):
			await interaction.followup.send("❌ Bạn chỉ được chọn số từ 1 đến 10!", ephemeral=True)
			return

		cd = get_lode_cooldown(user.id)
		if cd:
			mins, secs = divmod(int(cd.total_seconds()), 60)
			return await interaction.followup.send(
				f"🕓 Bạn cần chờ {mins} phút {secs} giây nữa để chơi tiếp!", ephemeral=True
			)

		user_data = users[user_id]
		if user_data.get("money", 0) < bet:
			await interaction.followup.send("💸 Bạn không đủ tiền để cược!", ephemeral=True)
			return

		user_data["money"] -= bet
		user_data["last_lode"] = datetime.utcnow().isoformat()
		save_users(users)

		spin_msg = await interaction.followup.send("🎰 Đang quay số Miền Bắc...")
		await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=3))

		result = random.randint(1, 10)
		emojis = ["🍉", "🍋", "🌟", "🍓", "🎯", "🍇", "🍀", "🎈", "💎", "🔥"]
		spin_text = ""

		for i in range(10):
			spin_text += f"🎲 {random.randint(1, 10)} {random.choice(emojis)}\n"
			await spin_msg.edit(content=f"🔄 Quay số...\n{spin_text}")
			await discord.utils.sleep_until(datetime.utcnow() + timedelta(milliseconds=500))

		win = result in [so1, so2, so3]
		if win:
			won = bet * 4
			user_data["money"] += won
			save_users(users)
			await spin_msg.edit(content=(
				f"🎉 Kết quả: **{result} {random.choice(emojis)}**\n"
				f"✅ Bạn đã đoán trúng! Nhận được **🪙 {won:,} xu**!"
			))
		else:
			await spin_msg.edit(content=(
				f"🎯 Kết quả: **{result} {random.choice(emojis)}**\n"
				f"❌ Rất tiếc, bạn đã đoán sai!"
			))

async def setup(bot):
	await bot.add_cog(Lode(bot))
