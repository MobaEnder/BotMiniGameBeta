import discord
from discord import app_commands
from discord.ext import commands
from data.data_manager import get_balance, update_balance


class Transfer(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="transfer",
	                      description="Chuyển tiền cho người dùng khác")
	@app_commands.describe(member="Người nhận", amount="Số tiền muốn chuyển")
	async def transfer(self, interaction: discord.Interaction,
	                   member: discord.Member, amount: int):
		sender_id = interaction.user.id
		receiver_id = member.id

		if member.bot:
			await interaction.response.send_message(
			    "❌ Bạn không thể chuyển tiền cho bot!", ephemeral=True)
			return

		if amount <= 0:
			await interaction.response.send_message("❌ Số tiền phải lớn hơn 0!",
			                                        ephemeral=True)
			return

		if sender_id == receiver_id:
			await interaction.response.send_message(
			    "❌ Bạn không thể chuyển tiền cho chính mình!", ephemeral=True)
			return

		sender_balance = get_balance(sender_id)
		if sender_balance < amount:
			await interaction.response.send_message("❌ Bạn không đủ tiền để chuyển!",
			                                        ephemeral=True)
			return

		update_balance(sender_id, -amount)
		new_balance = update_balance(receiver_id, amount)

		await interaction.response.send_message(
		    f"💸 Bạn đã chuyển **{amount} xu** cho {member.mention}.\n"
		    f"💰 Số dư còn lại của bạn là **{sender_balance - amount} xu**.")


async def setup(bot):
	await bot.add_cog(Transfer(bot))
