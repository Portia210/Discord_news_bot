from utils.logger import logger
from discord_utils.message_handler import get_message_handler
from ai_tools.chat_gpt import AIInterpreter
from utils.read_write import read_text_file, write_json_file
from config import Config
import discord
from datetime import datetime



async def process_news_to_list(discord_bot: discord.Client, hours_back: int = 24, news_channel_id: int = Config.CHANNEL_IDS.TWEETER_NEWS, list_of_users: list = [Config.USER_IDS.IFITT_BOT]):
    """
    Complete pipeline to process news messages and send PDF report to Discord.
    Handles: message export → AI processing → PDF generation → Discord sending
    """
    def _analyze_news_to_list(messages: str) -> list[dict]:
        """
        Analyze news messages to a list of dictionaries.
        The dictionaries will be in the following format:
        {
            "date": str,
            "time": str,
            "message": str,
            "link": str,
        }
        """
        try:
            ai_interpreter = AIInterpreter()
            news_summary_prompt = read_text_file("ai_tools/prompts/news_summary_hebrew.txt") + "\n".join(messages)
            response = ai_interpreter.get_json_response(news_summary_prompt)
            # response = [
            #     {
            #         "time": "morning",
            #         "message": "הבוקר פורסמו נתוני ה-CPI בארצות הברית, והם היו גבוהים מהצפוי. עלייה זו מצביעה על לחצים מתמשכים באינפלציה, מה שמוביל לחששות לגבי יציבות המחירים.",
            #         "link": "https://www.bloomberg.com/news/articles/cpi-data"
            #     },
            #     {
            #         "time": "noon",
            #         "message": "הנתונים האחרונים עוררו ציפיות כי ה-Fed יעלה את הריבית ב-0.25% בשבוע הבא. צעד זה מבוצע כדי למתן את הלחצים האינפלציוניים ולהחזיר יציבות לשווקים.",
            #         "link": "https://www.reuters.com/markets/fed-rate-hike"
            #     },
            #     {
            #         "time": "afternoon",
            #         "message": "שיעור האבטלה בארצות הברית צפוי להישאר על 3.7%. שיעור זה משקף שוק עבודה יציב וחזק, המצביע על כך שהכלכלה האמריקאית עדיין במצב טוב."
            #     }
            # ]
            return response
        except Exception as e:
            logger.error(f"Error analyzing news to list: {e}")
            return []
        
    try:
        message_handler = get_message_handler(discord_bot)
        messages_list, _ = await message_handler.read_channel_messages(news_channel_id, hours_back, list_of_users)
        
        if not messages_list:
            logger.warning("No messages found to process")
            return []
        
        # Convert messages to text format for AI processing
        messages_text = []
        for msg in messages_list:
            messages_text.append(f"[{msg['timestamp']}] {msg['author']}: {msg['content']}")
        
        news_list = _analyze_news_to_list(messages_text)
        return news_list
    except Exception as e:
        logger.error(f"❌ Error processing messages with AI: {e}")
        return []
    

       





