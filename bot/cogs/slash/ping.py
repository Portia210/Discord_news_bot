import discord
from discord.ext import commands

class PingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping", description="Check bot's latency")
    async def ping(self, ctx):
        await ctx.send(f'Pong! Latency: {round(self.bot.latency * 1000)}ms')

def setup(bot):
    bot.add_cog(PingCommands(bot)) 