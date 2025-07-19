import os
import discord
from discord.ext import commands
from utils.logger import logger
from config import Config
from scheduler_v2 import DiscordScheduler, TaskDefinitions
import threading
from website.server import start_web_server


# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize new scheduler components
discord_scheduler = None
calendar_manager = None
task_definitions = None



@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Start the web server in a background thread
    try:
        web_server_thread = start_web_server(host='0.0.0.0', port=5000, debug=False)
        logger.info("✅ Web server started successfully in background thread!")
    except Exception as e:
        logger.error(f"❌ Failed to start web server: {e}")
    
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
    
    # Initialize and start the new scheduler
    try:
        global discord_scheduler, task_definitions
        
        # Initialize scheduler components
        discord_scheduler = DiscordScheduler(bot, Config.CHANNEL_IDS.PYTHON_BOT, Config.CHANNEL_IDS.DEV)
        task_definitions = TaskDefinitions(discord_scheduler)
        
        logger.info("✅ Scheduler components initialized successfully!")
        
        # Setup all tasks
        task_definitions.setup_all_tasks()
        logger.info("✅ All tasks setup completed")
        
        # Start the scheduler
        discord_scheduler.start()
        logger.info("✅ APScheduler started successfully!")
        
        # Send bot startup message to dev channel
        await discord_scheduler.send_dev_alert(
            "🚀 **Bot Started Successfully**\n"
            "🔔 Dev alerts will be sent to this channel\n"
            "📊 Data alerts will be sent to the main channel\n"
            "🌐 Web server running on port 5000",
            0x00ff00,
            "🤖 Bot Status"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize scheduler: {e}")
        if discord_scheduler:
            await discord_scheduler.send_dev_alert(
                f"❌ **Scheduler Initialization Failed**\nError: {str(e)}",
                0xff0000,
                "🤖 Bot Status"
            )


async def load_cogs():
    """Load all command cogs"""
    cogs = [
        "cogs.slash.hello",
        "cogs.slash.ping", 
        "cogs.slash.sync",
        "cogs.slash.test",
        "cogs.text.greet",
        "cogs.admin.export",
        "cogs.admin.clean_messages"
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

async def cleanup():
    """Cleanup function to stop scheduler gracefully"""
    try:
        if discord_scheduler:
            discord_scheduler.stop()
            logger.info("✅ APScheduler stopped gracefully")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {e}")

def main():
    """Main entry point"""
    if not Config.TOKENS.DISCORD:
        raise ValueError("No Discord token found. Please check your .env file.")
    
    try:
        # Use bot.run() instead of asyncio.run() to avoid loop conflicts
        bot.run(Config.TOKENS.DISCORD)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user (Ctrl+C)")
        logger.info("Shutting down gracefully...")
        # Run cleanup in the event loop
        import asyncio
        try:
            asyncio.run(cleanup())
        except RuntimeError:
            # If there's already a running event loop, use it
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(cleanup())
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    main()