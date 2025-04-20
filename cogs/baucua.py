import discord
from discord import app_commands
from discord.ext import commands
import random
from data_manager import get_balance, update_balance


choices_dict = {
		"bầu": "🍐",
		"cua": "🦀",
		"tôm": "🦐",
		"cá": "🐟",
		"nai": "🦌",
		"gà": "🐓"
}


class BauCua(commands.Cog):
		def __init__(self, bot: commands.Bot):
				self.bot = bot

		# Gợi ý lựa chọn con vật
		async def autocomplete_choice(self, interaction: discord.Interaction, current: str):
				return [
						app_commands.Choice(name=f"{name} {emoji}", value=name)
						for name, emoji in choices_dict.items()
						if current.lower() in name.lower()
				]

		@app_commands.command(name="baucua", description="Chơi mini game bầu cua")
		@app_commands.describe(
				amount="Số tiền bạn muốn cược",
				choice="Chọn bầu / cua / tôm / cá / nai / gà"
		)
		@app_commands.autocomplete(choice=autocomplete_choice)
		async def baucua(self, interaction: discord.Interaction, amount: int, choice: str):
				await interaction.response.defer()

				choice = choice.lower()
				if choice not in choices_dict:
						await interaction.followup.send(
								f"❌ Lựa chọn không hợp lệ! Hãy chọn một trong: {', '.join(choices_dict.keys())}",
								ephemeral=True
						)
						return

				user_id = interaction.user.id
				balance = get_balance(user_id)

				if amount > balance:
						await interaction.followup.send("❌ Bạn không đủ tiền để cược!", ephemeral=True)
						return

				result = random.choices(list(choices_dict.keys()), k=3)
				win_count = result.count(choice)

				if win_count > 0:
						winnings = amount * win_count
						new_balance = update_balance(user_id, winnings)
						msg = (
								f"🎉 Kết quả: {' '.join(choices_dict[r] for r in result)}\n"
								f"✅ Bạn thắng {winnings} xu!\n"
								f"💰 Số dư hiện tại: {new_balance} xu"
						)
				else:
						new_balance = update_balance(user_id, -amount)
						msg = (
								f"💔 Kết quả: {' '.join(choices_dict[r] for r in result)}\n"
								f"❌ Bạn đã thua {amount} xu!\n"
								f"💰 Số dư hiện tại: {new_balance} xu"
						)

				await interaction.followup.send(msg)


async def setup(bot: commands.Bot):
		await bot.add_cog(BauCua(bot))
