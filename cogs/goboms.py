import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
import json
import os
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

def get_bomb_cooldown(user_id):
	data = load_users()
	user = data.get(str(user_id), {})
	last_time = user.get("last_bomb", "1970-01-01T00:00:00")
	last_time = datetime.fromisoformat(last_time)
	cooldown = timedelta(minutes=1)
	now = datetime.utcnow()
	if now - last_time >= cooldown:
		return None
	return cooldown - (now - last_time)

class BombDefuse(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="bombdefuse", description="💣 Gỡ Bom May Rủi - chọn đúng dây để thắng lớn!")
	@app_commands.describe(amount="Số tiền cược")
	async def bombdefuse(self, interaction: discord.Interaction, amount: int):
		await interaction.response.defer()
		user = interaction.user
		uid = str(user.id)
		data = load_users()

		if uid not in data:
			await interaction.followup.send("❌ Bạn chưa có tài khoản!", ephemeral=True)
			return

		cooldown = get_bomb_cooldown(uid)
		if cooldown:
			m, s = divmod(int(cooldown.total_seconds()), 60)
			await interaction.followup.send(f"⏳ Hãy chờ {m} phút {s} giây nữa để thử lại!", ephemeral=True)
			return

		if amount <= 0:
			await interaction.followup.send("❌ Số tiền cược phải lớn hơn 0!", ephemeral=True)
			return

		if data[uid]["money"] < amount:
			await interaction.followup.send("❌ Bạn không đủ tiền!", ephemeral=True)
			return

		wires = ["🟥", "🟩", "🟦", "🟨"]
		winning_wire = random.choice(wires)

		view = discord.ui.View(timeout=120)
		chosen = []

		class WireButton(discord.ui.Button):
			def __init__(self, wire):
				super().__init__(label=wire, style=discord.ButtonStyle.primary)
				self.wire = wire

			async def callback(self, interaction_button: discord.Interaction):
				if interaction_button.user.id != interaction.user.id:
					await interaction_button.response.send_message("Không phải lượt của bạn!", ephemeral=True)
					return
				if chosen:
					return
				chosen.append(self.wire)

				if self.wire == winning_wire:
					data[uid]["money"] += amount * 4 - amount
					result = f"✅ Bạn đã gỡ đúng dây {self.wire} và thắng **x4** số tiền! 💸"
				else:
					data[uid]["money"] -= amount
					result = f"💥 Boom! Dây {self.wire} đã nổ! Bạn mất trắng rồi! 😵"

				data[uid]["last_bomb"] = datetime.utcnow().isoformat()
				save_users(data)
				await interaction_button.response.edit_message(content=result + f"\n\n💰 Số dư: 🪙 {data[uid]['money']:,} xu", view=None)
				await asyncio.sleep(120)
				try:
					await interaction_button.message.delete()
				except:
					pass

		for w in wires:
			view.add_item(WireButton(w))

		embed = discord.Embed(title="💣 Gỡ Bom May Rủi",
						description="Chọn đúng dây để gỡ bom! Một dây an toàn duy nhất! 💥",
						color=discord.Color.red())
		embed.add_field(name="Cược:", value=f"🪙 {amount:,} xu", inline=False)
		msg = await interaction.followup.send(embed=embed, view=view)

		# Sau 2 phút nếu không chọn
		await asyncio.sleep(120)
		if not chosen:
			await msg.edit(content="⏳ Hết thời gian chọn dây! Trò chơi kết thúc.", view=None)
			await asyncio.sleep(5)
			try:
				await msg.delete()
			except:
				pass

async def setup(bot):
	await bot.add_cog(BombDefuse(bot))
