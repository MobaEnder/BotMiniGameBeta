import discord
from discord.ext import commands
import json
import os

LEVEL_FILE = "data/level.json"

def load_level_data():
		if not os.path.exists(LEVEL_FILE):
				with open(LEVEL_FILE, "w") as f:
						json.dump({}, f)
		with open(LEVEL_FILE, "r") as f:
				return json.load(f)

def save_level_data(data):
		with open(LEVEL_FILE, "w") as f:
				json.dump(data, f, indent=4)

class LevelSystem(commands.Cog):
		def __init__(self, bot):
				self.bot = bot

		@commands.Cog.listener()
		async def on_app_command_completion(self, interaction: discord.Interaction, command: discord.app_commands.Command):
				user_id = str(interaction.user.id)
				data = load_level_data()

				if user_id not in data:
						data[user_id] = {"xp": 0, "level": 1}

				# Cộng 30 EXP mỗi lần dùng lệnh
				data[user_id]["xp"] += 30

				# Kiểm tra lên cấp
				while data[user_id]["xp"] >= 600:
						data[user_id]["xp"] -= 600
						data[user_id]["level"] += 1

						# Gửi thông báo lên cấp (nếu muốn)
						try:
								await interaction.followup.send(f"🎉 {interaction.user.mention} đã lên cấp **{data[user_id]['level']}**!", ephemeral=True)
						except:
								pass

				save_level_data(data)

async def setup(bot):
		await bot.add_cog(LevelSystem(bot))
