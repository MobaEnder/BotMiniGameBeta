import discord
from discord import app_commands
from discord.ext import commands
from data.data_manager import collection  # Dùng trực tiếp MongoDB collection


class Leaderboard(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="leaderboard", description="Xem bảng xếp hạng người giàu nhất")
	async def leaderboard(self, interaction: discord.Interaction):
		# Lấy danh sách người dùng từ MongoDB, sắp xếp theo tiền giảm dần
		top_users = list(collection.find().sort("money", -1).limit(10))

		if not top_users:
			await interaction.response.send_message("❌ Không có người chơi nào trong bảng xếp hạng!")
			return

		description = ""
		for i, user_data in enumerate(top_users, start=1):
			user_id = user_data["_id"]
			user = await self.bot.fetch_user(int(user_id))
			money = user_data.get("money", 0)
			description += f"**{i}. {user.name}**\n💰 {money:,} xu\n"

		embed = discord.Embed(
			title="🏆 Bảng xếp hạng người giàu nhất",
			description=description,
			color=discord.Color.gold()
		)

		await interaction.response.send_message(embed=embed)


async def setup(bot):
	await bot.add_cog(Leaderboard(bot))
