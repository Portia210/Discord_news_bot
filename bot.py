import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import logger
from news_pdf.pdf_report_generator import PdfReportGenerator
from discord_utils.send_pdf import sendpdf
from config import config
from scheduler_v2 import DiscordScheduler, CalendarManager, TaskDefinitions

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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
        global discord_scheduler, calendar_manager, task_definitions
        
        # Initialize scheduler components
        discord_scheduler = DiscordScheduler(bot, config.channel_ids.investing_bot)
        calendar_manager = CalendarManager(discord_scheduler)
        task_definitions = TaskDefinitions(discord_scheduler, calendar_manager)
        
        logger.info("✅ Scheduler components initialized successfully!")
        
        # Setup all tasks
        task_definitions.setup_all_tasks()
        logger.info("✅ All tasks setup completed")
        
        # Start the scheduler
        discord_scheduler.start()
        logger.info("✅ APScheduler started successfully!")
        
        # Send startup message
        await discord_scheduler.send_alert(
            "🚀 **Bot Started Successfully**\n"
            f"📅 Scheduler active with {discord_scheduler.get_job_count()} tasks\n"
            "🔔 All alerts will be sent to this channel",
            0x00ff00,
            "🤖 Bot Status"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize scheduler: {e}")
        if discord_scheduler:
            await discord_scheduler.send_alert(
                f"❌ **Scheduler Initialization Failed**\nError: {str(e)}",
                0xff0000,
                "🤖 Bot Status"
            )
    
    # # Process and send daily news report
    # pdf_generator = PdfReportGenerator(bot)
    # pdf_success = await pdf_generator.generate_pdf_report()
    # if pdf_success:
    #     await sendpdf(bot, config.channel_ids.python_bot, "news_pdf/output.pdf", "Daily News Report", "daily_news_report.pdf")



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
    if not TOKEN:
        raise ValueError("No Discord token found. Please check your .env file.")
    
    try:
        # Use bot.run() instead of asyncio.run() to avoid loop conflicts
        bot.run(TOKEN)
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