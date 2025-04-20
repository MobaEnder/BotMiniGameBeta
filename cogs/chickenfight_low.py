# cogs/chickenfight_low.py

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
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

class ChickenFightLow(commands.Cog):
		def __init__(self, bot):
				self.bot = bot

		@app_commands.command(name="chickenfight_low", description="🐓 Đá gà solo - chọn Gà Đỏ hoặc Gà Vàng!")
		@app_commands.describe(amount="Số tiền muốn cược")
		async def chickenfight_low(self, interaction: discord.Interaction, amount: int):
				user = interaction.user
				uid = str(user.id)
				data = load_users()

				if uid not in data:
						await interaction.response.send_message("❌ Bạn chưa có tài khoản!", ephemeral=True)
						return

				if amount <= 0:
						await interaction.response.send_message("❌ Số tiền cược phải lớn hơn 0!", ephemeral=True)
						return

				if data[uid]["money"] < amount:
						await interaction.response.send_message("❌ Bạn không đủ tiền để chơi!", ephemeral=True)
						return

				class ChooseChicken(discord.ui.View):
						def __init__(self, author):
								super().__init__(timeout=10)
								self.value = None
								self.author = author

						async def interaction_check(self, interaction: discord.Interaction) -> bool:
								if interaction.user != self.author:
										await interaction.response.send_message("🚫 Bạn không thể chọn!", ephemeral=True)
										return False
								return True

						@discord.ui.button(label="Gà Đỏ", style=discord.ButtonStyle.danger, emoji="🔴")
						async def red_chicken(self, interaction: discord.Interaction, button: discord.ui.Button):
								self.value = "red"
								self.stop()
								await interaction.response.defer()

						@discord.ui.button(label="Gà Vàng", style=discord.ButtonStyle.success, emoji="🟡")
						async def yellow_chicken(self, interaction: discord.Interaction, button: discord.ui.Button):
								self.value = "yellow"
								self.stop()
								await interaction.response.defer()

				view = ChooseChicken(interaction.user)
				embed = discord.Embed(
						title="🐓 Nhà Cái Tới Từ BAKITTAN",
						description="**Chọn gà của bạn để đá:**\n🔴 Gà Đỏ hoặc 🟡 Gà Vàng",
						color=discord.Color.orange()
				)
				msg = await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
				message = await interaction.original_response()
				await view.wait()

				if view.value is None:
						await message.edit(content="⏳ Hết thời gian chọn gà! Trò chơi bị huỷ.", embed=None, view=None, delete_after=120)
						return

				user_choice = view.value
				await message.edit(
						content=f"🐔 **Bạn đã chọn:** {'🔴 Gà Đỏ' if user_choice == 'red' else '🟡 Gà Vàng'}\n⏱ Gà đang chuẩn bị chọi...",
						embed=None,
						view=None
				)

				await asyncio.sleep(10)  # Chuẩn bị

				winner = random.choice(["red", "yellow"])
				await asyncio.sleep(10)  # Chọi

				if user_choice == winner:
						data[uid]["money"] += amount
						result_text = f"🏆 **Gà của bạn đã thắng!** Bạn nhận được 🪙 {amount:,} xu."
				else:
						data[uid]["money"] -= amount
						result_text = f"💥 **Gà của bạn đã thua!** Bạn mất 🪙 {amount:,} xu."

				save_users(data)

				await message.edit(
						content=(
								f"⚔️ Trận đấu giữa 🔴 Gà Đỏ và 🟡 Gà Vàng bắt đầu!\n"
								f"🥁 Sau khi chiến đấu kịch liệt...\n\n"
								f"🏅 **Gà chiến thắng:** {'🔴 Gà Đỏ' if winner == 'red' else '🟡 Gà Vàng'}\n"
								f"{result_text}\n\n"
								f"💰 **Số dư hiện tại:** 🪙 {data[uid]['money']:,} xu"
						),
						delete_after=120
				)

async def setup(bot):
		await bot.add_cog(ChickenFightLow(bot))
