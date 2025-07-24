import discord
from config import Config

# Response emojis for different result types
RESPONSE_EMOJIS = {
    "success": "✅",
    "info": "ℹ️",
    "warning": "⚠️",
    "error": "❌"
}

class NotificationToggleButton(discord.ui.Button):
    def __init__(self, role: Config.NOTIFICATION_ROLES):
        super().__init__(
            label=role.name,
            style=discord.ButtonStyle.secondary,
            emoji=role.emoji,
            custom_id=role.key
        )
        self.role = role
        self.is_selected = False
    
    async def callback(self, interaction):
        # Toggle selection instantly
        self.is_selected = not self.is_selected
        
        # Update button appearance
        if self.is_selected:
            self.style = discord.ButtonStyle.success
            self.label = f"✓ {self.role.name}"
        else:
            self.style = discord.ButtonStyle.secondary
            self.label = self.role.name
        
        # Update view's selected roles list
        view = self.view
        if self.is_selected:
            if self.role not in view.selected_roles:
                view.selected_roles.append(self.role)
        elif self.role in view.selected_roles:
            view.selected_roles.remove(self.role)
        
        # Update confirm button state
        if view.confirm_button:
            view.confirm_button.disabled = False
            if view.selected_roles:
                view.confirm_button.label = f"✅ Confirm Changes ({len(view.selected_roles)} selected)"
                view.confirm_button.style = discord.ButtonStyle.primary
            else:
                view.confirm_button.label = "✅ Confirm Changes (no subscriptions)"
                view.confirm_button.style = discord.ButtonStyle.secondary
        
        # Quick update - no embed changes, just button states
        await interaction.response.edit_message(view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, action): # action equals subscribe or unsubscribe
        super().__init__(
            label="✅ Confirm Changes",
            style=discord.ButtonStyle.secondary,
            disabled=False,
            emoji="✅",
            row=1  # Put confirm button on second row
        )
        self.action = action
    
    async def callback(self, interaction):
        view = self.view
        selected_role_name_list = [role.name for role in view.selected_roles]
        
        # Show processing message
        selected_role_full_names = [role.full_name for role in view.selected_roles]
        processing_embed = discord.Embed(
            title="🔄 Processing Subscription Changes...",
            description=f"Updating {len(view.selected_roles)} notification types:",
            color=0xffaa00
        )
        processing_embed.add_field(
            name="📝 Processing",
            value="\n".join([f"• {name}" for name in selected_role_full_names]),
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
        
        # Call the edit function to handle both additions and removals
        await cog._process_subscription_changes(interaction, selected_role_name_list)


class NotificationView(discord.ui.View):
    def __init__(self, user_id, action, current_roles=None):
        super().__init__(timeout=300)  # 5 minute timeout
        
        # Add toggle buttons for each notification role
        for role in Config.NOTIFICATION_ROLES.ALL_ROLES:
            button = NotificationToggleButton(role)
            # Pre-select if user already has this role
            if current_roles and role in current_roles:
                button.is_selected = True
                button.style = discord.ButtonStyle.success
                button.label = f"✓ {role.name}"
            self.add_item(button)
        
        # Add confirm button on second row
        self.confirm_button = ConfirmButton(action)
        self.add_item(self.confirm_button)
        
        self.user_id = user_id
        self.action = action
        self.selected_roles = current_roles.copy() if current_roles else []
        
        # Update confirm button state based on pre-selected roles
        self.confirm_button.disabled = False
        if self.selected_roles:
            self.confirm_button.label = f"✅ Confirm Changes ({len(self.selected_roles)} selected)"
            self.confirm_button.style = discord.ButtonStyle.primary
        else:
            self.confirm_button.label = "✅ Confirm Changes (no subscriptions)"
            self.confirm_button.style = discord.ButtonStyle.secondary
    
    async def interaction_check(self, interaction):
        """Only allow the command user to interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Only the user who invoked the command can use this menu!", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        """Disable view when timeout occurs"""
        for item in self.children:
            item.disabled = True 