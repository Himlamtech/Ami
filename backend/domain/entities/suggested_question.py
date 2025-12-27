"""Suggested question domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class SuggestedQuestion:
    """Question bank item used for personalized suggestions."""

    id: str
    text: str
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
