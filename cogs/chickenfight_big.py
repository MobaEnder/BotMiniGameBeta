import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
from data_manager import get_user, update_balance, add_exp

JOIN_DURATION = 20  # Giây mở cược

class ChickenFightBig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_running = False
        self.players = {}

    @app_commands.command(name="chickenfight_big", description="🐓 Đá gà nhiều người - cược vào Gà Đỏ hoặc Gà Vàng!")
    async def chickenfight_big(self, interaction: discord.Interaction):
        await add_exp(interaction.user.id, 30)  # Tự động cộng EXP khi dùng lệnh

        if self.game_running:
            await interaction.response.send_message("⚠️ Trận đá gà đang diễn ra! Vui lòng chờ.", ephemeral=True)
            return

        self.game_running = True
        self.players = {}

        class JoinChicken(discord.ui.View):
            def __init__(self, parent):
                super().__init__(timeout=JOIN_DURATION)
                self.parent = parent

            @discord.ui.button(label="🔴 Gà Đỏ", style=discord.ButtonStyle.danger)
            async def bet_red(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.parent.handle_join(interaction, "red")

            @discord.ui.button(label="🟡 Gà Vàng", style=discord.ButtonStyle.success)
            async def bet_yellow(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.parent.handle_join(interaction, "yellow")

        async def countdown_message():
            timer_msg = await interaction.followup.send("⏳ Đang mở cược trận đá gà trong 20 giây...", ephemeral=False)
            for i in range(JOIN_DURATION, 0, -5):
                await asyncio.sleep(5)
                await timer_msg.edit(content=f"⏳ Còn {i} giây để đặt cược...")
            return timer_msg

        await interaction.response.send_message(
            "**🐓 CHICKENFIGHT - ĐÁ GÀ TẬP THỂ 🐓**\n"
            "🔴 Gà Đỏ vs 🟡 Gà Vàng\n\n"
            "👉 Nhấn nút bên dưới để cược và chọn số tiền!",
            view=JoinChicken(self),
            ephemeral=False
        )

        await interaction.channel.send("📝 Danh sách người chơi sẽ hiển thị sau khi cược xong...")
        await countdown_message()

        if not self.players:
            await interaction.channel.send("❌ Không có ai tham gia đá gà!", delete_after=10)
            self.game_running = False
            return

        # Kết quả
        winner = random.choice(["red", "yellow"])
        winner_emoji = "🔴" if winner == "red" else "🟡"
        result_lines = [f"🏁 Kết quả: **{winner_emoji} {'Gà Đỏ' if winner == 'red' else 'Gà Vàng'}** chiến thắng!\n"]

        for uid, info in self.players.items():
            user = await self.bot.fetch_user(int(uid))
            bet = info["amount"]
            pick = info["choice"]

            user_data = await get_user(uid)
            if not user_data:
                continue

            if pick == winner:
                await update_balance(uid, bet)
                result_lines.append(f"✅ {user.mention} thắng 🪙 {bet:,} xu")
            else:
                await update_balance(uid, -bet)
                result_lines.append(f"❌ {user.mention} thua 🪙 {bet:,} xu")

        await interaction.channel.send("\n".join(result_lines), delete_after=120)
        self.game_running = False

    async def handle_join(self, interaction: discord.Interaction, choice):
        user = interaction.user
        uid = str(user.id)

        user_data = await get_user(uid)
        if not user_data:
            await interaction.response.send_message("❌ Bạn chưa có tài khoản!", ephemeral=True)
            return

        if uid in self.players:
            await interaction.response.send_message("⚠️ Bạn đã tham gia rồi!", ephemeral=True)
            return

        class BetModal(discord.ui.Modal, title="Nhập số tiền cược"):
            amount = discord.ui.TextInput(label="Số tiền cược", placeholder="VD: 1000", required=True)

            async def on_submit(modal_self, interaction2: discord.Interaction):
                try:
                    amount = int(modal_self.amount.value)
                    if amount <= 0:
                        await interaction2.response.send_message("❌ Số tiền không hợp lệ.", ephemeral=True)
                        return
                    if user_data["money"] < amount:
                        await interaction2.response.send_message("❌ Bạn không đủ tiền!", ephemeral=True)
                        return

                    self.players[uid] = {
                        "name": user.name,
                        "amount": amount,
                        "choice": choice
                    }
                    await interaction2.response.send_message(
                        f"✅ Bạn đã cược **🪙 {amount:,} xu** vào {'🔴 Gà Đỏ' if choice == 'red' else '🟡 Gà Vàng'}!",
                        ephemeral=True
                    )
                except:
                    await interaction2.response.send_message("❌ Lỗi khi đặt cược!", ephemeral=True)

        await interaction.response.send_modal(BetModal())

async def setup(bot):
    await bot.add_cog(ChickenFightBig(bot))
