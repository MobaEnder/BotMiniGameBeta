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

class TaiXiuRoom:
		def __init__(self, creator, bet_amount):
				self.creator = creator
				self.bet_amount = bet_amount
				self.players = {}  # {user_id: "tài"/"xỉu"}

		def add_player(self, user_id, choice):
				if user_id not in self.players:
						self.players[user_id] = choice
						return True
				return False

		def get_result(self):
				dice = [random.randint(1, 6) for _ in range(3)]
				total = sum(dice)
				result = "tài" if total >= 11 else "xỉu"
				return result, total, dice

class TTX_Button(discord.ui.View):
		def __init__(self, ctx, room, timeout=15):
				super().__init__(timeout=timeout)
				self.ctx = ctx
				self.room = room
				self.finished = asyncio.Event()

		@discord.ui.button(label="🐯 Tài", style=discord.ButtonStyle.success, custom_id="taixiu_tai")
		async def tai_button(self, interaction: discord.Interaction, button: discord.ui.Button):
				await self.process_bet(interaction, "tài")

		@discord.ui.button(label="🦊 Xỉu", style=discord.ButtonStyle.primary, custom_id="taixiu_xiu")
		async def xiu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
				await self.process_bet(interaction, "xỉu")

		async def process_bet(self, interaction: discord.Interaction, choice: str):
				user_id = str(interaction.user.id)
				if user_id in self.room.players:
						return await interaction.response.send_message("❌ Bạn đã cược rồi!", ephemeral=True)

				user = get_user(interaction.user.id)
				if user["money"] < self.room.bet_amount:
						return await interaction.response.send_message(f"❌ Bạn không đủ tiền cược, bạn cần **{self.room.bet_amount} xu** để tham gia.", ephemeral=True)

				update_money(interaction.user.id, -self.room.bet_amount)
				self.room.add_player(user_id, choice)

				await interaction.response.send_message(f"✅ Bạn đã cược **{self.room.bet_amount} xu** vào **{choice.upper()}**!", ephemeral=True)

				bet_list = "\n".join(
						f"• <@{uid}> cược **{self.room.bet_amount} xu** vào **{self.room.players[uid]}**"
						for uid in self.room.players
				)
				await self.ctx.send(f"📋 **Danh sách cược:**\n{bet_list}")

		async def on_timeout(self):
				self.finished.set()

class TaiXiuBig(commands.Cog):
		def __init__(self, bot):
				self.bot = bot
				self.rooms = {}  # {room_id: TaiXiuRoom}

		@app_commands.command(name="taixiu_big", description="Tạo phòng chơi Tài/Xỉu nhiều người cược")
		async def taixiu_big(self, interaction: discord.Interaction, bet_amount: int):
				room_id = str(interaction.user.id)
				if room_id in self.rooms:
						await interaction.response.send_message("❌ Bạn đã tạo phòng rồi!", ephemeral=True)
						return

				room = TaiXiuRoom(interaction.user.id, bet_amount)
				self.rooms[room_id] = room
				await interaction.response.send_message(
						f"🎲 Trò chơi **Tài/Xỉu** bắt đầu!\n⏳ Bạn có 15 giây để đặt cược bằng cách bấm nút. Mỗi lượt cược **{bet_amount} xu**.",
						ephemeral=False
				)
				msg = await interaction.original_response()

				view = TTX_Button(interaction, room, timeout=15)
				await msg.edit(view=view)

				await asyncio.sleep(15)
				view.stop()
				await view.on_timeout()

				result, total, dice = room.get_result()
				result_text = f"🎲 Kết quả: {dice[0]} + {dice[1]} + {dice[2]} = {total} → **{result.upper()}**\n\n"
				result_text += "📋 **Danh sách cược:**\n"

				for uid, choice in room.players.items():
						result_text += f"• <@{uid}> cược **{bet_amount} xu** vào **{choice}**\n"

				winners = []
				for uid, choice in room.players.items():
						if choice == result:
								prize = bet_amount * 2
								update_money(uid, prize)
								winners.append(f"<@{uid}> (+{prize} xu)")

				if winners:
						result_text += "\n🏆 **Người thắng:** " + ", ".join(winners)
				else:
						result_text += "\n😢 Không ai thắng lần này."

				await msg.edit(content=result_text, view=None)

				# ✅ Xóa phòng sau khi kết thúc
				del self.rooms[room_id]

async def setup(bot):
		await bot.add_cog(TaiXiuBig(bot))
