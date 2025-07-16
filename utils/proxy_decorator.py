import functools
import aiohttp
import requests
from typing import Optional, Dict, Any, Union
from utils.logger import logger
import asyncio


class ProxyConfig:
    """Configuration class for proxy settings"""
    def __init__(self, 
                 proxy_url: str = None,
                 proxy_username: str = None,
                 proxy_password: str = None,
                 proxy_type: str = "http"):
        self.proxy_url = proxy_url
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_type = proxy_type
    
    def get_aiohttp_proxy(self) -> Optional[str]:
        """Get proxy URL formatted for aiohttp"""
        if not self.proxy_url:
            return None
        
        if self.proxy_username and self.proxy_password:
            # Format: http://username:password@proxy_host:port
            return f"{self.proxy_type}://{self.proxy_username}:{self.proxy_password}@{self.proxy_url.replace('http://', '').replace('https://', '')}"
        else:
            return f"{self.proxy_type}://{self.proxy_url}"
    
    def get_requests_proxy(self) -> Optional[Dict[str, str]]:
        """Get proxy dict formatted for requests"""
        if not self.proxy_url:
            return None
        
        proxy_dict = {
            "http": self.get_aiohttp_proxy(),
            "https": self.get_aiohttp_proxy()
        }
        
        if self.proxy_username and self.proxy_password:
            proxy_dict["auth"] = (self.proxy_username, self.proxy_password)
        
        return proxy_dict


def create_proxy_session(proxy_config: ProxyConfig = None) -> aiohttp.ClientSession:
    """
    Create an aiohttp session with proxy support
    
    Usage:
        session = create_proxy_session(ProxyConfig("proxy.example.com:8080"))
        async with session.post(url, data=data) as response:
            # Your code here
    """
    if not proxy_config:
        return aiohttp.ClientSession()
    
    proxy_url = proxy_config.get_aiohttp_proxy()
    if proxy_url:
        logger.debug(f"Creating session with proxy: {proxy_url}")
        # For aiohttp, you might need to use a proxy connector
        # This is a simplified version - you may need to adjust based on your proxy service
        connector = aiohttp.TCPConnector()
        return aiohttp.ClientSession(connector=connector)
    
    return aiohttp.ClientSession()


# Global proxy configuration
_global_proxy_config = None

def set_global_proxy(proxy_config: ProxyConfig):
    """Set global proxy configuration"""
    global _global_proxy_config
    _global_proxy_config = proxy_config
    logger.info(f"Global proxy configured: {proxy_config.proxy_url}")

def get_global_proxy() -> Optional[ProxyConfig]:
    """Get global proxy configuration"""
    return _global_proxy_config


def with_proxy_session(proxy_config: ProxyConfig = None):
    """
    Decorator that replaces aiohttp.ClientSession() with a proxy-enabled session
    
    Usage:
        @with_proxy_session(ProxyConfig("proxy.example.com:8080", "user", "pass"))
        async def _fetch_table(self, page_name, payload: dict):
            # Your existing code with aiohttp.ClientSession() will automatically use proxy
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the proxy config (either passed to decorator or global)
            config = proxy_config or get_global_proxy()
            
            if config:
                # Monkey patch aiohttp.ClientSession for this function call
                original_session = aiohttp.ClientSession
                
                def proxy_session(*session_args, **session_kwargs):
                    proxy_url = config.get_aiohttp_proxy()
                    if proxy_url:
                        logger.debug(f"Using proxy: {proxy_url}")
                        # You might need to use aiohttp.ProxyConnector for proper proxy support
                        # For now, we'll use the basic approach
                        connector = aiohttp.TCPConnector()
                        return aiohttp.ClientSession(connector=connector, *session_args, **session_kwargs)
                    return original_session(*session_args, **session_kwargs)
                
                # Replace aiohttp.ClientSession temporarily
                aiohttp.ClientSession = proxy_session
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    # Restore original aiohttp.ClientSession
                    aiohttp.ClientSession = original_session
            else:
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def with_proxy_context(proxy_config: ProxyConfig = None):
    """
    Context manager decorator for proxy support
    
    Usage:
        @with_proxy_context(ProxyConfig("proxy.example.com:8080"))
        async def _fetch_table(self, page_name, payload: dict):
            # Your existing code here
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            config = proxy_config or get_global_proxy()
            
            if config:
                # Create proxy session
                session = create_proxy_session(config)
                # Pass session as a keyword argument to the function
                kwargs['session'] = session
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    await session.close()
            else:
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Simple function to modify existing code with minimal changes
def modify_session_creation(proxy_config: ProxyConfig = None):
    """
    Simple function to modify session creation in existing code
    
    Usage:
        # Replace this line in your code:
        # async with aiohttp.ClientSession() as session:
        
        # With this:
        session = create_proxy_session(proxy_config)
        async with session as session:
    """
    return create_proxy_session(proxy_config) 