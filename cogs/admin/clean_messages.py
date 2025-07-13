import discord
from discord.ext import commands
import asyncio

class CleanCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="clean", description="Clean messages from the channel")
    async def clean(self, ctx, amount: int = 20):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to use this command!")
            return
            
        if amount > 100:
            await ctx.send("Cannot delete more than 100 messages at once!")
            return
            
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
            await ctx.send(f'✅ Cleaned {len(deleted) - 1} messages', delete_after=3)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

def setup(bot):
    bot.add_cog(CleanCommands(bot)) 