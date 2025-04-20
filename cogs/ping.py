import discord
from discord.ext import commands
from discord import app_commands

class PingUser(commands.Cog):
		def __init__(self, bot):
				self.bot = bot

		@app_commands.command(name="ping", description="Ping người được chọn 10 lần!")
		@app_commands.describe(user="Người bạn muốn spam ping 10 lần")
		async def ping(self, interaction: discord.Interaction, user: discord.User):
				await interaction.response.send_message(f"Bắt đầu ping {user.mention} 10 lần! 🚨")
				for i in range(10):
						await interaction.channel.send(user.mention)

async def setup(bot):
		await bot.add_cog(PingUser(bot))
