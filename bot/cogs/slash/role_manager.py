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
    current_input = ctx.value
    
    # Split current input into words
    words = current_input.split()
    
    # Get already selected types (all complete words)
    selected_types = []
    partial_word = ""
    
    if words:
        # Check if input ends with space (user finished typing a word)
        if current_input.endswith(" "):
            # All words are complete
            selected_types = [w for w in words if w in NOTIFICATION_TYPES]
            partial_word = ""
        else:
            # Last word might be partial
            selected_types = [w for w in words[:-1] if w in NOTIFICATION_TYPES]
            partial_word = words[-1].lower()
    
    # Get available types that haven't been selected yet
    available_types = [t for t in NOTIFICATION_TYPES.keys() if t not in selected_types]
    
    # Build suggestions based on current state
    suggestions = []
    
    if not current_input:
        # No input, show individual options
        suggestions = list(NOTIFICATION_TYPES.keys())
    elif current_input.endswith(" "):
        # User finished a word, show options to add
        base = current_input
        for option in available_types:
            suggestions.append(f"{base}{option}")
    else:
        # User is typing, filter and complete
        if partial_word:
            # Filter available types by partial word
            matching_types = [t for t in available_types if t.startswith(partial_word)]
            
            if matching_types:
                # Build completion suggestions
                base = " ".join(words[:-1]) + (" " if len(words) > 1 else "")
                for option in matching_types:
                    suggestions.append(f"{base}{option}")
            else:
                # No matches, show all available
                base = current_input + " "
                for option in available_types:
                    suggestions.append(f"{base}{option}")
        else:
            # Empty partial word, show all available
            for option in available_types:
                suggestions.append(option)
    
    return suggestions[:25]  # Discord limit


class NotificationToggleButton(discord.ui.Button):
    def __init__(self, notification_key, notification_name, emoji):
        super().__init__(
            label=notification_name,
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=notification_key
        )
        self.notification_key = notification_key
        self.notification_name = notification_name
        self.is_selected = False
    
    async def callback(self, interaction):
        # Toggle selection instantly
        self.is_selected = not self.is_selected
        
        # Update button appearance
        if self.is_selected:
            self.style = discord.ButtonStyle.success
            self.label = f"✓ {self.notification_name}"
        else:
            self.style = discord.ButtonStyle.secondary
            self.label = self.notification_name
        
        # Update view's selected types list
        view = self.view
        if self.is_selected:
            if self.notification_key not in view.selected_types:
                view.selected_types.append(self.notification_key)
        else:
            if self.notification_key in view.selected_types:
                view.selected_types.remove(self.notification_key)
        
        # Update confirm button state
        confirm_button = None
        for item in view.children:
            if isinstance(item, ConfirmButton):
                confirm_button = item
                break
        
        if confirm_button:
            if view.selected_types:
                confirm_button.disabled = False
                confirm_button.label = f"✅ Confirm {view.action.title()} ({len(view.selected_types)} selected)"
                confirm_button.style = discord.ButtonStyle.primary
            else:
                confirm_button.disabled = True
                confirm_button.label = f"Select types to {view.action}"
                confirm_button.style = discord.ButtonStyle.secondary
        
        # Quick update - no embed changes, just button states
        await interaction.response.edit_message(view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, action):
        super().__init__(
            label=f"Select types to {action}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            emoji="✅",
            row=1  # Put confirm button on second row
        )
        self.action = action
    
    async def callback(self, interaction):
        view = self.view
        selected_types = " ".join(view.selected_types)
        
        # Show processing message
        selected_names = [view.notification_types[key] for key in view.selected_types]
        processing_embed = discord.Embed(
            title=f"🔄 Processing {self.action.title()}...",
            description=f"Working on {len(view.selected_types)} notification types:",
            color=0xffaa00
        )
        processing_embed.add_field(
            name="📝 Processing",
            value="\n".join([f"• {name}" for name in selected_names]),
            inline=False
        )
        
        # Disable all buttons
        for item in view.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=processing_embed, view=view)
        
        # Find the cog to call the appropriate function
        cog = interaction.client.get_cog("RoleManager")
        if not cog:
            await interaction.followup.send("❌ Error: Role manager not found!", ephemeral=True)
            return
        
        # Create a mock context object for the function calls
        class MockContext:
            def __init__(self, interaction):
                self.guild = interaction.guild
                self.author = interaction.user
                self.respond = interaction.followup.send
        
        mock_ctx = MockContext(interaction)
        
        # Call the appropriate function
        if self.action == "subscribe":
            await cog._subscribe(mock_ctx, selected_types)
        elif self.action == "unsubscribe":
            await cog._unsubscribe(mock_ctx, selected_types)


class NotificationView(discord.ui.View):
    def __init__(self, notification_types, user_id, action):
        super().__init__(timeout=300)  # 5 minute timeout
        
        # Add toggle buttons for each notification type
        emoji_map = {
            "live_news": "📰",
            "news_report": "📊", 
            "economic_events": "📈"
        }
        
        for key, name in notification_types.items():
            emoji = emoji_map.get(key, "🔔")
            button = NotificationToggleButton(key, name, emoji)
            self.add_item(button)
        
        # Add confirm button on second row
        self.add_item(ConfirmButton(action))
        
        self.notification_types = notification_types
        self.user_id = user_id
        self.action = action
        self.selected_types = []
    
    async def interaction_check(self, interaction):
        """Only allow the command user to interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Only the command user can use this menu!", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        """Disable view when timeout occurs"""
        for item in self.children:
            item.disabled = True


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Use the module-level notification types
        self.notification_types = NOTIFICATION_TYPES
    
    @discord.slash_command(name="notifications", description="Manage your notification preferences")
    async def notifications_main(self, ctx,
                                 action: str = discord.Option(str, "Choose an action", choices=["subscribe", "unsubscribe", "list", "info"])):
        """Main notifications command with subactions"""
        if action == "info":
            await self._show_info(ctx)
        elif action == "list":
            await self._list_roles(ctx)
        elif action in ["subscribe", "unsubscribe"]:
            # Show selection menu for types
            await self._show_type_selector(ctx, action)
    
    async def _show_info(self, ctx):
        """Show notification help"""
        embed = discord.Embed(
            title="🔔 How Notification Roles work?",
            description="Use the `/notifications` command to add or remove your notification roles, for each notification role you have, the bot will mention you when notification of that type is posted.",
            color=0x0099ff
        )
        embed.add_field(
            name="Subscribe", 
            value="`/notifications action:subscribe`\n*Toggle buttons will appear to select notification types*", 
            inline=False
        )
        embed.add_field(
            name="Unsubscribe", 
            value="`/notifications action:unsubscribe`\n*Toggle buttons will appear to select notification types*", 
            inline=False
        )
        embed.add_field(name="List", value="`/notifications action:list`", inline=False)
        embed.add_field(
            name="Available Types", 
            value="**live_news**, **news_report**, **economic_events**", 
            inline=False
        )
        embed.add_field(
            name="Examples", 
            value="• `/notifications action:subscribe` → Click toggle buttons\n• `/notifications action:unsubscribe` → Click toggle buttons\n• `/notifications action:list` → See your current roles", 
            inline=False
        )
        embed.add_field(
            name="💡 Pro Tips",
            value="• **Toggle buttons**: Click buttons to select/deselect types (they turn green when selected)\n• **Visual feedback**: Selected buttons show ✓ and turn green\n• **Confirm when ready**: Click the confirm button when you're happy with your selection!",
            inline=False
        )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    async def _show_type_selector(self, ctx, action):
        """Show toggle buttons for choosing notification types"""
        embed = discord.Embed(
            title=f"🔔 {action.title()} Notifications",
            description=f"Click the buttons to select notification types you want to {action}:",
            color=0x0099ff
        )
        
        embed.add_field(
            name="💡 How to Use",
            value="Click the buttons above to select/deselect notification types, then click confirm!",
            inline=False
        )
        
        # Create button view
        view = NotificationView(self.notification_types, ctx.author.id, action)
        
        await ctx.respond(embed=embed, view=view, ephemeral=True)
    
    async def _subscribe(self, ctx, types: str):
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
            
            # Show summary first if multiple types were requested
            if len(requested_types) > 1:
                response_parts.append(f"🔔 **Processed {len(requested_types)} notification types:**")
            
            if added_roles:
                emoji = "✅" if len(added_roles) == 1 else "✅"
                response_parts.append(f"{emoji} **Added ({len(added_roles)}):** {', '.join(added_roles)}")
            if already_had:
                emoji = "ℹ️" if len(already_had) == 1 else "ℹ️"
                response_parts.append(f"{emoji} **Already had ({len(already_had)}):** {', '.join(already_had)}")
            if failed_roles:
                emoji = "❌" if len(failed_roles) == 1 else "❌"
                response_parts.append(f"{emoji} **Failed ({len(failed_roles)}):** {', '.join(failed_roles)}")
            
            if not response_parts or (not added_roles and not already_had and not failed_roles):
                response_parts.append("❌ No roles were processed.")
            
            await ctx.respond('\n'.join(response_parts), ephemeral=False)
            
        except Exception as e:
            print(f"Error in subscribe command: {e}")
            await ctx.respond("❌ An error occurred while processing your request.", ephemeral=False)
    
    async def _unsubscribe(self, ctx, types: str):
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
            
            # Show summary first if multiple types were requested
            if len(requested_types) > 1:
                response_parts.append(f"🔔 **Processed {len(requested_types)} notification types:**")
            
            if removed_roles:
                response_parts.append(f"✅ **Removed ({len(removed_roles)}):** {', '.join(removed_roles)}")
            if didnt_have:
                response_parts.append(f"ℹ️ **Didn't have ({len(didnt_have)}):** {', '.join(didnt_have)}")
            if missing_roles:
                response_parts.append(f"⚠️ **Role doesn't exist ({len(missing_roles)}):** {', '.join(missing_roles)}")
            if failed_roles:
                response_parts.append(f"❌ **Failed ({len(failed_roles)}):** {', '.join(failed_roles)}")
            
            if not response_parts or (not removed_roles and not didnt_have and not missing_roles and not failed_roles):
                response_parts.append("❌ No roles were processed.")
            
            await ctx.respond('\n'.join(response_parts), ephemeral=False)
            
        except Exception as e:
            print(f"Error in unsubscribe command: {e}")
            await ctx.respond("❌ An error occurred while processing your request.", ephemeral=False)
    
    async def _list_roles(self, ctx):
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