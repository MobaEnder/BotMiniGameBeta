import discord
from discord import app_commands
from discord.ext import commands
from data_manager import load_data


class Leaderboard(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="leaderboard",
	                      description="Xem bảng xếp hạng người giàu nhất")
	async def leaderboard(self, interaction: discord.Interaction):
		data = load_data()

		# Lọc và sắp xếp theo tiền
		leaderboard = sorted(data.items(),
		                     key=lambda x: x[1].get("money", 0),
		                     reverse=True)

		if not leaderboard:
			await interaction.response.send_message(
			    "❌ Không có người chơi nào trong bảng xếp hạng!")
			return

		description = ""
		for i, (user_id, info) in enumerate(leaderboard[:10], start=1):
			user = await self.bot.fetch_user(int(user_id))
			description += f"**{i}. {user.name}**\n{info.get('money', 0)} xu\n"

		embed = discord.Embed(title="🏆 Bảng xếp hạng",
		                      description=description,
		                      color=discord.Color.gold())

		await interaction.response.send_message(embed=embed)


async def setup(bot):
	await bot.add_cog(Leaderboard(bot))
