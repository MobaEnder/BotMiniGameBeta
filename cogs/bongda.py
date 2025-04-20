import discord
from discord import app_commands, ButtonStyle
from discord.ui import Button, View
from discord.ext import commands
import random
import asyncio
import json
import os

class BongDa(commands.Cog):
		def __init__(self, bot):
				self.bot = bot
				self.countries = [
						"Japan", "PXG", "Batstard Muchen", "Ubers", "Blue Lock",
						"Italy", "England", "Manshine", "Barcha", ""
				]
				self.game_room = None
				self.players = []
				self.teams = {}
				self.bets = {}
				self.join_message = None
				self.game_messages = []
				self.USERS_FILE = "data/users.json"

		def load_users(self):
				try:
						if not os.path.exists(self.USERS_FILE):
								with open(self.USERS_FILE, "w") as f:
										json.dump({}, f)
						with open(self.USERS_FILE, "r") as f:
								return json.load(f)
				except (json.JSONDecodeError, IOError) as e:
						print(f"Error loading users.json: {e}")
						return {}

		def save_users(self, data):
				try:
						with open(self.USERS_FILE, "w") as f:
								json.dump(data, f, indent=4)
				except IOError as e:
						print(f"Error saving users.json: {e}")

		def update_balance(self, user_id, amount):
				uid = str(user_id)
				users_data = self.load_users()

				if uid not in users_data:
						users_data[uid] = {"money": 1000}

				users_data[uid]["money"] = users_data[uid].get("money", 1000) + amount
				if users_data[uid]["money"] < 0:
						users_data[uid]["money"] = 0

				self.save_users(users_data)
				return users_data[uid]["money"]

		def check_balance(self, user_id):
				uid = str(user_id)
				users_data = self.load_users()
				if uid not in users_data:
						users_data[uid] = {"money": 1000}
						self.save_users(users_data)
				return users_data[uid].get("money", 1000)

		def reset_game_state(self):
				self.game_room = None
				self.players = []
				self.teams = {}
				self.bets = {}
				self.join_message = None
				self.game_messages = []

		async def play_game(self, interaction, team1, team2):
				try:
						msg = await interaction.followup.send(f"🏟 **Trận đấu giữa {team1} và {team2} bắt đầu!** ⚽\n"
																									"🥅⚽🥅 Cầu thủ đang tranh bóng... 🏃‍♂️💨")
						self.game_messages.append(msg)
				except discord.errors.Forbidden:
						await interaction.followup.send("Bot không có quyền gửi tin nhắn trong kênh này! ⚽")

				await asyncio.sleep(15)

				score1 = random.randint(1, 10)
				score2 = random.randint(1, 10)
				winner = team1 if score1 > score2 else team2 if score2 > score1 else "Hòa"

				if winner != "Hòa":
						winner_player = self.players[0] if self.teams[self.players[0]] == winner else self.players[1]
						loser_player = self.players[1] if self.teams[self.players[0]] == winner else self.players[0]
						bet_amount = self.bets[self.players[0].id]

						self.update_balance(winner_player.id, bet_amount)
						self.update_balance(loser_player.id, -bet_amount)

						try:
								msg = await interaction.followup.send(f"🏆 **Kết quả trận đấu:** {winner} thắng!\n"
																											f"{team1} {score1} - {score2} {team2}\n"
																											f"Chúc mừng {winner_player.mention}! Bạn thắng {bet_amount} 💰\n"
																											f"{loser_player.mention} đã thua {bet_amount} 💰")
								self.game_messages.append(msg)
						except discord.errors.Forbidden:
								await interaction.followup.send("Bot không có quyền gửi tin nhắn trong kênh này! ⚽")
				else:
						try:
								msg = await interaction.followup.send(f"🏁 **Kết quả trận đấu:** Hòa!\n"
																											f"{team1} {score1} - {score2} {team2}\n"
																											"Một trận đấu cân sức! Không ai mất tiền ⚽")
								self.game_messages.append(msg)
						except discord.errors.Forbidden:
								await interaction.followup.send("Bot không có quyền gửi tin nhắn trong kênh này! ⚽")

				try:
						msg = await interaction.followup.send("🏟 **Ván chơi đã kết thúc!** Bạn có thể bắt đầu ván mới bằng `/bongda` ⚽")
						self.game_messages.append(msg)
				except discord.errors.Forbidden:
						await interaction.followup.send("Bot không có quyền gửi tin nhắn trong kênh này! ⚽")

				messages_to_delete = self.game_messages.copy()
				self.reset_game_state()

				await asyncio.sleep(60)

				for msg in messages_to_delete:
						try:
								await msg.delete()
						except (discord.errors.NotFound, discord.errors.Forbidden):
								pass

		@app_commands.command(name="bongda", description="Tạo một trận đấu bóng đá cho 2 người chơi với cược tiền")
		@app_commands.describe(bet_amount="Số tiền bạn muốn cược (nhập số bất kỳ)")
		async def bongda(self, interaction: discord.Interaction, bet_amount: int):
				try:
						# Defer phản hồi để tránh timeout
						await interaction.response.defer()

						# Kiểm tra nếu đã có phòng chơi
						if self.game_room:
								await interaction.followup.send("Đã có một trận đấu đang diễn ra! Vui lòng chờ nhé ⚽", ephemeral=True)
								return

						# Kiểm tra số tiền cược hợp lệ
						if bet_amount <= 0:
								await interaction.followup.send("Số tiền cược phải lớn hơn 0! ⚽", ephemeral=True)
								return

						# Kiểm tra số dư
						current_balance = self.check_balance(interaction.user.id)
						if current_balance < bet_amount:
								await interaction.followup.send(f"Bạn không đủ tiền để cược! Số dư hiện tại: {current_balance} 💰", ephemeral=True)
								return

						# Tạo phòng chơi mới
						self.game_room = interaction.channel
						self.players = []
						self.teams = {}
						self.bets = {}
						self.game_messages = []

						# Thêm người chơi đầu tiên và số tiền cược
						self.players.append(interaction.user)
						self.bets[interaction.user.id] = bet_amount

						# Tạo nút "Tham gia"
						join_button = Button(label="Tham gia", style=ButtonStyle.green, emoji="⚽")

						async def join_button_callback(interaction: discord.Interaction):
								try:
										await interaction.response.defer(ephemeral=True)

										if interaction.user in self.players:
												await interaction.followup.send("Bạn đã tham gia rồi! Chờ người chơi khác nhé ⚽", ephemeral=True)
												return

										if len(self.players) >= 2:
												await interaction.followup.send("Đã đủ 2 người chơi! Không thể tham gia nữa ⚽", ephemeral=True)
												return

										current_balance = self.check_balance(interaction.user.id)
										if current_balance < self.bets[self.players[0].id]:
												await interaction.followup.send(f"Bạn không đủ tiền để cược! Cần ít nhất {self.bets[self.players[0].id]} 💰. Số dư hiện tại: {current_balance}", ephemeral=True)
												return

										self.players.append(interaction.user)
										self.bets[interaction.user.id] = self.bets[self.players[0].id]
										try:
												msg = await interaction.followup.send(f"🏟 {interaction.user.mention} đã tham gia! Đủ 2 người, trận đấu sắp bắt đầu! ⚽")
												self.game_messages.append(msg)
										except discord.errors.Forbidden:
												await interaction.followup.send("Bot không có quyền gửi tin nhắn trong kênh này! ⚽")

										try:
												join_button.disabled = True
												if self.join_message:
														await self.join_message.edit(view=self.join_view)
										except (discord.errors.NotFound, discord.errors.Forbidden):
												pass

										team1 = random.choice(self.countries)
										team2 = random.choice([c for c in self.countries if c != team1])
										self.teams[self.players[0]] = team1
										self.teams[self.players[1]] = team2

										try:
												msg = await interaction.followup.send(f"⚽ **Đội hình thi đấu:**\n"
																															f"{self.players[0].mention} chọn đội **{team1}** 🇺🇳\n"
																															f"{self.players[1].mention} chọn đội **{team2}** 🇺🇳\n"
																															f"Số tiền cược: **{self.bets[self.players[0].id]}** 💰\n"
																															"Trận đấu sẽ bắt đầu sau 10 giây... ⏳")
												self.game_messages.append(msg)
										except discord.errors.Forbidden:
												await interaction.followup.send("Bot không có quyền gửi tin nhắn trong kênh này! ⚽")

										await self.play_game(interaction, team1, team2)

								except Exception as e:
										await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}. Vui lòng thử lại! ⚽")
										self.reset_game_state()

						join_button.callback = join_button_callback
						self.join_view = View(timeout=None)
						self.join_view.add_item(join_button)

						await interaction.followup.send(f"🏟 **Trận đấu bóng đá bắt đầu!** {interaction.user.mention} đã tham gia.\n"
																						f"Số tiền cược: **{bet_amount}** 💰\n"
																						"Cần 1 người chơi nữa! Nhấn nút để tham gia ⚽", view=self.join_view)
						self.join_message = await interaction.original_response()
						self.game_messages.append(self.join_message)

				except Exception as e:
						await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}. Vui lòng thử lại! ⚽")
						self.reset_game_state()

async def setup(bot):
		await bot.add_cog(BongDa(bot))
