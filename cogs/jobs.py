import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta
import json
import os

DATA_FILE = "data/users.json"

JOBS = {
		"nông dân": (20, 50),
		"lập trình viên": (50, 100),
		"ca sĩ": (40, 90),
		"đầu bếp": (30, 70),
		"game thủ": (45, 95),
		"geysax": (150, 205),
}

# Gợi ý nghề hiển thị emoji
JOB_CHOICES = {
		"nông dân": "👨‍🌾 Nông dân",
		"lập trình viên": "💻 Lập trình viên",
		"ca sĩ": "🎤 Ca sĩ",
		"đầu bếp": "👨‍🍳 Đầu bếp",
		"game thủ": "🎮 Game thủ",
		"geysax": "🍑 Geysax",
}

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
		uid = str(user_id)
		if uid not in data:
				data[uid] = {
						"money": 0,
						"last_work": "1970-01-01T00:00:00",
						"job": None
				}
				save_data(data)
		return data[uid]

def update_user(user_id, key, value):
		data = load_data()
		uid = str(user_id)
		user = get_user(user_id)
		user[key] = value
		data[uid] = user
		save_data(data)

def update_money(user_id, amount):
		data = load_data()
		uid = str(user_id)
		user = get_user(user_id)
		user["money"] += amount
		data[uid] = user
		save_data(data)
		return user["money"]

def can_work(user_id):
		user = get_user(user_id)
		last_time = datetime.fromisoformat(user.get("last_work", "1970-01-01T00:00:00"))
		return datetime.utcnow() - last_time >= timedelta(hours=1)

class JobSystem(commands.Cog):
		def __init__(self, bot):
				self.bot = bot

		@app_commands.command(name="setjob", description="Chọn nghề nghiệp để làm việc")
		@app_commands.describe(job="Chọn nghề nghiệp của bạn")
		async def setjob(self, interaction: discord.Interaction, job: str):
				if job not in JOBS:
						return await interaction.response.send_message(
								"❌ Nghề bạn chọn không hợp lệ. Hãy dùng gợi ý!",
								ephemeral=True
						)

				update_user(interaction.user.id, "job", job)
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
				user = get_user(interaction.user.id)
				job = user.get("job")

				if not job:
						return await interaction.response.send_message(
								"❌ Bạn chưa chọn nghề! Dùng lệnh `/setjob` để chọn.",
								ephemeral=True
						)

				if not can_work(interaction.user.id):
						return await interaction.response.send_message(
								"🕒 Bạn cần nghỉ ngơi một chút! Hãy thử lại sau 1 giờ.",
								ephemeral=True
						)

				salary = random.randint(*JOBS[job])
				new_balance = update_money(interaction.user.id, salary)
				update_user(interaction.user.id, "last_work", datetime.utcnow().isoformat())

				await interaction.response.send_message(
						f"💼 Bạn đã làm việc với vai trò **{JOB_CHOICES[job]}** và nhận được **{salary} xu**!\n"
						f"💰 Số dư hiện tại: {new_balance} xu."
				)

async def setup(bot):
		await bot.add_cog(JobSystem(bot))
