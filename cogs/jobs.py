import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random

JOBS = {
    "nông dân": (20, 50),
    "lập trình viên": (50, 100),
    "ca sĩ": (40, 90),
    "đầu bếp": (30, 70),
    "game thủ": (45, 95),
    "geysax": (150, 205),
}

JOB_CHOICES = {
    "nông dân": "👨‍🌾 Nông dân",
    "lập trình viên": "💻 Lập trình viên",
    "ca sĩ": "🎤 Ca sĩ",
    "đầu bếp": "👨‍🍳 Đầu bếp",
    "game thủ": "🎮 Game thủ",
    "geysax": "🍑 Geysax",
}

class JobSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_doc(self, user_id):
        return self.bot.db.users.find_one({"_id": str(user_id)})

    def update_user_doc(self, user_id, update_data):
        self.bot.db.users.update_one({"_id": str(user_id)}, {"$set": update_data}, upsert=True)

    def increment_money(self, user_id, amount):
        self.bot.db.users.update_one({"_id": str(user_id)}, {"$inc": {"money": amount}}, upsert=True)
        user = self.bot.db.users.find_one({"_id": str(user_id)})
        return user.get("money", 0)

    @app_commands.command(name="setjob", description="Chọn nghề nghiệp để làm việc")
    @app_commands.describe(job="Chọn nghề nghiệp của bạn")
    async def setjob(self, interaction: discord.Interaction, job: str):
        if job not in JOBS:
            await interaction.response.send_message("❌ Nghề bạn chọn không hợp lệ. Hãy dùng gợi ý!", ephemeral=True)
            return

        self.update_user_doc(interaction.user.id, {"job": job})
        await interaction.response.send_message(f"✅ Bạn đã chọn nghề **{JOB_CHOICES[job]}**.")

    @setjob.autocomplete("job")
    async def job_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=emoji_name, value=job_key)
            for job_key, emoji_name in JOB_CHOICES.items()
            if current.lower() in job_key.lower()
        ][:25]

    @app_commands.command(name="work", description="Làm việc để kiếm tiền theo nghề đã chọn")
    async def work(self, interaction: discord.Interaction):
        user_data = self.get_user_doc(interaction.user.id)
        if not user_data:
            await interaction.response.send_message("❌ Bạn chưa có tài khoản! Dùng lệnh `/daily` trước.", ephemeral=True)
            return

        job = user_data.get("job")
        if not job:
            await interaction.response.send_message("❌ Bạn chưa chọn nghề! Dùng lệnh `/setjob` để chọn.", ephemeral=True)
            return

        last_work = user_data.get("last_work", "1970-01-01T00:00:00")
        last_time = datetime.fromisoformat(last_work)
        if datetime.utcnow() - last_time < timedelta(hours=1):
            await interaction.response.send_message("🕒 Bạn cần nghỉ ngơi một chút! Hãy thử lại sau 1 giờ.", ephemeral=True)
            return

        salary = random.randint(*JOBS[job])
        new_balance = self.increment_money(interaction.user.id, salary)
        self.update_user_doc(interaction.user.id, {"last_work": datetime.utcnow().isoformat()})

        await interaction.response.send_message(
            f"💼 Bạn đã làm việc với vai trò **{JOB_CHOICES[job]}** và nhận được **{salary} xu**!\n"
            f"💰 Số dư hiện tại: {new_balance:,} xu."
        )

async def setup(bot):
    await bot.add_cog(JobSystem(bot))
