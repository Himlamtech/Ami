"""Suggestion DTOs."""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SuggestionItem(BaseModel):
    id: str
    text: str
    type: str
    category: Optional[str] = None
    relevance_score: float = 0.0
    source: str = "system"


class SuggestionsResponse(BaseModel):
    suggestions: List[SuggestionItem]
    generated_at: datetime


__all__ = ["SuggestionItem", "SuggestionsResponse"]
