import discord
from discord import app_commands
from discord.ext import commands
import random
from data_manager import get_user, update_balance, add_exp, get_level_info

choices_dict = {
    "bầu": "🍐",
    "cua": "🦀",
    "tôm": "🦐",
    "cá": "🐟",
    "nai": "🦌",
    "gà": "🐓"
}

async def autocomplete_choice(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=f"{name} {emoji}", value=name)
        for name, emoji in choices_dict.items()
        if current.lower() in name.lower()
    ]

class BauCua(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="baucua", description="Chơi mini game bầu cua")
    @app_commands.describe(
        amount="Số tiền bạn muốn cược",
        choice="Chọn bầu / cua / tôm / cá / nai / gà"
    )
    @app_commands.autocomplete(choice=autocomplete_choice)
    async def baucua(self, interaction: discord.Interaction, amount: int, choice: str):
        await interaction.response.defer()
        user_id = interaction.user.id
        user = get_user(user_id)
        balance = user.get("money", 0)

        choice = choice.lower()
        if choice not in choices_dict:
            await interaction.followup.send(
                f"❌ Lựa chọn không hợp lệ! Hãy chọn một trong: {', '.join(choices_dict.keys())}",
                ephemeral=True
            )
            return

        if amount <= 0:
            await interaction.followup.send("❌ Số tiền cược phải lớn hơn 0!", ephemeral=True)
            return

        if amount > balance:
            await interaction.followup.send("❌ Bạn không đủ tiền để cược!", ephemeral=True)
            return

        result = random.choices(list(choices_dict.keys()), k=3)
        win_count = result.count(choice)

        if win_count > 0:
            winnings = amount * win_count
            new_balance = update_balance(user_id, winnings)
            outcome_text = f"✅ Bạn thắng {winnings} xu!"
        else:
            new_balance = update_balance(user_id, -amount)
            outcome_text = f"❌ Bạn đã thua {amount} xu!"

        # Thêm EXP mỗi lần chơi
        exp, level = add_exp(user_id, 30)
        level_info = get_level_info(user_id)

        embed = discord.Embed(
            title="🎲 Bầu Cua Kết Quả",
            description=(
                f"Kết quả: {' '.join(choices_dict[r] for r in result)}\n"
                f"{outcome_text}\n\n"
                f"💰 Số dư: **{new_balance} xu**\n"
                f"⭐ EXP: **{level_info['exp']} / {level_info['next_level_exp']}**\n"
                f"🏅 Cấp độ: **{level_info['level']}**"
            ),
            color=discord.Color.green() if win_count > 0 else discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(BauCua(bot))
