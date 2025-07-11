import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import logger
from discord_utils.process_news import process_and_send_news_report


# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Load command cogs
    await load_cogs()
    
    # Sync slash commands globally using pycord method
    try:
        await bot.sync_commands()
        logger.info("Commands synced successfully!")
        # Print the available slash commands for debugging
        slash_commands = [cmd.name for cmd in bot.application_commands]
        text_commands = [cmd.name for cmd in bot.commands]
        logger.info(f"Available slash commands: {slash_commands}")
        logger.info(f"Available text commands: {text_commands}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    # Process and send daily news report
    await process_and_send_news_report(bot) 



async def load_cogs():
    """Load all command cogs"""
    cogs = [
        "cogs.slash.hello",
        "cogs.slash.ping", 
        "cogs.slash.sync",
        "cogs.slash.test",
        "cogs.text.greet",
        "cogs.admin.export"
    ]
    
    loaded_cogs = []
    for cog in cogs:
        try:
            bot.load_extension(cog)
            loaded_cogs.append(cog)
            # logger.info(f"✅ Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"❌ Failed to load cog {cog}: {e}")
    
    logger.info(f"Successfully loaded {len(loaded_cogs)}/{len(cogs)} cogs")
    return loaded_cogs

def main():
    """Main entry point"""
    if not TOKEN:
        raise ValueError("No Discord token found. Please check your .env file.")
    
    try:
        # Use bot.run() instead of asyncio.run() to avoid loop conflicts
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user (Ctrl+C)")
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    main()