"""
Interaction Utilities for Discord Slash Commands
"""

import discord
import asyncio
from utils.logger import logger


async def respond_with_progress(ctx, initial_message: str, ephemeral: bool = False):
    """
    Respond to an interaction with an initial message and return the response object
    
    Args:
        ctx: Discord interaction context
        initial_message: Initial message to send
        ephemeral: Whether the message should be ephemeral
    
    Returns:
        The response message object
    """
    try:
        # Use deferred response to prevent timeout
        await ctx.defer(ephemeral=ephemeral)
        response = await ctx.followup.send(initial_message, ephemeral=ephemeral)
        return response
    except Exception as e:
        logger.error(f"❌ Error responding to interaction: {e}")
        return None


def split_text_at_sentences(text: str, max_length: int = 1024) -> list:
    """
    Split text at sentence boundaries to fit Discord embed field limits
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk (default 1024 for Discord embed fields)
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= max_length:
        return [text]
    
    chunks = []
    remaining_text = text
    
    while len(remaining_text) > max_length:
        # Find the last sentence ending (dot, exclamation, question mark) before max_length
        last_sentence_end = -1
        
        # Look for sentence endings within the limit
        for i in range(max_length - 1, -1, -1):
            if remaining_text[i] in '.!?':
                # Check if it's followed by whitespace or end of string
                if i + 1 >= len(remaining_text) or remaining_text[i + 1].isspace():
                    last_sentence_end = i + 1
                    break
        
        # If no sentence ending found, look for newlines
        if last_sentence_end == -1:
            for i in range(max_length - 1, -1, -1):
                if remaining_text[i] == '\n':
                    last_sentence_end = i + 1
                    break
        
        # If still no break point found, split at max_length
        if last_sentence_end == -1:
            last_sentence_end = max_length
        
        # Add the chunk
        chunk = remaining_text[:last_sentence_end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Update remaining text
        remaining_text = remaining_text[last_sentence_end:].strip()
    
    # Add any remaining text
    if remaining_text:
        chunks.append(remaining_text)
    
    return [chunk for chunk in chunks if chunk.strip()]


def truncate_text(text: str, max_length: int = 1024) -> str:
    """
    Truncate text to fit Discord embed field limits
    
    Args:
        text: Text to truncate
        max_length: Maximum length (default 1024 for Discord embed fields)
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Truncate and add ellipsis
    return text[:max_length-3] + "..."

async def update_interaction_response(ctx, new_content: str, embed: discord.Embed = None):
    """
    Update the interaction response with new content
    
    Args:
        ctx: Discord interaction context
        new_content: New content to display
        embed: Optional embed to include
    """
    try:
        # Use followup to send updated content
        await ctx.followup.send(new_content, embed=embed, ephemeral=False)
    except Exception as e:
        logger.error(f"❌ Error updating interaction response: {e}")
        # Fallback to new response
        await ctx.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


async def handle_long_operation(ctx, operation_name: str, operation_func, *args, **kwargs):
    """
    Handle a long operation with progress updates
    
    Args:
        ctx: Discord interaction context
        operation_name: Name of the operation for progress messages
        operation_func: Function to execute
        *args, **kwargs: Arguments for the operation function
    
    Returns:
        Result of the operation function
    """
    try:
        # Send initial progress message
        await ctx.respond(f"🔄 {operation_name}...", ephemeral=False)
        
        # Execute the operation
        result = await operation_func(*args, **kwargs) if asyncio.iscoroutinefunction(operation_func) else operation_func(*args, **kwargs)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in {operation_name}: {e}")
        await update_interaction_response(ctx, f"❌ Error during {operation_name}: {str(e)}")
        return None 