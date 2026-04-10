import os
import json
import logging
from typing import List, Dict, Any, Optional
from importlib import import_module

class RecipeManager:
    """
    Manages Aether Recipes: declarative manifests for complex agentic workflows.
    Inspired by GKE Recipes and distributed systems blueprints.
    Supports multi-step workflows with integrated evaluation loops.
    """
    def __init__(self, recipes_dir: str = "/usr/local/google/home/jwortz/aether/recipes"):
        self.recipes_dir = recipes_dir
        self.logger = logging.getLogger("aether.core.recipes")
        os.makedirs(self.recipes_dir, exist_ok=True)
        self._ensure_default_recipes()

    def _ensure_default_recipes(self):
        """Seed the system with initial high-value recipes."""
        gemma_recipe = {
            "recipe_id": "gemma-4-offline-moe",
            "version": "1.1.0",
            "description": "Completely offline high-temp mixture of experts recipe for Gemma 4 with integrated evaluation.",
            "intent_match": "offline moe gemma",
            "workflow": {
                "steps": [
                    {
                        "name": "execution",
                        "engine": "core.moe.HighTempMoE",
                        "method": "execute_moe_recipe",
                        "params": {
                            "offline_mode": True,
                            "temperature": 1.2
                        }
                    },
                    {
                        "name": "review",
                        "engine": "core.evolution.EvolutionEngine",
                        "method": "adversarial_debate",
                        "params": {
                            "agent_name": "MoE-Moderator-Reviewer",
                            "iterations": 1
                        }
                    }
                ]
            },
            "metadata": {
                "tags": ["offline", "moe", "high-temp", "eval-closed-loop"],
                "wc_score": 1.0
            }
        }
        self.register_recipe(gemma_recipe)

    def register_recipe(self, recipe_data: Dict[str, Any]):
        """Saves a recipe manifest to the recipes directory."""
        recipe_id = recipe_data.get("recipe_id")
        if not recipe_id:
            raise ValueError("Recipe must have a 'recipe_id'")
        
        file_path = os.path.join(self.recipes_dir, f"{recipe_id}.json")
        with open(file_path, 'w') as f:
            json.dump(recipe_data, f, indent=2)
        self.logger.info(f"Registered recipe: {recipe_id}")

    def list_recipes(self) -> List[Dict[str, Any]]:
        """Lists all available recipes."""
        recipes = []
        if not os.path.exists(self.recipes_dir):
            return []
        for filename in os.listdir(self.recipes_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.recipes_dir, filename), 'r') as f:
                        recipes.append(json.load(f))
                except Exception:
                    continue
        return recipes

    def get_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        file_path = os.path.join(self.recipes_dir, f"{recipe_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    def execute_recipe(self, recipe_id: str, user_input: str) -> Any:
        """Dynamic execution of a multi-step recipe workflow with a closed-loop review phase."""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found.")

        workflow = recipe.get("workflow", {})
        steps = workflow.get("steps", [])
        
        if not steps:
            # Fallback to single-step legacy format
            engine_path = workflow.get("engine")
            method_name = workflow.get("method")
            params = workflow.get("params", {})
            steps = [{"name": "execution", "engine": engine_path, "method": method_name, "params": params}]

        current_result = user_input
        history = []

        self.logger.info(f"Executing Recipe: {recipe_id} with {len(steps)} steps")
        
        for step in steps:
            name = step.get("name")
            engine_path = step.get("engine")
            method_name = step.get("method")
            params = step.get("params", {})

            self.logger.info(f"Step '{name}': Calling {engine_path}.{method_name}")
            
            # Dynamic import and instantiation
            module_path, class_name = engine_path.rsplit(".", 1)
            module = import_module(module_path)
            engine_class = getattr(module, class_name)
            engine_instance = engine_class()
            
            method = getattr(engine_instance, method_name)
            
            # Execute step.
            # If it's a review step, it typically critiques the current_result.
            # adversarial_debate takes (agent_name, current_instructions)
            # We might need to adapt the args depending on the method.
            if method_name == "adversarial_debate":
                 current_result = method(params.get("agent_name", "Worker"), current_result, iterations=params.get("iterations", 1))
            else:
                 current_result = method(current_result, **params)
            
            history.append({"step": name, "output": current_result})
            
        return {"final_result": current_result, "history": history}

    def route_to_recipe(self, intent_query: str) -> Optional[str]:
        """Finds the best matching recipe for a given intent."""
        recipes = self.list_recipes()
        best_match = None
        max_score = 0
        
        query_words = set(intent_query.lower().split())
        
        for recipe in recipes:
            match_str = recipe.get("intent_match", "").lower()
            match_words = set(match_str.split())
            intersection = query_words.intersection(match_words)
            
            score = len(intersection) / max(1, len(match_words))
            if score > max_score and score > 0.4: # Lowered threshold slightly
                max_score = score
                best_match = recipe["recipe_id"]
                
        return best_match

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    manager = RecipeManager()
    recipe_id = manager.route_to_recipe("offline moe for gemma")
    print(f"Routed to: {recipe_id}")
