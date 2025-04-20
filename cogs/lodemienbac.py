# cogs/lodemienbac.py

import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta
import asyncio

from data.data_manager import get_user, update_balance, add_exp

COOLDOWN = timedelta(minutes=1)

class Lode(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cooldowns = {}

	@app_commands.command(name="lodemienbac", description="🎯 Đoán số từ 1-10, có 3 lần đoán. Trúng x4 số tiền!")
	@app_commands.describe(
		bet="Số tiền bạn muốn cược",
		so1="Số đầu tiên bạn chọn (1-10)",
		so2="Số thứ hai bạn chọn (1-10)",
		so3="Số thứ ba bạn chọn (1-10)"
	)
	async def lodemienbac(self, interaction: discord.Interaction, bet: int, so1: int, so2: int, so3: int):
		await interaction.response.defer()

		user_id = str(interaction.user.id)
		user = get_user(user_id)

		if not all(1 <= s <= 10 for s in [so1, so2, so3]):
			return await interaction.followup.send("❌ Bạn chỉ được chọn số từ 1 đến 10!", ephemeral=True)

		# Cooldown
		last_time = user.get("last_lode", "1970-01-01T00:00:00")
		time_passed = datetime.utcnow() - datetime.fromisoformat(last_time)
		if time_passed < COOLDOWN:
			remaining = COOLDOWN - time_passed
			mins, secs = divmod(int(remaining.total_seconds()), 60)
			return await interaction.followup.send(f"🕓 Chờ {mins} phút {secs} giây nữa để chơi tiếp!", ephemeral=True)

		if user["money"] < bet:
			return await interaction.followup.send("💸 Bạn không đủ tiền để cược!", ephemeral=True)

		# Trừ tiền & cập nhật thời gian
		update_balance(user_id, -bet)
		user["last_lode"] = datetime.utcnow().isoformat()

		# Quay số hiệu ứng
		spin_msg = await interaction.followup.send("🎰 Đang quay số Miền Bắc...")
		await asyncio.sleep(2)

		result = random.randint(1, 10)
		emojis = ["🍉", "🍋", "🌟", "🍓", "🎯", "🍇", "🍀", "🎈", "💎", "🔥"]
		result_emoji = random.choice(emojis)

		spin_text = ""
		for _ in range(8):
			spin_text += f"🎲 {random.randint(1, 10)} {random.choice(emojis)}\n"
			await spin_msg.edit(content=f"🔄 Quay số...\n{spin_text}")
			await asyncio.sleep(0.4)

		# Kết quả
		if result in [so1, so2, so3]:
			won = bet * 4
			update_balance(user_id, won)
			add_exp(user_id, 30)
			await spin_msg.edit(content=(
				f"🎉 Kết quả: **{result} {result_emoji}**\n"
				f"✅ Bạn đã đoán trúng và nhận **🪙 {won:,} xu**!"
			))
		else:
			add_exp(user_id, 30)
			await spin_msg.edit(content=(
				f"🎯 Kết quả: **{result} {result_emoji}**\n"
				f"❌ Rất tiếc, bạn đã đoán sai!"
			))

async def setup(bot):
	await bot.add_cog(Lode(bot))
