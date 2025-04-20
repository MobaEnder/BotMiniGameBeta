import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import json
import os

DATA_FILE = "data/users.json"

def load_data():
		if not os.path.exists(DATA_FILE):
				with open(DATA_FILE, "w") as f:
						json.dump({}, f)
		with open(DATA_FILE, "r") as f:
				return json.load(f)

def save_data(data):
		with open(DATA_FILE, "w") as f:
				json.dump(data, f, indent=4)

def get_user(user_id):
		data = load_data()
		user_id = str(user_id)
		if user_id not in data:
				data[user_id] = {"money": 0}
				save_data(data)
		return data[user_id]

def update_money(user_id, amount):
		data = load_data()
		user_id = str(user_id)
		user = get_user(user_id)
		user["money"] += amount
		data[user_id] = user
		save_data(data)
		return user["money"]

class Race(commands.Cog):
		def __init__(self, bot):
				self.bot = bot

		@app_commands.command(name="race", description="Đua ngựa đặt cược và chọn ngựa của bạn!")
		@app_commands.describe(
				bet_amount="Số tiền bạn muốn cược",
				horse="Chọn con ngựa bạn muốn cược"
		)
		@app_commands.choices(horse=[
				app_commands.Choice(name="🐎 Ngựa 1", value="🐎"),
				app_commands.Choice(name="🏇 Ngựa 2", value="🏇"),
				app_commands.Choice(name="🐴 Ngựa 3", value="🐴"),
		])
		async def race(self, interaction: discord.Interaction, bet_amount: int, horse: app_commands.Choice[str]):
				user_id = str(interaction.user.id)
				user = get_user(user_id)

				if bet_amount <= 0:
						await interaction.response.send_message("❌ Số tiền cược không hợp lệ.", ephemeral=True)
						return

				if user["money"] < bet_amount:
						await interaction.response.send_message("❌ Bạn không đủ tiền để cược!", ephemeral=True)
						return

				horses = ["🐎", "🏇", "🐴"]
				positions = [0, 0, 0]
				finish_line = 10
				player_horse = horse.value

				await interaction.response.send_message("🎬 **Cuộc đua ngựa bắt đầu!**", ephemeral=False)
				race_msg = await interaction.followup.send("Đang chuẩn bị đường đua...")

				await asyncio.sleep(1)

				winner = -1
				while max(positions) < finish_line:
						await asyncio.sleep(1)
						advancing = random.choices([0, 1, 2], k=2)
						for i in advancing:
								positions[i] += 1

						track = ""
						for i in range(3):
								track += f"{horses[i]} |{'=' * positions[i]}>\n"
								if positions[i] >= finish_line and winner == -1:
										winner = i

						await race_msg.edit(content=f"```\n{track}```")

				result_text = f"🏁 **{horses[winner]} đã về nhất!**\n"
				result_text += f"Bạn đã cược vào: **{player_horse}**\n"

				if player_horse == horses[winner]:
						prize = bet_amount * 2
						update_money(user_id, prize)
						result_text += f"🎉 Bạn thắng và nhận được **{prize} xu**!"
				else:
						update_money(user_id, -bet_amount)
						result_text += f"😢 Bạn đã thua và mất **{bet_amount} xu**."

				await interaction.followup.send(result_text)

async def setup(bot):
		await bot.add_cog(Race(bot))
