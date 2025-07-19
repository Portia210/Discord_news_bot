from utils.logger import logger

def view_permissions(guild):
    permissions = guild.me.guild_permissions
    logger.info(f"Permissions for {guild.name}:")
    logger.info(f"Administrator: {permissions.administrator}")
    logger.info(f"Manage Channels: {permissions.manage_channels}")
    logger.info(f"Manage Roles: {permissions.manage_roles}")
    logger.info(f"Send Messages: {permissions.send_messages}")
    logger.info(f"Use Application Commands: {permissions.use_application_commands}")