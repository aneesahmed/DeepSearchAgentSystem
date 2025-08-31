# File: deep_research/search_providers.py
"""
Search Providers Module
======================
Contains all search provider implementations for the deep research system.
"""

import os
import logging
from typing import List, Dict

import aiohttp

from .core import SearchProvider

logger = logging.getLogger(__name__)


class TavilySearchProvider(SearchProvider):
    """Tavily search provider (recommended)."""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment")
        self.base_url = "https://api.tavily.com"
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using Tavily API."""
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "max_results": num_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/search", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        logger.error(f"Tavily search failed: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []


class DuckDuckGoSearchProvider(SearchProvider):
    """DuckDuckGo search provider (fallback)."""
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using DuckDuckGo (simplified implementation)."""
        try:
            # This is a simplified implementation
            # In practice, you'd use duckduckgo-search library or similar
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=num_results):
                    results.append({
                        'url': result.get('href', ''),
                        'title': result.get('title', ''),
                        'content': result.get('body', '')
                    })
            return results
        except ImportError:
            logger.warning("duckduckgo-search not available. Install with: pip install duckduckgo-search")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []


class SearchAPIProvider(SearchProvider):
    """Generic search API provider."""
    
    def __init__(self):
        self.api_key = os.getenv("SEARCH_API_KEY")
        if not self.api_key:
            raise ValueError("SEARCH_API_KEY not found in environment")
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using generic search API."""
        # Implement your preferred search API here
        # This is a placeholder implementation
        logger.warning("SearchAPIProvider not fully implemented")
        return []


def get_default_search_provider() -> SearchProvider:
    """Get default search provider based on available API keys."""
    if os.getenv("TAVILY_API_KEY"):
        logger.info("Using Tavily search provider")
        return TavilySearchProvider()
    elif os.getenv("SEARCH_API_KEY"):
        logger.info("Using generic search API provider")
        return SearchAPIProvider()
    else:
        logger.info("Using DuckDuckGo search provider (fallback)")
        return DuckDuckGoSearchProvider()