import discord
from discord import app_commands
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

def get_rank_name(level):
		if level >= 80:
				return "🥇 Thách Đấu"
		elif level >= 70:
				return "🏆 Cao Thủ"
		elif level >= 60:
				return "💎 Lục Bảo"
		elif level >= 50:
				return "💠 Kim Cương"
		elif level >= 40:
				return "🔶 Bạch Kim"
		elif level >= 30:
				return "⭐ Vàng"
		elif level >= 20:
				return "🔷 Bạc"
		elif level >= 10:
				return "🥉 Đồng"
		else:
				return "🪙 Tân Thủ"

class Rank(commands.Cog):

		def __init__(self, bot):
				self.bot = bot

		@app_commands.command(name="rank", description="Xem thứ hạng cấp độ của bạn hoặc người khác")
		@app_commands.describe(user="Người dùng bạn muốn xem rank (tùy chọn)")
		async def rank(self, interaction: discord.Interaction, user: discord.User = None):
				target_user = user or interaction.user
				user_id = str(target_user.id)
				data = load_level_data()

				if user_id not in data:
						await interaction.response.send_message(
								f"{target_user.mention} chưa có dữ liệu cấp độ trong hệ thống.", ephemeral=True)
						return

				# Sắp xếp theo level thật và xp
				sorted_users = sorted(
						data.items(),
						key=lambda item: (item[1].get("level", 1), item[1].get("xp", 0)),
						reverse=True
				)

				rank_pos = next((i for i, (uid, _) in enumerate(sorted_users) if uid == user_id), -1) + 1

				user_data = data[user_id]
				level = user_data.get("level", 1)
				xp = user_data.get("xp", 0)
				rank_name = get_rank_name(level)

				embed = discord.Embed(
						title=f"🏆 Rank của {target_user.display_name}",
						color=discord.Color.gold()
				)
				embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else discord.Embed.Empty)
				embed.add_field(name="Rank", value=f"{rank_pos}/{len(data)}", inline=True)
				embed.add_field(name="Cấp độ", value=f"{level}", inline=True)
				embed.add_field(name="XP", value=f"{xp} / 600", inline=True)
				embed.add_field(name="Hạng", value=rank_name, inline=False)

				await interaction.response.send_message(embed=embed)

async def setup(bot):
		await bot.add_cog(Rank(bot)) 
