import os
import discord
from discord.ext import commands
from utils.logger import logger
from config import Config, ENABLE_PROXY, REMOTE_SERVER
import asyncio
from news_pdf.news_report import NewsReport

logger.info(f"REMOTE_SERVER? {REMOTE_SERVER}")
logger.info(f"ENABLE_PROXY? {ENABLE_PROXY}")

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents.guilds = True  # Required for slash commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize scheduler
discord_scheduler = None


@bot.event
async def on_application_command_error(ctx, error):
    logger.error(f"❌ Error in command {ctx.command.name}: {error}")
    await ctx.send(f"❌ Error: {error}")

@bot.event
async def on_disconnect():
    logger.warning("🔌 Bot disconnected")

@bot.event
async def on_resumed():
    logger.warning("🔄 Bot resumed")

# Add comprehensive monitoring
@bot.event
async def on_application_command(ctx):
    # logger.info(f"🎯 Slash command used: /{ctx.command.name} by {ctx.author}")
    # logger.info(f"📊 Commands available before: {[cmd.name for cmd in bot.application_commands]}")
    pass

@bot.event
async def on_application_command_completion(ctx):
    logger.info(f"✅ Command /{ctx.command.name} completed successfully")
    # logger.info(f"📊 Commands available after: {[cmd.name for cmd in bot.application_commands]}")
    
    # Check bot permissions after command
    # guild = ctx.guild
    # bot_permissions = guild.me.guild_permissions
    # logger.info(f"🔐 Bot permissions - Use App Commands: {bot_permissions.use_application_commands}")
    # logger.info(f"🔐 Bot permissions - Manage Roles: {bot_permissions.manage_roles}")
    # logger.info(f"👑 Bot top role: {guild.me.top_role.name} (position: {guild.me.top_role.position})")

@bot.event
async def on_guild_update(before, after):
    logger.warning(f"🏠 Guild updated: {after.name}")
    logger.info(f"📊 Bot role position: {after.me.top_role.position}")
    logger.info(f"📊 Commands still available: {[cmd.name for cmd in bot.application_commands]}")

@bot.event
async def on_member_update(before, after):
    if after.id == bot.user.id:  # Bot itself was updated
        logger.warning(f"🤖 Bot member updated - roles changed!")
        logger.info(f"📊 Bot roles before: {[r.name for r in before.roles]}")
        logger.info(f"📊 Bot roles after: {[r.name for r in after.roles]}")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"❌ Bot error in event {event}: {args}")
    import traceback
    logger.error(f"❌ Full traceback: {traceback.format_exc()}")


@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Load command cogs
    await load_cogs()
    
    # Sync slash commands to specific guilds for faster updates
    try:
        logger.info(f"📦 Loaded cogs: {[cog for cog in bot.cogs.keys()]}")
        
        bot_guild_ids = [guild.id for guild in bot.guilds]
        await bot.sync_commands(guild_ids=bot_guild_ids)
        
        slash_commands = [cmd.name for cmd in bot.application_commands]
        text_commands = [cmd.name for cmd in bot.commands]
        logger.info(f"🔧 Available slash commands: {slash_commands}")
        logger.info(f"🔧 Available text commands: {text_commands}")
        
        from discord_utils.message_handler import get_message_handler



        news_report = NewsReport(bot, Config.TIMEZONES.APP_TIMEZONE)
        await news_report.generate_full_json_report("auto", 35)
        await news_report.send_report_to_discord(Config.CHANNEL_IDS.MARKET_NEWS, Config.NOTIFICATION_ROLES.NEWS_REPORT)

            
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")
    



async def load_cogs():
    """Load all command cogs"""
    logger.info(f"📦 Currently loaded cogs: {list(bot.cogs.keys())}")
    
    cogs = [
        "cogs.slash.test_slash",
        "cogs.slash.stock_info",
        "cogs.slash.notification",
        "cogs.text.hello",
    ]
    
    loaded_cogs = []
    for cog in cogs:
        try:
            if cog.split('.')[-1] in [c.__class__.__name__.lower() for c in bot.cogs.values()]:
                logger.warning(f"⚠️  Cog {cog} already loaded! Skipping...")
                continue
            bot.load_extension(cog)
            loaded_cogs.append(cog)
        except Exception as e:
            logger.error(f"❌ Failed to load cog {cog}: {e}")
    
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