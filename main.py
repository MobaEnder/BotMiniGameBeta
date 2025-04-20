import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Load cogs
for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
				bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
		print(f'Logged in as {bot.user}')

bot.run(os.getenv("TOKEN"))  # TOKEN phải có trong biến môi trường Railway
