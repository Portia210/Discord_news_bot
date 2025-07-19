import discord
from discord.ext import commands
from utils.logger import logger
from discord_utils.message_handler import get_message_handler

class ExportCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="export", description="Export messages from a channel to text file (Admin only)")
    async def export_messages(self, ctx, *, args: str = ""):
        """
        Export messages from a channel to text file
        
        Usage: !export #channel-name @user1 @user2 24
               !export <#channel_id> @user1 24
               !export @user1 24
               !export 24
        Args:
            args: Space-separated arguments (channel, users, hours in any order)
        """
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You need administrator permissions to use this command!")
            return
        
        # Parse arguments
        channel = None
        user_list = []
        hours = 24
        
        if args:
            parts = args.split()
            
            for part in parts:
                # Check if it's a channel mention <#channel_id>
                if part.startswith('<#') and part.endswith('>'):
                    try:
                        channel_id = int(part[2:-1])
                        channel = self.bot.get_channel(channel_id)
                        if not channel:
                            await ctx.send(f"❌ Channel with ID {channel_id} not found.")
                            return
                    except ValueError:
                        await ctx.send(f"❌ Invalid channel mention: {part}")
                        return
                
                # Check if it's a user mention @user
                elif part.startswith('<@') and part.endswith('>'):
                    try:
                        user_id = part.strip('<@!>')
                        user = await self.bot.fetch_user(int(user_id))
                        user_list.append(user)
                    except Exception as e:
                        logger.error(f"Error fetching user: {e}")
                        await ctx.send(f"❌ Could not find user: {part}")
                        return
                
                # Check if it's a number (hours)
                elif part.isdigit():
                    hours = int(part)
                
                # If it's not any of the above, it might be a channel name (but we require #)
                else:
                    await ctx.send(f"❌ Invalid argument: {part}. Use #channel-name, @user, or number for hours.")
                    return
        
        # Use current channel if no channel specified
        if channel is None:
            channel = ctx.channel
        
        user_names = [user.name for user in user_list] if user_list else ["all users"]
        await ctx.send(f"Exporting messages from #{channel.name} for the last {hours} hours (filtering by: {', '.join(user_names)})...")
        
        try:
            # Create message handler
            user_ids = [user.id for user in user_list] if user_list else None
            message_handler = get_message_handler(self.bot)
            
            # Export using the new method with parameters
            filepath = await message_handler.export_channel_to_text(channel.id, hours_back=hours, user_ids=user_ids)
            
            if filepath:
                filter_text = f" (filtered by: {', '.join(user_names)})" if user_list else ""
                await ctx.send(f"✅ Successfully exported #{channel.name} messages{filter_text} to: `{filepath}`")
            else:
                await ctx.send(f"❌ Failed to export messages from #{channel.name}")
                
        except Exception as e:
            logger.error(f"Error in export command: {e}")
            await ctx.send(f"❌ Error exporting messages: {str(e)}")

def setup(bot):
    bot.add_cog(ExportCommands(bot)) 