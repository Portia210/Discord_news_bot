import discord
from discord.ext import commands

class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="test", description="Simple test command")
    async def test(self, ctx):
        await ctx.send("Test command works! ✅")

def setup(bot):
    bot.add_cog(TestCommands(bot)) 