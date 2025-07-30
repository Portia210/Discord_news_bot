import discord
from discord.ext import commands
from db.init_db import init_db
from db.engine import get_db_sync
from db.crud import CRUDBase
from db.models import SymbolsList
from scrapers.company_info import get_company_info
from ai_tools.process_company_description import get_hebrew_description
from discord_utils.interaction_utils import respond_with_progress, update_interaction_response, truncate_text, split_text_at_sentences
from utils.logger import logger

class StockInfoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="stock_info", description="Check if a stock symbol exists in the database")
    async def stock_info(self, ctx, 
                        symbol: str = discord.Option(str, "Stock symbol to check", required=True)):
        """Check if a stock symbol exists in the database"""
        try:
            # Defer immediately to prevent timeout
            await ctx.defer(ephemeral=False)
            
            # Initialize database and create CRUD instance
            init_db()
            symbols_crud = CRUDBase(SymbolsList)
            db = get_db_sync()
            
            # Check if symbol exists
            symbol_data = symbols_crud.get_by_field(db, "symbol", symbol.upper())
            
            if not symbol_data:
                await ctx.followup.send(f"❌ Symbol **{symbol.upper()}** not found in database", ephemeral=False)
                db.close()
                return
            
            # Check if it's a stock
            if symbol_data.type and symbol_data.type.lower() != "stock":
                await ctx.followup.send(f"**{symbol.upper()}** is not a company, it's a **{symbol_data.type}**", ephemeral=False)
                db.close()
                return
            
            # Fetch company info only if raw_description is empty
            company_info = None
            progress_message = None
            
            if not symbol_data.raw_description:
                progress_message = await ctx.followup.send("🔄 Getting company information...", ephemeral=False)
                company_info = get_company_info(symbol.upper())
                if not company_info:
                    await progress_message.edit(content="Sorry, there is an issue fetching company information.")
                    db.close()
                    return
                
                # Update database with company info
                update_data = {
                    "raw_description": company_info.get("description", ""),
                    "market_cap": company_info.get("market_cap"),
                    "market_cap_profile": company_info.get("market_cap_profile"),
                    "website_url": company_info.get("website_url")
                }
                symbols_crud.update_by_field(db, "symbol", symbol.upper(), update_data)
            else:
                # Use existing data
                company_info = {
                    "description": symbol_data.raw_description,
                    "market_cap": symbol_data.market_cap,
                    "market_cap_profile": symbol_data.market_cap_profile,
                    "website_url": symbol_data.website_url
                }
            
            # Get Hebrew description only if it's empty
            if not symbol_data.hebrew_description:
                if progress_message:
                    await progress_message.edit(content="🔄 Getting Hebrew description...")
                else:
                    progress_message = await ctx.followup.send("🔄 Getting Hebrew description...", ephemeral=False)
                
                try:
                    hebrew_desc = get_hebrew_description(symbol.upper(), company_info.get("description", ""))
                    symbols_crud.update_by_field(db, "symbol", symbol.upper(), {"hebrew_description": hebrew_desc})
                except Exception as e:
                    await progress_message.edit(content="Sorry, there is an issue processing the description.")
                    db.close()
                    return
            else:
                hebrew_desc = symbol_data.hebrew_description
            
            # Delete progress message if it exists
            if progress_message:
                await progress_message.delete()
            
            # Split description into multiple embeds if needed
            description_chunks = split_text_at_sentences(hebrew_desc, 1024)
            
            # Send main embed with basic info
            main_embed = discord.Embed(
                title=f"📊 {symbol.upper()} Information",
                color=0x0099ff
            )
            main_embed.add_field(name="Symbol", value=symbol.upper(), inline=True)
            main_embed.add_field(name="Company Name", value=symbol_data.name, inline=True)
            main_embed.add_field(name="Website", value=company_info.get("website_url", "N/A"), inline=True)
            
            
            # Add first part of description to main embed (ensure it's not too long)
            if description_chunks:
                main_embed.add_field(name="Description", value= description_chunks[0], inline=False)
            
            await ctx.followup.send(embed=main_embed, ephemeral=False)
            
            # Send additional embeds for remaining description chunks
            for i, chunk in enumerate(description_chunks[1:], 2):
                desc_embed = discord.Embed(
                    title=f"📊 {symbol.upper()} Description (Part {i})",
                    color=0x0099ff
                )
                desc_embed.add_field(name="Description", value=chunk, inline=False)
                await ctx.channel.send(embed=desc_embed)
            
            db.close()
            
        except Exception as e:
            await ctx.respond(f"❌ Error getting stock info", ephemeral=True)
            logger.error(f"Error getting stock info: {e}")
            db.close()

def setup(bot):
    bot.add_cog(StockInfoCommands(bot)) 