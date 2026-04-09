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

    def register_tool(self, intent: str, tool_name: str, path: str, score: float = 1.0, preferred_model: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Registers a new tool capability with a Worker Capability (WC) score and preferred model."""
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        
        entry_data = {
            "intent": intent,
            "tool_name": tool_name,
            "path": path,
            "wc_score": score,
            "preferred_model": preferred_model or "gemini-2.0-flash", # Default for general tasks
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
        Maps an intent query to the best available tools and models.
        Returns a ranked list of capabilities with model recommendations.
        """
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        
        scored_results = []
        query_words = set(intent_query.lower().split())
        
        # High-reasoning keywords trigger high-fidelity model recommendations
        reasoning_keywords = {"analyze", "review", "refactor", "architect", "complex", "debug"}
        needs_high_fidelity = any(word in query_words for word in reasoning_keywords)

        for entry in data["routing_table"]:
            intent_words = set(entry["intent"].lower().split())
            intersection = query_words.intersection(intent_words)
            
            # Semantic match score based on keyword overlap
            semantic_score = len(intersection) / max(1, len(intent_words))
            
            # Final score combines semantic relevance and Worker Capability (WC)
            final_score = semantic_score * entry.get("wc_score", 1.0)
            
            if final_score > 0:
                # Override preferred model if high-fidelity is needed and not already set
                recommended_model = entry.get("preferred_model")
                if needs_high_fidelity and recommended_model == "gemini-2.0-flash":
                    recommended_model = "claude-3-5-sonnet-v2" # Upgrade for complex tasks

                scored_results.append({
                    **entry,
                    "match_score": round(final_score, 2),
                    "recommended_model": recommended_model
                })
        
        # Sort by match_score descending
        scored_results.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_results

    def list_capabilities(self) -> List[Dict[str, Any]]:
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        return data["routing_table"]
