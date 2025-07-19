import discord
from discord.ext import commands

class HelloCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="hello", description="Responds with a friendly hello message")
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}! 👋')

def setup(bot):
    bot.add_cog(HelloCommands(bot)) 