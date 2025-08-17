import discord
from discord.ext import commands
from scrapers.yf.yf_scraper import YfScraper
from discord_utils.interaction_utils import split_text_at_sentences
from utils.logger import logger
import yfinance as yf
from db.init_db import init_db
from db.engine import get_db_sync
from db.crud import CRUDBase
from config import Config
from db.models import SymbolsList
from ai_tools.process_company_description import get_hebrew_description

class StockInfoCommandsV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_ticker_exists(self, ticker_name):
        """Check if a ticker exists using yfinance search"""
        try:
            ticker = yf.Search(ticker_name, max_results=3, enable_fuzzy_query=True)
            return any(quote["symbol"] == ticker_name for quote in ticker.all["quotes"])
        except Exception as e:
            logger.error(f"Error checking ticker existence: {e}")
            return False
    
    def create_embed(self, symbol, parsed_data, hebrew_desc=None):
        """Create embed with stock information"""
        embed = discord.Embed(title=f"📊 {symbol.upper()} Information", color=0x0099ff)
        
        # Add basic fields
        fields = [
            ("📈 Symbol", parsed_data.get("symbol")),
            ("🏷️ Type", parsed_data.get("type")),
            ("🏢 Company Name", parsed_data.get("company_name")),
            ("🌐 Website", parsed_data.get("website")),
            ("📊 IR Website", parsed_data.get("ir_website")),
            ("🏭 Industry", parsed_data.get("industry")),
            ("📋 Sector", parsed_data.get("sector")),
            ("💰 Last Price", parsed_data.get("last_price"))
        ]
        
        for name, value in fields:
            if value and value not in ["N/A", "None"]:
                embed.add_field(name=name, value=str(value)[:1024], inline=True)
        
        # Add Hebrew description if available
        if hebrew_desc:
            chunks = split_text_at_sentences(hebrew_desc, 1024)
            if chunks:
                embed.add_field(name="📝 תיאור החברה", value=chunks[0], inline=False)
        
        return embed, chunks[1:] if hebrew_desc and len(chunks) > 1 else []
    
    @discord.slash_command(name="stock_info", description="Get stock information using Yahoo Finance API")
    async def stock_info(self, ctx, symbol: str = discord.Option(str, "Stock symbol to check", required=True)):
        """Get stock information using Yahoo Finance API"""
        db = None
        try:
            await ctx.defer(ephemeral=False)
            
            # Initialize database
            init_db()
            symbols_crud = CRUDBase(SymbolsList)
            db = get_db_sync()
            
            # Check database first
            symbol_data = symbols_crud.get_by_field(db, "symbol", symbol.upper()) # this will return None if the symbol is not in the database
            hebrew_desc = symbol_data.hebrew_description if symbol_data else None
            
            # Always create a progress message to edit later
            progress_msg = await ctx.followup.send("🔄 Getting stock information...", ephemeral=False)
            
            # Check yfinance only if not in database
            if not hebrew_desc:
                if not self.is_ticker_exists(symbol.upper()):
                    await progress_msg.edit(content=f"❌ Symbol **{symbol.upper()}** not found")
                    return
            
            # Get Yahoo Finance data
            yfr = YfScraper(proxy=Config.PROXY.APP_PROXY)
            quote_data = await yfr.get_quote_summary(symbol.upper())
            
            if not quote_data:
                await progress_msg.edit(content=f"❌ Error getting stock information for symbol **{symbol.upper()}**")
                return
            
            parsed_data = yfr.parse_quote_summary(quote_data)
            if not parsed_data or not parsed_data.get("symbol"):
                await progress_msg.edit(content=f"❌ Unable to parse data for symbol **{symbol.upper()}**")
                return
            
            # Process Hebrew description if needed
            if not hebrew_desc:
                business_summary = parsed_data.get("business_summary")
                if business_summary:
                    await progress_msg.edit(content="🔄 Processing Hebrew description...")
                    
                    try:
                        hebrew_desc = get_hebrew_description(symbol.upper(), business_summary)
                        
                        # Save to database
                        if symbol_data:
                            symbols_crud.update_by_field(db, "symbol", symbol.upper(), {"hebrew_description": hebrew_desc})
                        else:
                            symbols_crud.create(db, {"symbol": symbol.upper(), "hebrew_description": hebrew_desc})
                            
                    except Exception as e:
                        logger.error(f"Error processing Hebrew description: {e}")
                        hebrew_desc = None
            
            # Replace progress message with final embed
            main_embed, remaining_chunks = self.create_embed(symbol, parsed_data, hebrew_desc)
            await progress_msg.edit(content=None, embed=main_embed)
            
            # Send remaining chunks
            for i, chunk in enumerate(remaining_chunks, 2):
                try:
                    desc_embed = discord.Embed(
                        color=0x0099ff
                    )
                    desc_embed.add_field(name="📝 תיאור החברה", value=chunk, inline=False)
                    desc_embed.set_footer(text=f"תיאור החברה (חלק {i})")
                    await ctx.channel.send(embed=desc_embed)
                except Exception as e:
                    logger.error(f"Error sending additional embed {i}: {e}")
                    await ctx.channel.send(f"📊 {symbol.upper()} תיאור החברה (חלק {i}):\n{chunk}")
            
        except Exception as e:
            logger.error(f"Error getting stock info: {e}")
            try:
                await ctx.followup.send(f"❌ Error getting stock info: {str(e)}", ephemeral=False)
            except:
                await ctx.respond(f"❌ Error getting stock info: {str(e)}", ephemeral=True)
        finally:
            if db:
                db.close()

def setup(bot):
    bot.add_cog(StockInfoCommandsV2(bot))
