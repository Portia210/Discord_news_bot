import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import logger
from news_pdf.pdf_report_generator import PdfReportGenerator
from discord_utils.send_pdf import sendpdf
from config import config
from scheduler import Scheduler, CalendarManager
from scheduler.custom_tasks import CustomTasks

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize scheduler and calendar manager
scheduler = Scheduler()
calendar_manager = CalendarManager(bot, config.channel_ids.investing_bot)
custom_tasks = CustomTasks(calendar_manager)

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
    
    # Initialize and start the scheduler
    try:
        logger.info("✅ Calendar manager initialized successfully!")
        
        # Add custom tasks to the scheduler
        custom_task_list = custom_tasks.get_custom_tasks()
        for task in custom_task_list:
            scheduler.add_task(task)
        logger.info(f"✅ Added {len(custom_task_list)} custom tasks to scheduler")
        
        # Start the scheduler background task
        bot.loop.create_task(scheduler.start())
        logger.info("✅ Scheduler background task started!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize scheduler: {e}")
    
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
        if scheduler:
            await scheduler.stop()
            logger.info("✅ Scheduler stopped gracefully")
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