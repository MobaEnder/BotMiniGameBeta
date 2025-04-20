import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta
from data_manager import get_user, update_balance, add_exp, get_level_info

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

class Fishing(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="fish", description="Câu cá để kiếm tiền và tìm cá hiếm!")
	async def fish(self, interaction: discord.Interaction):
		user_id = str(interaction.user.id)
		user_data = await get_user(user_id)

		last_fish_str = user_data.get("last_fish", "1970-01-01T00:00:00")
		last_fish_time = datetime.fromisoformat(last_fish_str)
		if datetime.utcnow() - last_fish_time < timedelta(hours=1):
			return await interaction.response.send_message(
				"🕒 Bạn vừa câu cá gần đây! Hãy thử lại sau **1 giờ**.", ephemeral=True
			)

		# Random sự kiện + cá
		event = random.choice(RANDOM_EVENTS)
		modifier = event["modifier"]
		fish = random.choices(
			FISH_TYPES,
			weights=[60, 30, 20, 20, 7, 2, 1],
			k=1
		)[0]
		final_value = int(fish["value"] * modifier)

		# Cập nhật tiền + EXP
		new_balance = await update_balance(user_id, final_value)
		await add_exp(user_id, 30)

		# Cập nhật thời gian câu cá
		user_data["last_fish"] = datetime.utcnow().isoformat()
		await get_user(user_id, update=user_data)

		# Ghi chú độ hiếm nếu có
		rarity_note = ""
		if "rarity" in fish:
			rarity_note = f"🎉 Bạn đã bắt được cá **{fish['rarity']}**!"

		await interaction.response.send_message(
			f"{event['message']}\n"
			f"🎣 Bạn câu được {fish['name']} và bán được **{final_value} xu**!\n"
			f"{rarity_note}\n"
			f"💰 Số dư hiện tại: {new_balance} xu.\n"
			f"✨ Bạn nhận được **30 EXP**!"
		)

async def setup(bot):
	await bot.add_cog(Fishing(bot))
