import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta
import json
import os
import asyncio

USER_FILE = "data/users.json"
EMOJIS = ["🍒", "🍋", "🔔", "🍇", "💎", "⭐"]

def load_users():
	if not os.path.exists(USER_FILE):
		with open(USER_FILE, "w") as f:
			json.dump({}, f)
	with open(USER_FILE, "r") as f:
		return json.load(f)

def save_users(data):
	with open(USER_FILE, "w") as f:
		json.dump(data, f, indent=4)

def get_user_data(user_id):
	data = load_users()
	return data.get(str(user_id), {})

def get_slot_cooldown(user_id):
	user = get_user_data(user_id)
	last = user.get("last_slot", "1970-01-01T00:00:00")
	last_time = datetime.fromisoformat(last)
	elapsed = datetime.utcnow() - last_time
	cd = timedelta(minutes=2)
	return None if elapsed >= cd else cd - elapsed

class XungXeng(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="xungxeng", description="🎰 Quay xèng may mắn để thử vận may!")
	@app_commands.describe(
		amount="Số tiền bạn muốn đặt cược",
		pick="Chọn biểu tượng bạn muốn đặt cược (🍒, 🍋, 🔔, 🍇, 💎, ⭐)"
	)
	@app_commands.choices(
		pick=[
			app_commands.Choice(name="🍒 Cheri", value="🍒"),
			app_commands.Choice(name="🍋 Chanh", value="🍋"),
			app_commands.Choice(name="🔔 Chuông", value="🔔"),
			app_commands.Choice(name="🍇 Nho", value="🍇"),
			app_commands.Choice(name="💎 Kim Cương", value="💎"),
			app_commands.Choice(name="⭐ Ngôi Sao", value="⭐"),
		]
	)
	async def xungxeng(self, interaction: discord.Interaction, amount: int, pick: app_commands.Choice[str]):
		users = load_users()
		uid = str(interaction.user.id)

		if uid not in users:
			await interaction.response.send_message("❌ Bạn chưa có hồ sơ!", ephemeral=True)
			return

		cd = get_slot_cooldown(interaction.user.id)
		if cd:
			m, s = divmod(int(cd.total_seconds()), 60)
			return await interaction.response.send_message(
				f"⏳ Bạn cần chờ {m} phút {s} giây để quay tiếp!", ephemeral=True)

		if amount <= 0:
			return await interaction.response.send_message("❌ Số tiền không hợp lệ!", ephemeral=True)

		if users[uid]["money"] < amount:
			return await interaction.response.send_message("❌ Bạn không đủ xu!", ephemeral=True)

		await interaction.response.send_message("🎰 Bắt đầu quay xèng...", ephemeral=False)
		msg = await interaction.original_response()

		# Bắt đầu hiệu ứng quay hoạt ảnh từng bước
		slots = ["❓", "❓", "❓"]
		steps = [0, 1, 2]
		final_result = [random.choice(EMOJIS) for _ in range(3)]

		for i in steps:
			await asyncio.sleep(2)  # delay giữa mỗi vòng quay
			slots[i] = final_result[i]
			anim_embed = discord.Embed(
				title="🎰 Đang quay...",
				description=" | ".join(slots),
				color=discord.Color.orange()
			)
			await msg.edit(embed=anim_embed)

		await asyncio.sleep(1)

		# Tính kết quả
		symbol = pick.value
		count = final_result.count(symbol)
		if count == 3:
			win = amount * 5
			result_text = f"🎉 JACKPOT! Ba {symbol} trùng khớp!"
		elif count == 2:
			win = amount * 2
			result_text = f"🥳 Hai {symbol} trùng khớp!"
		elif count == 1:
			win = amount  # Hòa vốn
			result_text = f"😐 Một {symbol}, hoàn tiền."
		else:
			win = 0
			result_text = f"😢 Không có {symbol} nào, thua rồi..."

		# Cập nhật dữ liệu
		users[uid]["money"] -= amount
		users[uid]["money"] += win
		users[uid]["last_slot"] = datetime.utcnow().isoformat()
		save_users(users)

		# Hiển thị kết quả cuối
		result_embed = discord.Embed(title="🎰 Kết quả Xèng May Mắn", color=discord.Color.gold())
		result_embed.add_field(name="Kết quả", value=" | ".join(final_result), inline=False)
		result_embed.add_field(name="Bạn chọn", value=f"{symbol}", inline=True)
		result_embed.add_field(name="💬 Kết luận", value=result_text, inline=False)
		result_embed.add_field(name="💰 Tiền cược", value=f"{amount:,} xu", inline=True)
		result_embed.add_field(name="🏆 Nhận được", value=f"{win:,} xu", inline=True)
		result_embed.add_field(name="🪙 Số dư", value=f"{users[uid]['money']:,} xu", inline=False)

		await msg.edit(embed=result_embed)

async def setup(bot):
	await bot.add_cog(XungXeng(bot))
