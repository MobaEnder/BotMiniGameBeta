import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')
    print("✅ Slash commands synced.")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCOD_TOKEN"))

asyncio.run(main())
