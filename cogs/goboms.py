import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
import asyncio
from data_manager import get_user, update_balance, add_exp

class BombDefuse(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="bombdefuse", description="💣 Gỡ Bom May Rủi - chọn đúng dây để thắng lớn!")
	@app_commands.describe(amount="Số tiền cược")
	async def bombdefuse(self, interaction: discord.Interaction, amount: int):
		await interaction.response.defer()
		user = interaction.user
		uid = str(user.id)

		# Lấy dữ liệu người dùng từ MongoDB
		user_data = await get_user(uid)

		# Kiểm tra cooldown
		last_time_str = user_data.get("last_bomb", "1970-01-01T00:00:00")
		last_time = datetime.fromisoformat(last_time_str)
		now = datetime.utcnow()
		cooldown = timedelta(minutes=1)
		if now - last_time < cooldown:
			remaining = cooldown - (now - last_time)
			m, s = divmod(int(remaining.total_seconds()), 60)
			return await interaction.followup.send(f"⏳ Hãy chờ {m} phút {s} giây nữa để chơi tiếp!", ephemeral=True)

		if amount <= 0:
			return await interaction.followup.send("❌ Số tiền cược phải lớn hơn 0!", ephemeral=True)

		if user_data["money"] < amount:
			return await interaction.followup.send("❌ Bạn không đủ tiền!", ephemeral=True)

		wires = ["🟥", "🟩", "🟦", "🟨"]
		winning_wire = random.choice(wires)
		chosen = []

		view = discord.ui.View(timeout=120)

		class WireButton(discord.ui.Button):
			def __init__(self, wire):
				super().__init__(label=wire, style=discord.ButtonStyle.primary)
				self.wire = wire

			async def callback(self, interaction_button: discord.Interaction):
				if interaction_button.user.id != interaction.user.id:
					return await interaction_button.response.send_message("Không phải lượt của bạn!", ephemeral=True)
				if chosen:
					return
				chosen.append(self.wire)

				# Xử lý kết quả
				result = ""
				if self.wire == winning_wire:
					await update_balance(uid, amount * 3)  # lời gấp 4 - cược gốc
					result = f"✅ Bạn đã gỡ đúng dây {self.wire} và thắng **x4** số tiền! 💸"
				else:
					await update_balance(uid, -amount)
					result = f"💥 Boom! Dây {self.wire} đã nổ! Bạn mất trắng rồi! 😵"

				# Cập nhật thời gian chơi bom
				user_data["last_bomb"] = datetime.utcnow().isoformat()
				await get_user(uid, update=user_data)

				# Cộng EXP
				await add_exp(uid, 30)
				new_balance = user_data["money"] + (amount * 3 if self.wire == winning_wire else -amount)

				await interaction_button.response.edit_message(
					content=result + f"\n\n💰 Số dư: 🪙 {new_balance:,} xu\n✨ Bạn nhận được **30 EXP**!",
					view=None
				)

				await asyncio.sleep(120)
				try:
					await interaction_button.message.delete()
				except:
					pass

		for w in wires:
			view.add_item(WireButton(w))

		embed = discord.Embed(
			title="💣 Gỡ Bom May Rủi",
			description="Chọn đúng dây để gỡ bom! Một dây duy nhất là an toàn! 💥",
			color=discord.Color.red()
		)
		embed.add_field(name="Cược:", value=f"🪙 {amount:,} xu", inline=False)
		msg = await interaction.followup.send(embed=embed, view=view)

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
