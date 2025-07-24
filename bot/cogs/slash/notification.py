import discord
from discord.ext import commands
from config import Config
from discord_ui import NotificationView, RESPONSE_EMOJIS





class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="notifications", description="Manage your notification preferences")
    async def notifications_main(self, ctx,
                                 action: str = discord.Option(str, "Choose an action", choices=["edit_subscriptions", "list", "info"])):
        """Main notifications command with subactions"""
        if action == "info":
            await self._show_info(ctx)
        elif action == "list":
            await self._list_roles(ctx)
        else:
            # Show edit subscriptions menu
            await self._edit_subscriptions(ctx)
    
    async def _show_info(self, ctx):
        """Show notification help"""
        embed = discord.Embed(
            title="🔔 How Notification Roles work?",
            description="Use the `/notifications` command to manage your notification roles. For each notification role you have, the bot will mention you when notifications of that type are posted.",
            color=0x0099ff
        )
        embed.add_field(
            name="Edit Subscriptions", 
            value="`/notifications action:edit_subscriptions`\n*Toggle buttons will appear with your current subscriptions pre-selected*", 
            inline=False
        )
        embed.add_field(name="List", value="`/notifications action:list`", inline=False)
        embed.add_field(
            name="Available Types", 
            value=f"**{', **'.join(Config.NOTIFICATION_ROLES.get_names())}**", 
            inline=False
        )
        
        await ctx.respond(embed=embed, ephemeral=True)
    

    async def _edit_subscriptions(self, ctx):
        """Show toggle buttons for editing notification subscriptions with current roles pre-selected"""
        # Get user's current notification roles
        member = ctx.guild.get_member(ctx.author.id)
        current_roles = []
        
        if member:
            for role_obj in Config.NOTIFICATION_ROLES.ALL_ROLES:
                discord_role = discord.utils.get(ctx.guild.roles, name=role_obj.full_name)
                if discord_role and discord_role in member.roles:
                    current_roles.append(role_obj)
        
        embed = discord.Embed(
            title="🔔 Edit Notification Subscriptions",
            description="Your current subscriptions are pre-selected. Click buttons to add or remove notification types:",
            color=0x0099ff
        )
        
        if current_roles:
            current_names = [role.full_name for role in current_roles]
            embed.add_field(
                name="📋 Current Subscriptions",
                value="\n".join([f"• {name}" for name in current_names]),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Current Subscriptions",
                value="None - you're not subscribed to any notifications",
                inline=False
            )
        
        embed.add_field(
            name="💡 How to Use?",
            value="Click the buttons above to select/deselect notification types, then click confirm to save changes!",
            inline=False
        )
        
        # Create button view with current roles pre-selected
        view = NotificationView(ctx.author.id, "edit", current_roles)
        
        await ctx.respond(embed=embed, view=view, ephemeral=True)
    

    

    
    async def _process_subscription_changes(self, interaction, selected_role_name_list: list):
        """Process subscription changes by adding missing roles and removing unselected roles"""
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("❌ I need 'Manage Roles' permission!", ephemeral=False)
                return
            
            member = interaction.guild.get_member(interaction.user.id)
            results = {
                "Added": ("success", []),
                "Removed": ("success", []),
                "Already had": ("info", []),
                "Didn't have": ("info", []),
                "Failed": ("error", [])
            }
            
            # Get all notification roles that should exist
            all_notification_roles = []
            for role_obj in Config.NOTIFICATION_ROLES.ALL_ROLES:
                discord_role = discord.utils.get(interaction.guild.roles, name=role_obj.full_name)
                if not discord_role:
                    try:
                        discord_role = await interaction.guild.create_role(
                            name=role_obj.full_name,
                            color=role_obj.color,
                            reason=f"Notification role for {role_obj.name}"
                        )
                    except Exception as e:
                        results["Failed"][1].append(f"{role_obj.full_name}: {e}")
                        continue
                all_notification_roles.append((role_obj, discord_role))
            
            # Process each notification role
            for role_obj, discord_role in all_notification_roles:
                role_name = role_obj.full_name
                user_has_role = discord_role in member.roles
                user_wants_role = role_obj.name in selected_role_name_list
                
                if user_wants_role and not user_has_role:
                    # User wants the role but doesn't have it - add it
                    try:
                        await member.add_roles(discord_role, reason=f"User subscribed to {role_obj.name} notifications")
                        results["Added"][1].append(role_name)
                    except Exception as e:
                        results["Failed"][1].append(f"{role_name}: {e}")
                
                elif user_wants_role and user_has_role:
                    # User wants the role and already has it
                    results["Already had"][1].append(role_name)
                
                elif not user_wants_role and user_has_role:
                    # User doesn't want the role but has it - remove it
                    try:
                        await member.remove_roles(discord_role, reason=f"User unsubscribed from {role_obj.name} notifications")
                        results["Removed"][1].append(role_name)
                    except Exception as e:
                        results["Failed"][1].append(f"{role_name}: {e}")
                
                elif not user_wants_role and not user_has_role:
                    # User doesn't want the role and doesn't have it
                    results["Didn't have"][1].append(role_name)
            
            response = self._edit_subscriptions_response_message(results)
            await interaction.followup.send(response, ephemeral=False)
            
        except Exception as e:
            print(f"Error in edit subscriptions command: {e}")
            await interaction.followup.send("❌ An error occurred while processing your request.", ephemeral=False)
    
    def _edit_subscriptions_response_message(self, results: dict):
        """Build response message for edit subscriptions operation"""
        # Get all roles that the user now has (Added + Already had)
        current_subscriptions = []
        current_subscriptions.extend(results["Added"][1])  # Newly added roles
        current_subscriptions.extend(results["Already had"][1])  # Roles they already had
        
        if current_subscriptions:
            return f"✅ You are now subscribed to:\n{', '.join(current_subscriptions)}"
        else:
            return "✅ You don't have any subscriptions now."
    

    
    async def _list_roles(self, ctx):
        """List user's notification roles"""
        if not ctx.guild:
            await ctx.respond("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        member = ctx.guild.get_member(ctx.author.id)
        
        embed = discord.Embed(
            title="🔔 Your Notification Roles",
            description="Here are your current notification subscriptions:",
            color=0x00ff00
        )
        
        for role_obj in Config.NOTIFICATION_ROLES.ALL_ROLES:
            role = discord.utils.get(ctx.guild.roles, name=role_obj.full_name)
            status = f"{RESPONSE_EMOJIS['success']} {role_obj.full_name}" if role and role in member.roles else f"{RESPONSE_EMOJIS['error']} {role_obj.full_name}"
            embed.add_field(name="", value=status, inline=False)
        
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(RoleManager(bot)) 