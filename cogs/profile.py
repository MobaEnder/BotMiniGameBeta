import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os

USER_FILE = "data/users.json"
LEVEL_FILE = "data/level.json"


def load_users():
	if not os.path.exists(USER_FILE):
		with open(USER_FILE, "w") as f:
			json.dump({}, f)
	with open(USER_FILE, "r") as f:
		return json.load(f)


def save_users(data):
	with open(USER_FILE, "w") as f:
		json.dump(data, f, indent=4)


def load_levels():
	if not os.path.exists(LEVEL_FILE):
		with open(LEVEL_FILE, "w") as f:
			json.dump({}, f)
	with open(LEVEL_FILE, "r") as f:
		return json.load(f)


def get_user_data(user_id):
	data = load_users()
	return data.get(str(user_id), {})


def get_level_data(user_id):
	data = load_levels()
	uid = str(user_id)
	user = data.get(uid, {})
	xp = user.get("xp", 0)
	level = user.get("level", 1)
	progress = xp % 600
	return level, xp, progress


def get_work_cooldown(user_id):
	user = get_user_data(user_id)
	last_time = datetime.fromisoformat(
	    user.get("last_work", "1970-01-01T00:00:00"))
	time_passed = datetime.utcnow() - last_time
	cooldown = timedelta(hours=1)
	return None if time_passed >= cooldown else cooldown - time_passed


def get_fish_cooldown(user_id):
	user = get_user_data(user_id)
	last_time = datetime.fromisoformat(
	    user.get("last_fish", "1970-01-01T00:00:00"))
	time_passed = datetime.utcnow() - last_time
	cooldown = timedelta(minutes=30)
	return None if time_passed >= cooldown else cooldown - time_passed


def get_miner_cooldown(user_id):
	user = get_user_data(user_id)
	last_time = datetime.fromisoformat(
	    user.get("last_mine", "1970-01-01T00:00:00"))
	time_passed = datetime.utcnow() - last_time
	cooldown = timedelta(minutes=45)
	return None if time_passed >= cooldown else cooldown - time_passed


def get_race_cooldown(user_id):
	user = get_user_data(user_id)
	last_time = datetime.fromisoformat(
			user.get("last_race", "1970-01-01T00:00:00"))
	time_passed = datetime.utcnow() - last_time
	cooldown = timedelta(minutes=15)
	return None if time_passed >= cooldown else cooldown - time_passed


def get_dig_cooldown(user_id):
	user = get_user_data(user_id)
	last_time = datetime.fromisoformat(
			user.get("last_dig", "1970-01-01T00:00:00"))
	time_passed = datetime.utcnow() - last_time
	cooldown = timedelta(minutes=20)
	return None if time_passed >= cooldown else cooldown - time_passed

# ... (phần import và các hàm khác giữ nguyên)

class Profile(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="profile", description="Xem hồ sơ người dùng")
	@app_commands.describe(
			user="Người dùng cần xem (nếu bỏ qua sẽ là chính bạn)")
	async def profile(self,
										interaction: discord.Interaction,
										user: discord.User = None):
		try:
			user = user or interaction.user
			users = load_users()
			level_data = load_levels()
			uid = str(user.id)

			if uid not in users or uid not in level_data:
				await interaction.response.send_message(
						"❌ Người dùng này chưa có dữ liệu.", ephemeral=True)
				return

			user_info = users[uid]
			level_info = level_data[uid]

			job = user_info.get("job", "Chưa có")
			money = user_info.get("money", 0)
			quote = user_info.get("quote", "None")

			level = level_info.get("level", 1)
			xp = level_info.get("xp", 0)
			progress = xp % 600

			def format_cd(cd):
				if not cd:
					return "✅ Sẵn sàng"
				mins, secs = divmod(int(cd.total_seconds()), 60)
				return f"{mins} phút {secs} giây"

			embed = discord.Embed(title=f"🌟 Profile @{user.display_name}",
														color=discord.Color.purple())

			if user.avatar:
				embed.set_thumbnail(url=user.avatar.url)

			embed.add_field(name="💼 Nghề nghiệp", value=job, inline=True)
			embed.add_field(name="📈 Cấp độ", value=str(level), inline=True)
			embed.add_field(name="💰 Tài sản", value=f"🪙 {money:,} xu", inline=True)

			embed.add_field(name="💬 Quote", value=f"“{quote}”", inline=False)

			embed.add_field(
				name="⏳ Cooldown các mini game",
				value=(f"🔨 **Work** : {format_cd(get_work_cooldown(user.id))}\n"
							 f"🎣 **Fish** : {format_cd(get_fish_cooldown(user.id))}\n"
							 f"⛏️ **Miner**: {format_cd(get_miner_cooldown(user.id))}\n"
							 f"🐎 **Race** : {format_cd(get_race_cooldown(user.id))}\n"
							 f"⚒️ **Dig**  : {format_cd(get_dig_cooldown(user.id))}"),
				inline=False)

			# Gửi message và xóa sau 60 giây
			msg = await interaction.response.send_message(embed=embed)
			sent_msg = await interaction.original_response()
			await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=60))
			await sent_msg.delete()

		except Exception as e:
			await interaction.response.send_message(
					f"❌ Lỗi khi hiển thị hồ sơ: `{e}`", ephemeral=True)

	@app_commands.command(name="setquote",
												description="Đặt câu quote cho hồ sơ của bạn")
	@app_commands.describe(quote="Câu quote bạn muốn hiển thị trên hồ sơ")
	async def setquote(self, interaction: discord.Interaction, quote: str):
		data = load_users()
		uid = str(interaction.user.id)
		if uid not in data:
			await interaction.response.send_message("❌ Bạn chưa có hồ sơ!",
																							ephemeral=True)
			return
		data[uid]["quote"] = quote
		save_users(data)
		await interaction.response.send_message(
				f"✅ Quote của bạn đã được cập nhật thành: \"{quote}\"", ephemeral=True)


async def setup(bot):
	await bot.add_cog(Profile(bot))
