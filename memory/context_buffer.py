import dataclasses
import time
from typing import List, Dict, Any, Optional, Set
import re

@dataclasses.dataclass
class ContextItem:
    """Represents a single fragment of memory in the Aetherial Memory system."""
    content: str
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)
    timestamp: float = dataclasses.field(default_factory=time.time)
    importance: float = 1.0  # 1.0 is default, higher is more important
    tags: Set[str] = dataclasses.field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "tags": list(self.tags)
        }

class ActiveAttentionFilter:
    """Filters context items based on relevance to the current task and session state."""

    def __init__(self, recency_weight: float = 0.4, keyword_weight: float = 0.4, importance_weight: float = 0.2):
        self.recency_weight = recency_weight
        self.keyword_weight = keyword_weight
        self.importance_weight = importance_weight

    def calculate_relevance(self, item: ContextItem, query_keywords: Set[str], current_time: float) -> float:
        # 1. Recency Score (Normalized exponential decay)
        age = current_time - item.timestamp
        # Decay half-life of 1 hour (3600 seconds) for demonstration
        recency_score = 1.0 / (1.0 + (age / 3600.0))

        # 2. Keyword Match Score
        content_lower = item.content.lower()
        match_count = sum(1 for kw in query_keywords if kw.lower() in content_lower)
        keyword_score = min(1.0, match_count / max(1, len(query_keywords)))

        # 3. Importance Score (Normalized)
        importance_score = min(1.0, item.importance / 10.0)

        # Final Weighted Score
        return (
            recency_score * self.recency_weight +
            keyword_score * self.keyword_weight +
            importance_score * self.importance_weight
        )

    def filter(self, items: List[ContextItem], query: str, top_k: int = 5) -> List[ContextItem]:
        """Filters and returns the top K most relevant context items."""
        if not items:
            return []

        # Extract keywords from query (simple regex)
        query_keywords = set(re.findall(r'\w+', query.lower()))
        current_time = time.time()

        # Score items
        scored_items = [
            (item, self.calculate_relevance(item, query_keywords, current_time))
            for item in items
        ]

        # Sort by score descending
        scored_items.sort(key=lambda x: x[1], reverse=True)

        return [item for item, score in scored_items[:top_k]]

class ContextBuffer:
    """Global Context Buffer with selective context injection."""

    def __init__(self, attention_filter: Optional[ActiveAttentionFilter] = None):
        self.global_history: List[ContextItem] = []
        self.attention_filter = attention_filter or ActiveAttentionFilter()

    def add_memory(self, content: str, importance: float = 1.0, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Adds a new item to the global history."""
        item = ContextItem(
            content=content,
            importance=importance,
            tags=set(tags) if tags else set(),
            metadata=metadata or {},
            timestamp=time.time()
        )
        self.global_history.append(item)

    def get_active_context(self, query: str, max_items: int = 10) -> str:
        """Retrieves and formats the most relevant context for a given query."""
        relevant_items = self.attention_filter.filter(self.global_history, query, top_k=max_items)
        
        # Sort relevant items chronologically for injection
        relevant_items.sort(key=lambda x: x.timestamp)

        context_blocks = []
        for item in relevant_items:
            # Simple block formatting
            context_blocks.append(f"--- Memory ({time.ctime(item.timestamp)}) ---\n{item.content}")

        return "\n\n".join(context_blocks)

    def clear(self):
        """Clears the global history."""
        self.global_history = []

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the context buffer."""
        return {
            "total_items": len(self.global_history),
            "total_characters": sum(len(item.content) for item in self.global_history)
        }
