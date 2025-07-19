import discord
from discord.ext import commands

class GreetCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="greet")
    async def greet(self, ctx):
        await ctx.send("Hello! This is a regular command.")

def setup(bot):
    bot.add_cog(GreetCommands(bot)) 