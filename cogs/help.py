import discord
import asyncio
from discord import app_commands
from discord.ext import commands


class HelpView(discord.ui.View):
	def __init__(self, embeds, timeout=180):
		super().__init__(timeout=timeout)
		self.embeds = embeds
		self.current = 0

	async def update_message(self, interaction):
		for item in self.children:
			if isinstance(item, discord.ui.Button):
				item.disabled = False
		if self.current == 0:
			self.children[0].disabled = True
		if self.current == len(self.embeds) - 1:
			self.children[1].disabled = True

		await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

	@discord.ui.button(label="⬅️ Trước", style=discord.ButtonStyle.blurple, disabled=True)
	async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.current > 0:
			self.current -= 1
			await self.update_message(interaction)

	@discord.ui.button(label="Tiếp ➡️", style=discord.ButtonStyle.blurple)
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.current < len(self.embeds) - 1:
			self.current += 1
			await self.update_message(interaction)


class HelpCommand(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="help", description="Xem danh sách các lệnh có sẵn")
	async def help(self, interaction: discord.Interaction):
		embeds = []

		# Trang 1: Kinh tế và hồ sơ
		embed1 = discord.Embed(
				title="📘 Danh sách Lệnh - Trang 1/3",
				description="💰 **Lệnh về Kinh tế & Hồ sơ người chơi:**",
				color=discord.Color.blue())
		embed1.add_field(name="💼 /setjob", value="Chọn nghề nghiệp của bạn.", inline=False)
		embed1.add_field(name="💳 /balance", value="Xem số dư tài khoản hiện tại.", inline=False)
		embed1.add_field(name="🎁 /daily", value="Nhận tiền mỗi ngày (24h cooldown).", inline=False)
		embed1.add_field(name="🛠️ /work", value="Làm việc để kiếm tiền. Có nhiều nghề khác nhau!", inline=False)
		embed1.add_field(name="🧍 /profile", value="Xem hồ sơ: nghề nghiệp, cấp độ, số dư, cooldown game, v.v.", inline=False)
		embed1.add_field(name="📈 /rank", value="Xem cấp độ, XP và bảng xếp hạng.", inline=False)
		embed1.add_field(name="🔁 /transfer", value="Chuyển tiền cho người dùng khác.", inline=False)
		embeds.append(embed1)

		# Trang 2: Mini-games thường
		embed2 = discord.Embed(
				title="🎮 Danh sách Lệnh - Trang 2/3",
				description="🎲 **Mini-games & Lệnh giải trí:**",
				color=discord.Color.purple())
		embed2.add_field(name="🦀 /baucua", value="Chơi mini-game Bầu Cua và thử vận may!", inline=False)
		embed2.add_field(name="🎲 /taixiu_low", value="Chơi Tài/Xỉu đơn giản bằng nút bấm.", inline=False)
		embed2.add_field(name="🧑‍🤝‍🧑 /taixiu_big", value="Chơi Tài/Xỉu nhiều người cùng lúc!", inline=False)
		embed2.add_field(name="⛏️ /miner", value="Đào quặng, có thể gặp kho báu hoặc thất bại.", inline=False)
		embed2.add_field(name="🐟 /fish", value="Câu cá nhận phần thưởng ngẫu nhiên. Có cá hiếm!", inline=False)
		embed2.add_field(name="🪙 /dig", value="Đào kho báu để nhận xu (cooldown 20 phút).", inline=False)
		embed2.add_field(name="🏇 /race", value="Tham gia đua ngựa, cược vào con thắng!", inline=False)
		embed2.add_field(name="📢 /ping", value="Gọi người được tag liên tục 10 lần!", inline=False)
		embeds.append(embed2)

		# Trang 3: Mini-games mới
		embed3 = discord.Embed(
				title="🎯 Danh sách Lệnh - Trang 3/3",
				description="🆕 **Các trò chơi và lệnh mới thêm:**",
				color=discord.Color.orange())
		embed3.add_field(name="🎰 /xungxeng", value="Quay xèng may mắn, có thể trúng lớn!", inline=False)
		embed3.add_field(name="🎯 /lodemienbac", value="Đoán số 1-10, đoán 3 số, trúng x4 tiền!", inline=False)
		embed3.add_field(name="🐍 /snakegame", value="Leo thang ăn xu, rớt là mất trắng!", inline=False)
		embed3.add_field(name="💣 /bombdefuse", value="Gỡ bom ngẫu nhiên, sai là nổ banh xác!", inline=False)
		embed3.add_field(name="🐔 /chickenfight_low", value="Đá gà 1v1 bằng nút bấm, cược đơn giản!", inline=False)
		embed3.add_field(name="🐓 /chickenfight_big", value="Đá gà nhiều người cùng đặt cược!", inline=False)
		embeds.append(embed3)

		# Gửi message và tự xóa sau 30s
		message = await interaction.response.send_message(
				embed=embeds[0],
				view=HelpView(embeds),
				ephemeral=False
		)
		await asyncio.sleep(30)
		try:
			msg = await interaction.original_response()
			await msg.delete()
		except discord.NotFound:
			pass


async def setup(bot):
	await bot.add_cog(HelpCommand(bot))
