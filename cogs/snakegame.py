# cogs/snakegame.py

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
import json
import os
import asyncio

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

def get_snake_cooldown(user_id):
	data = load_users()
	user = data.get(str(user_id), {})
	last_time = user.get("last_snake", "1970-01-01T00:00:00")
	last_time = datetime.fromisoformat(last_time)
	now = datetime.utcnow()
	cooldown = timedelta(minutes=0)
	if now - last_time >= cooldown:
		return None
	return cooldown - (now - last_time)

class SnakeGame(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="snakegame", description="🐍 Rắn leo thang - cược càng cao càng lời!")
	@app_commands.describe(amount="Số tiền muốn đặt cược")
	async def snakegame(self, interaction: discord.Interaction, amount: int):
		await interaction.response.defer()
		user = interaction.user
		data = load_users()
		uid = str(user.id)

		if uid not in data:
			await interaction.followup.send("❌ Bạn chưa có tài khoản!", ephemeral=True)
			return

		cooldown = get_snake_cooldown(uid)
		if cooldown:
			m, s = divmod(int(cooldown.total_seconds()), 60)
			await interaction.followup.send(
				f"⏳ Bạn cần chờ {m} phút {s} giây nữa để chơi tiếp.", ephemeral=True)
			return

		if amount <= 0:
			await interaction.followup.send("❌ Số tiền cược phải lớn hơn 0!", ephemeral=True)
			return

		if data[uid]["money"] < amount:
			await interaction.followup.send("❌ Bạn không đủ tiền để chơi!", ephemeral=True)
			return

		stages = ["🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟥", "💀"]
		result = []
		total = amount
		step_count = 0

		msg = await interaction.followup.send(f"🐍 **Rắn bắt đầu leo...**\n💰 Tiền hiện tại: 🪙 {total:,} xu")

		for i in range(1, 9):
			await asyncio.sleep(1.5)
			step = random.choice(stages)

			if step == "🟥" or step == "💀":
				result.append(f"{step} **Bậc {i}: Rớt xuống! Mất trắng!** 💀")
				total = 0
				data[uid]["money"] -= amount
				break
			else:
				total *= 2
				step_count += 1
				result.append(f"🟩 **Bậc {i} thành công!** 🐍 💸 Tiền: 🪙 {total:,} xu")

				view = ContinueOrStopView()
				await msg.edit(content="\n".join(result) + f"\n\n⏳ **Muốn tiếp tục hay dừng lại?**", view=view)

				try:
					await view.wait()
				except:
					pass

				if view.choice == "stop" or view.choice is None:
					result.append("🛑 **Bạn đã dừng lại.** ✅ Giữ tiền!")
					data[uid]["money"] += total - amount
					break

		if total > 0 and step_count == 8:
			data[uid]["money"] += total - amount

		data[uid]["last_snake"] = datetime.utcnow().isoformat()
		save_users(data)

		await msg.edit(content="🎰 **Kết quả Rắn Leo Thang:**\n" + "\n".join(result) +
						 f"\n\n💰 **Số dư:** 🪙 {data[uid]['money']:,} xu", view=None)

		# ✅ Tự động xóa sau 2 phút
		await asyncio.sleep(120)
		try:
			await msg.delete()
		except:
			pass

class ContinueOrStopView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=10)
		self.choice = None

	@discord.ui.button(label="Tiếp tục", style=discord.ButtonStyle.success, emoji="▶️")
	async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.choice = "continue"
		self.stop()

	@discord.ui.button(label="Dừng lại", style=discord.ButtonStyle.danger, emoji="⛔")
	async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.choice = "stop"
		self.stop()

async def setup(bot):
	await bot.add_cog(SnakeGame(bot))
