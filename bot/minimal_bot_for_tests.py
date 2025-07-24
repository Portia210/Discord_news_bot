import discord
from discord.ext import commands
import asyncio
from config import Config
from discord_utils.role_utils import get_role_mention
from utils.logger import logger

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    
    # Get the first guild (server) the bot is in
    guild = bot.guilds[0] if bot.guilds else None
    if not guild:
        print("❌ Bot is not in any guilds!")
        return
    
    print(f"📋 Bot is in guild: {guild.name}")
    
    # Get the alert channel (using the channel ID from config)
    alert_channel = bot.get_channel(Config.CHANNEL_IDS.INVESTING_BOT)
    if not alert_channel:
        print("❌ Alert channel not found!")
        return
    
    print(f"📢 Found alert channel: {alert_channel.name}")
    
    # Get the Economic Calendar role mention
    economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
    role_mention = await get_role_mention(bot, economic_role.full_name)
    
    # Send the test message
    test_message = f"🧪 **Test Bot Started**\nThis is a test message to verify role mentions work correctly.\n\n{role_mention}"
    logger.info(f"Test message: {test_message}")
    
    try:
        await alert_channel.send(test_message)
        print("✅ Test message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
    
    # Disconnect after sending the message
    await asyncio.sleep(2)
    await bot.close()
    print("🔌 Bot disconnected.")

# Run the bot
if __name__ == "__main__":
    # Load token from environment or config
    token = Config.TOKENS.DISCORD
    if not token:
        print("❌ Discord token not found!")
        exit(1)
    
    print("🚀 Starting test mention bot...")
    bot.run(token) 