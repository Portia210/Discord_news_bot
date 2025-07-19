import discord
from discord.ext import commands

class SyncCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="sync", description="Sync slash commands (Admin only)")
    async def sync(self, ctx):
        # if ctx.author.guild_permissions.administrator:
        if True:
            try:
                # Use pycord sync method
                await self.bot.sync_commands()
                await ctx.send('Commands synced successfully!')
            except Exception as e:
                await ctx.send(f'Failed to sync commands: {e}')
        else:
            await ctx.send("You don't have permission to use this command!")

def setup(bot):
    bot.add_cog(SyncCommands(bot)) 