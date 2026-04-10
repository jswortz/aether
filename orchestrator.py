import logging
from typing import Optional, List, Dict, Any
from core.headless_runner import HeadlessGeminiRunner
from core.toolsmith import Toolsmith
from core.router import AgentRouter
from core.recipes import get_recipe
from memory.context_buffer import ContextBuffer
from evals.judge_scoring import Judge

class AetherOrchestrator:
    """
    The main entry point for the Aether framework. 
    Coordinates the Supervisor, Memory, and Evolution loops.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("aether.orchestrator")
        self.runner = HeadlessGeminiRunner()
        self.memory = ContextBuffer()
        self.router = AgentRouter()
        self.toolsmith = Toolsmith(self.runner)
        self.judge = Judge(self.runner)
        
    def process_request(self, user_query: str) -> str:
        """
        Processes a user request through the Aether swarm, using the Agent Router
        to identify the best models, tools, or high-fidelity recipes.
        """
        self.logger.info(f"Processing request: {user_query}")
        
        # 1. Consult Agent Router for the best path
        routes = self.router.route(user_query)
        recipe_name = routes[0].get("recipe") if routes else None
        
        # 2. If a first-class Recipe is found, execute it
        if recipe_name:
            recipe = get_recipe(recipe_name)
            if recipe:
                self.logger.info(f"Executing first-class recipe: {recipe_name}")
                offline_mode = "offline" in user_query.lower() or "gemma" in user_query.lower()
                recipe_result = recipe.execute(user_query, offline_mode=offline_mode)
                response = recipe_result["output"]
                self.memory.add_memory(f"User: {user_query}\nRecipe [{recipe_name}]: {response}")
                return response

        # 3. Retrieve relevant memory context for standard execution
        context = self.memory.get_active_context(user_query)
        
        # 4. Execute via Supervisor Agent
        # The Supervisor is responsible for breaking down the task 
        # and handing it off to specialized workers or the Toolsmith.
        try:
            # Simulation of stall detection (Prodder integration)
            # In a real loop, we would monitor the 'steps' from the runner.
            steps_taken = 0
            max_steps = 15
            response = ""
            
            while steps_taken < max_steps:
                response = self.runner.execute_task(
                    f"Context from memory: {context}\n\nUser query: {user_query}", 
                    agent_name="aether-supervisor"
                )
                steps_taken += 1
                
                # If the response looks stuck or repetitive, trigger the Prodder
                if self._is_stalled(response):
                    self.logger.warning("Agent stall detected. Triggering Prodder...")
                    # The Supervisor is prodded to find a new path
                    user_query = self.runner.execute_task(
                        f"The current agent seems stuck. Provide a 'prod' stimulus to move the task forward.\nTrace: {response}",
                        agent_name="aether-supervisor"
                    )
                    continue
                
                break
            
            # 3. Add successful interaction to memory
            self.memory.add_memory(f"User: {user_query}\nAgent: {response}")
            
            return response

        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            # Potentially trigger self-correction or Toolsmith gap analysis here
            return f"I encountered an error: {str(e)}"

    def _is_stalled(self, response: str) -> bool:
        """
        Heuristic to detect if an agent is stuck in a loop or circular reasoning.
        """
        # Simple stall detection: placeholder for actual logic
        return False

    def run_eval(self, query: str, response: str, reference: str) -> Dict[str, Any]:
        """
        Runs 'The Judge' to evaluate a specific response.
        """
        return self.judge.score_output(query, response, reference)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = AetherOrchestrator()
