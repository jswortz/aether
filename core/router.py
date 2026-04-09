import json
import os
from typing import List, Dict, Any, Optional

class AgentRouter:
    """
    High-bandwidth dispatcher that maps semantic intents to worker capabilities.
    """
    def __init__(self, registry_path: str = "/usr/local/google/home/jwortz/aether/core/router_registry.json"):
        self.registry_path = registry_path
        self._ensure_registry()

    def _ensure_registry(self):
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, 'w') as f:
                json.dump({"routing_table": []}, f, indent=2)

    def register_tool(self, intent: str, tool_name: str, path: str, score: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        """Registers a new tool capability with a Worker Capability (WC) score."""
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        
        entry_data = {
            "intent": intent,
            "tool_name": tool_name,
            "path": path,
            "wc_score": score,
            "metadata": metadata or {}
        }

        # Check if already exists
        for i, entry in enumerate(data["routing_table"]):
            if entry["tool_name"] == tool_name:
                data["routing_table"][i] = entry_data
                break
        else:
            data["routing_table"].append(entry_data)

        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def route(self, intent_query: str) -> List[Dict[str, Any]]:
        """
        Maps an intent query to the best available tools based on WC scores and semantic intent.
        Returns a ranked list of capabilities.
        """
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        
        scored_results = []
        query_words = set(intent_query.lower().split())
        
        for entry in data["routing_table"]:
            intent_words = set(entry["intent"].lower().split())
            intersection = query_words.intersection(intent_words)
            
            # Semantic match score based on keyword overlap
            semantic_score = len(intersection) / max(1, len(intent_words))
            
            # Final score combines semantic relevance and Worker Capability (WC)
            final_score = semantic_score * entry.get("wc_score", 1.0)
            
            if final_score > 0:
                scored_results.append({
                    **entry,
                    "match_score": final_score
                })
        
        # Sort by match_score descending
        scored_results.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_results

    def list_capabilities(self) -> List[Dict[str, Any]]:
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        return data["routing_table"]
