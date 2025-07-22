import discord
from discord.ext import commands

class TestSlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="testslash2", description="Test if slash commands work")
    async def test_slash(self, ctx):
        await ctx.respond("✅ Slash commands are working!", ephemeral=False)

    @commands.command(name="testtext", description="Test if text commands work")
    async def test_text(self, ctx):
        await ctx.send("✅ Text commands are working!")


def setup(bot):
    bot.add_cog(TestSlashCommands(bot)) 