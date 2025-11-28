"""Web search configuration value object."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class WebSearchConfig:
    """
    Immutable configuration for web search using Firecrawl.
    
    Value object that encapsulates web search parameters.
    """
    
    enabled: bool = False
    query: Optional[str] = None
    max_results: int = 5
    timeout: int = 30000  # milliseconds
    formats: tuple = ("markdown",)  # Use tuple for immutability
    include_in_context: bool = True
    
    def __post_init__(self):
        """Validate web search configuration."""
        if not 1 <= self.max_results <= 10:
            raise ValueError("max_results must be between 1 and 10")
        
        if not 5000 <= self.timeout <= 60000:
            raise ValueError("timeout must be between 5000 and 60000 ms")
    
    def is_enabled(self) -> bool:
        """Check if web search is enabled."""
        return self.enabled
    
    def has_custom_query(self) -> bool:
        """Check if using custom query (not using user's message)."""
        return self.query is not None and len(self.query.strip()) > 0
    
    @classmethod
    def disabled(cls) -> "WebSearchConfig":
        """Create disabled web search config."""
        return cls(enabled=False)
    
    @classmethod
    def quick(cls, query: Optional[str] = None) -> "WebSearchConfig":
        """Create quick search config (fewer results, shorter timeout)."""
        return cls(
            enabled=True,
            query=query,
            max_results=3,
            timeout=15000,
            formats=("markdown",),
            include_in_context=True,
        )
    
    @classmethod
    def comprehensive(cls, query: Optional[str] = None) -> "WebSearchConfig":
        """Create comprehensive search config (more results, longer timeout)."""
        return cls(
            enabled=True,
            query=query,
            max_results=10,
            timeout=45000,
            formats=("markdown", "html"),
            include_in_context=True,
        )
