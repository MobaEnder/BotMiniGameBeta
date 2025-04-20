import discord
from discord.ext import commands
import asyncio
import os
import json

# Setup intents
intents = discord.Intents.default()
intents.message_content = True  # Quan trọng nếu cần xử lý nội dung tin nhắn
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Slash commands synced: {len(synced)} lệnh.")
    except Exception as e:
        print("❌ Lỗi sync:", e)

async def main():
    async with bot:
        # Load các cogs
        cogs = [
            "cogs.baucua", "cogs.economy", "cogs.leaderboard", "cogs.transfer",
            "cogs.jobs", "cogs.help", "cogs.profile", "cogs.fishing",
            "cogs.miner", "cogs.taixiu_low", "cogs.taixiu_big", "cogs.rank",
            "cogs.level_system", "cogs.ping", "cogs.dig", "cogs.race",
            "cogs.xungxeng", "cogs.lodemienbac", "cogs.snakegame", "cogs.goboms",
            "cogs.chickenfight_low", "cogs.chickenfight_big", "cogs.bongda"
        ]
        for cog in cogs:
            try:
                await bot.load_extension(cog)
                print(f"✅ Loaded cog: {cog}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog}: {type(e).__name__} - {e}")

        # Kiểm tra token trước khi khởi động
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("❗ DISCORD_TOKEN environment variable is not set!")
        await bot.start(token)

# Khởi chạy bot
asyncio.run(main())
