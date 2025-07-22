import discord
from discord.ext import commands

# Define notification types at module level for autocomplete
NOTIFICATION_TYPES = {
    "live_news": "📰 Live News",
    "news_report": "📊 News Report",
    "economic_events": "📈 Economic Events"
}

async def notification_autocomplete(ctx: discord.AutocompleteContext):
    """Provide autocomplete suggestions for notification types"""
    current_input = ctx.value.lower()
    
    # Get available types that haven't been typed yet
    already_typed = [t.strip() for t in current_input.split() if t.strip()]
    available_types = [t for t in NOTIFICATION_TYPES.keys() if t not in already_typed]
    
    # Filter based on current input
    if current_input:
        # If the user is typing a partial word, suggest completions
        last_word = current_input.split()[-1] if current_input.split() else ""
        suggestions = [t for t in available_types if t.startswith(last_word)]
        
        # If current input ends with space, show all remaining options
        if current_input.endswith(" "):
            suggestions = available_types
    else:
        suggestions = list(NOTIFICATION_TYPES.keys())
    
    return suggestions[:25]  # Discord limit

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Use the module-level notification types
        self.notification_types = NOTIFICATION_TYPES
    
    # Create a slash command group for notifications
    notifications = discord.SlashCommandGroup("notifications", "Manage notification roles")
    
    @notifications.command(name="info", description="Show notification help")
    async def info(self, ctx):
        embed = discord.Embed(
            title="🔔 Notification Role Manager",
            description="Use these commands to manage your notification roles:",
            color=0x0099ff
        )
        embed.add_field(
            name="Subscribe", 
            value="`/notifications subscribe types: live_news news_report`\n*You can specify multiple types separated by spaces*", 
            inline=False
        )
        embed.add_field(
            name="Unsubscribe", 
            value="`/notifications unsubscribe types: live_news economic_events`\n*You can specify multiple types separated by spaces*", 
            inline=False
        )
        embed.add_field(name="List", value="`/notifications list`", inline=False)
        embed.add_field(
            name="Available Types", 
            value="**live_news**, **news_report**, **economic_events**", 
            inline=False
        )
        embed.add_field(
            name="Examples", 
            value="• `/notifications subscribe types: live_news`\n• `/notifications subscribe types: live_news news_report`\n• `/notifications unsubscribe types: economic_events`", 
            inline=False
        )
        embed.add_field(
            name="💡 Pro Tip",
            value="Use autocomplete! Start typing and Discord will suggest available options.",
            inline=False
        )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @notifications.command(name="subscribe", description="Subscribe to notification role(s)")
    async def subscribe(self, ctx, 
                       types: str = discord.Option(str, "Notification types (space-separated): live_news news_report economic_events", 
                                                   autocomplete=notification_autocomplete)):
        """Subscribe to one or more notification roles"""
        try:
            if not ctx.guild:
                await ctx.respond("❌ This command can only be used in a server!", ephemeral=False)
                return
            
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.respond("❌ I need 'Manage Roles' permission!", ephemeral=False)
                return
            
            # Parse space-separated types
            requested_types = [t.strip().lower() for t in types.split() if t.strip()]
            invalid_types = [t for t in requested_types if t not in self.notification_types]
            
            if invalid_types:
                await ctx.respond(f"❌ Invalid types: {', '.join(invalid_types)}\nAvailable: {', '.join(self.notification_types.keys())}", ephemeral=False)
                return
            
            member = ctx.guild.get_member(ctx.author.id)
            added_roles = []
            already_had = []
            failed_roles = []
            
            for notif_type in requested_types:
                role_name = self.notification_types[notif_type]
                
                # Get or create the role
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if not role:
                    try:
                        color = self._get_role_color(notif_type)
                        role = await ctx.guild.create_role(
                            name=role_name,
                            color=color,
                            reason=f"Notification role for {notif_type}"
                        )
                    except Exception as e:
                        failed_roles.append(f"{role_name}: {e}")
                        continue
                
                # Add role to user
                try:
                    if role in member.roles:
                        already_had.append(role_name)
                    else:
                        await member.add_roles(role, reason=f"User subscribed to {notif_type} notifications")
                        added_roles.append(role_name)
                except Exception as e:
                    failed_roles.append(f"{role_name}: {e}")
            
            # Build response message
            response_parts = []
            if added_roles:
                response_parts.append(f"✅ **Added roles:** {', '.join(added_roles)}")
            if already_had:
                response_parts.append(f"ℹ️ **Already had:** {', '.join(already_had)}")
            if failed_roles:
                response_parts.append(f"❌ **Failed:** {', '.join(failed_roles)}")
            
            if not response_parts:
                response_parts.append("❌ No roles were processed.")
            
            await ctx.respond('\n'.join(response_parts), ephemeral=False)
            
        except Exception as e:
            print(f"Error in subscribe command: {e}")
            await ctx.respond("❌ An error occurred while processing your request.", ephemeral=False)
    
    @notifications.command(name="unsubscribe", description="Unsubscribe from notification role(s)")
    async def unsubscribe(self, ctx, 
                         types: str = discord.Option(str, "Notification types (space-separated): live_news news_report economic_events",
                                                     autocomplete=notification_autocomplete)):
        """Unsubscribe from one or more notification roles"""
        try:
            if not ctx.guild:
                await ctx.respond("❌ This command can only be used in a server!", ephemeral=False)
                return
            
            # Parse space-separated types
            requested_types = [t.strip().lower() for t in types.split() if t.strip()]
            invalid_types = [t for t in requested_types if t not in self.notification_types]
            
            if invalid_types:
                await ctx.respond(f"❌ Invalid types: {', '.join(invalid_types)}\nAvailable: {', '.join(self.notification_types.keys())}", ephemeral=False)
                return
            
            member = ctx.guild.get_member(ctx.author.id)
            removed_roles = []
            didnt_have = []
            missing_roles = []
            failed_roles = []
            
            for notif_type in requested_types:
                role_name = self.notification_types[notif_type]
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                
                if not role:
                    missing_roles.append(role_name)
                    continue
                
                try:
                    if role not in member.roles:
                        didnt_have.append(role_name)
                    else:
                        await member.remove_roles(role, reason=f"User unsubscribed from {notif_type} notifications")
                        removed_roles.append(role_name)
                except Exception as e:
                    failed_roles.append(f"{role_name}: {e}")
            
            # Build response message
            response_parts = []
            if removed_roles:
                response_parts.append(f"✅ **Removed roles:** {', '.join(removed_roles)}")
            if didnt_have:
                response_parts.append(f"ℹ️ **Didn't have:** {', '.join(didnt_have)}")
            if missing_roles:
                response_parts.append(f"⚠️ **Role doesn't exist:** {', '.join(missing_roles)}")
            if failed_roles:
                response_parts.append(f"❌ **Failed:** {', '.join(failed_roles)}")
            
            if not response_parts:
                response_parts.append("❌ No roles were processed.")
            
            await ctx.respond('\n'.join(response_parts), ephemeral=False)
            
        except Exception as e:
            print(f"Error in unsubscribe command: {e}")
            await ctx.respond("❌ An error occurred while processing your request.", ephemeral=False)
    
    @notifications.command(name="list", description="List your notification roles")
    async def list_roles(self, ctx):
        """List user's notification roles"""
        if not ctx.guild:
            await ctx.respond("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        member = ctx.guild.get_member(ctx.author.id)
        subscribed = []
        
        for notif_type, role_name in self.notification_types.items():
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role and role in member.roles:
                subscribed.append(f"✅ {role_name}")
            else:
                subscribed.append(f"❌ {role_name}")
        
        embed = discord.Embed(
            title="🔔 Your Notification Roles",
            description="Here are your current notification roles:",
            color=0x00ff00
        )
        
        for status in subscribed:
            embed.add_field(name="", value=status, inline=False)
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    def _get_role_color(self, notif_type: str) -> discord.Color:
        """Get color for notification role"""
        colors = {
            "live_news": discord.Color.red(),
            "news_report": discord.Color.blue(),
            "economic_events": discord.Color.gold()
        }
        return colors.get(notif_type, discord.Color.default())

def setup(bot):
    bot.add_cog(RoleManager(bot)) 