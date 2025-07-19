import discord
from utils.logger import logger



async def send_pdf(bot: discord.Client, channel_id: int, input_file_path: str, message: str, filename_on_discord: str):
    channel = bot.get_channel(channel_id)
    
    if channel:
        try:
            # Send the PDF file
            with open(input_file_path, "rb") as pdf_file:
                await channel.send(
                    content=message,
                    file=discord.File(pdf_file, filename=filename_on_discord)
                )
            logger.info("✅ PDF report sent to Discord channel successfully")
        except Exception as e:
            logger.error(f"❌ Failed to send PDF to Discord channel: {e}")
            # Send a fallback message if PDF sending fails
            await channel.send("📰 **Daily News Report**\nNews processing completed, but there was an issue sending the PDF file.")
    else:
        logger.error(f"❌ Could not find channel with ID: {channel_id}")
        
    
    