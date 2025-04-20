import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
import asyncio

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
	uid = str(user_id)
	if uid not in data:
		data[uid] = {"money": 0}
		save_data(data)
	return data[uid]


def update_money(user_id, amount):
	data = load_data()
	uid = str(user_id)
	user = get_user(user_id)
	user["money"] += amount
	data[uid] = user
	save_data(data)
	return user["money"]


class TàiXỉuView(discord.ui.View):

	def __init__(self, user_id, bet_amount):
		super().__init__(timeout=10)
		self.user_id = user_id
		self.bet_amount = bet_amount
		self.choice = None
		self.interaction_event = asyncio.Event()

	@discord.ui.button(label="Tài", style=discord.ButtonStyle.success)
	async def tai_button(self, interaction: discord.Interaction,
	                     button: discord.ui.Button):
		if interaction.user.id != self.user_id:
			return await interaction.response.send_message(
			    "Bạn không phải người chơi!", ephemeral=True)
		self.choice = "tài"
		await interaction.response.send_message(
		    "🎲 Bạn đã chọn **Tài**. Đang quay xúc xắc...")
		self.interaction_event.set()

	@discord.ui.button(label="Xỉu", style=discord.ButtonStyle.danger)
	async def xiu_button(self, interaction: discord.Interaction,
	                     button: discord.ui.Button):
		if interaction.user.id != self.user_id:
			return await interaction.response.send_message(
			    "Bạn không phải người chơi!", ephemeral=True)
		self.choice = "xỉu"
		await interaction.response.send_message(
		    "🎲 Bạn đã chọn **Xỉu**. Đang quay xúc xắc...")
		self.interaction_event.set()


class TaiXiuLow(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="taixiu_low",
	                      description="Chơi Tài Xỉu đơn (chọn nút và đợi 5s)")
	@app_commands.describe(amount="Số tiền bạn muốn cược")
	async def taixiu_low(self, interaction: discord.Interaction, amount: int):
		user = get_user(interaction.user.id)

		if amount <= 0:
			return await interaction.response.send_message(
			    "❌ Số tiền cược phải lớn hơn 0.", ephemeral=True)
		if user["money"] < amount:
			return await interaction.response.send_message(
			    "❌ Bạn không đủ tiền để cược.", ephemeral=True)

		view = TàiXỉuView(interaction.user.id, amount)
		await interaction.response.send_message(
		    f"🎮 Chọn **Tài** hoặc **Xỉu** để cược **{amount} xu**.",
		    view=view,
		    ephemeral=True)

		await view.interaction_event.wait()
		await asyncio.sleep(5)

		dice = [random.randint(1, 6) for _ in range(3)]
		total = sum(dice)
		result = "tài" if total >= 11 else "xỉu"

		win = result == view.choice
		money_change = amount if win else -amount
		new_balance = update_money(interaction.user.id, money_change)

		result_text = (
		    f"🎲 Kết quả: {dice[0]} + {dice[1]} + {dice[2]} = **{total} ⇒ {result.upper()}**\n"
		    f"{'✅ Bạn thắng' if win else '❌ Bạn thua'} **{abs(money_change)} xu**!\n"
		    f"💰 Số dư hiện tại: {new_balance} xu.")

		await interaction.followup.send(result_text, ephemeral=True)


async def setup(bot):
	await bot.add_cog(TaiXiuLow(bot))
