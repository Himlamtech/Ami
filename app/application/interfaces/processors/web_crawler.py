"""Web crawler interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class IWebCrawler(ABC):
    """
    Interface for web crawling.
    
    Crawls websites and extracts content.
    """
    
    @abstractmethod
    async def scrape_url(
        self,
        url: str,
        formats: List[str] = None,
        timeout: int = 30000,
    ) -> Dict[str, Any]:
        """
        Scrape single URL.
        
        Args:
            url: URL to scrape
            formats: Desired output formats (e.g., ["markdown", "html"])
            timeout: Timeout in milliseconds
            
        Returns:
            Dict with:
                - content: Extracted content
                - metadata: Page metadata
                - success: Whether scrape succeeded
        """
        pass
    
    @abstractmethod
    async def crawl_website(
        self,
        url: str,
        max_depth: int = 2,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Crawl website (multiple pages).
        
        Args:
            url: Starting URL
            max_depth: Maximum crawl depth
            limit: Maximum number of pages
            
        Returns:
            List of scraped pages
        """
        pass
