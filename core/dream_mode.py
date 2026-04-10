import os
import json
import logging
import glob
from typing import List, Dict, Any, Optional
from core.router import AgentRouter
from core.evolution import EvolutionEngine
from core.toolsmith import Toolsmith
from core.recipes import RecipeManager
from core.headless_runner import HeadlessGeminiRunner

class AetherDreamMode:
    """
    Dream Mode is a background process where Aether reflects on historical traces,
    runs counterfactual simulations, and evolves its capabilities while idle.
    """
    
    def __init__(self, assets_dir: str = "/usr/local/google/home/jwortz/aether/assets", 
                 router: Optional[AgentRouter] = None,
                 evolution_engine: Optional[EvolutionEngine] = None,
                 toolsmith: Optional[Toolsmith] = None,
                 recipe_manager: Optional[RecipeManager] = None,
                 runner: Optional[HeadlessGeminiRunner] = None):
        self.assets_dir = assets_dir
        self.runner = runner or HeadlessGeminiRunner()
        self.router = router or AgentRouter()
        self.evolution_engine = evolution_engine or EvolutionEngine(runner=self.runner)
        self.toolsmith = toolsmith or Toolsmith(runner=self.runner)
        self.recipe_manager = recipe_manager or RecipeManager()
        
        self.logger = logging.getLogger("aether.core.dream_mode")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO)

    def run_dream_cycle(self):
        """Main entry point for a Dream Mode session."""
        self.logger.info("Aether entering Dream Mode...")
        
        traces = self._load_historical_traces()
        if not traces:
            self.logger.info("No traces found to reflect upon. System is at peace.")
            return

        for run_id, trace_data in traces.items():
            self.logger.info(f"Reflecting on trace: {run_id}")
            
            # 1. Performance Evaluation
            reflection = self._reflect_and_score(run_id, trace_data)
            score = reflection.get("score", 1.0)
            gap = reflection.get("gap_identified")
            
            self.logger.info(f"Trace {run_id} Score: {score}")

            # 2. Counterfactual Simulation for low-performing runs
            if score < 0.7:
                self.logger.info(f"Low performance detected. Running counterfactual simulation...")
                sim_results = self._counterfactual_simulation(trace_data, gap)
                self.logger.info(f"Counterfactual insight: {sim_results.get('insight')}")
                
                # 3. Update Router Scores
                self._update_router_scores(trace_data, score)

                # 4. Trigger Evolution / Toolsmith / RecipeSmith
                if sim_results.get("requires_new_recipe") and gap:
                    self.logger.info(f"Complex gap identified: {gap}. Synthesizing new Recipe.")
                    self._synthesize_recipe(gap)
                elif sim_results.get("requires_new_tool") and gap:
                    self.logger.info(f"Tool gap identified: {gap}. Triggering Toolsmith.")
                    self._trigger_evolution(gap)
            else:
                # Even for good runs, we might want to boost scores slightly
                self._update_router_scores(trace_data, score)

        self.logger.info("Aether Dream Mode cycle complete. Waking up.")

    def _load_historical_traces(self) -> Dict[str, Any]:
        """Loads metadata and planning data from recent runs."""
        run_dirs = glob.glob(os.path.join(self.assets_dir, "run_*"))
        traces = {}
        
        for run_dir in run_dirs:
            run_id = os.path.basename(run_dir)
            metadata_path = os.path.join(run_dir, "metadata.json")
            planning_path = os.path.join(run_dir, "planning.json")
            
            if os.path.exists(metadata_path) and os.path.exists(planning_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    with open(planning_path, 'r') as f:
                        planning = json.load(f)
                    
                    traces[run_id] = {
                        "metadata": metadata,
                        "planning": planning,
                        "path": run_dir
                    }
                except json.JSONDecodeError:
                    continue
        return traces

    def _reflect_and_score(self, run_id: str, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Uses LLM to evaluate the performance of a past run."""
        prompt = f"""
        ### SYSTEM: REFLECTION AGENT
        Analyze the following trace of an agent run (Run ID: {run_id}).
        
        METADATA:
        {json.dumps(trace_data['metadata'], indent=2)}
        
        PLANNING & OUTPUT:
        {json.dumps(trace_data['planning'], indent=2)}
        
        Evaluate the success of this run on a scale of 0.0 to 1.0.
        Identify any capability gaps or tool failures.
        
        Output your analysis in JSON format:
        {{
            "score": float,
            "reasoning": "...",
            "gap_identified": "description of any missing capability or tool improvement"
        }}
        """
        try:
            response = self.runner.execute_task(prompt)
            # Try to extract JSON from the response
            start = response.find('{')
            end = response.rfind('}') + 1
            return json.loads(response[start:end])
        except Exception as e:
            self.logger.error(f"Error during reflection for {run_id}: {e}")
            return {"score": 1.0, "gap_identified": None}

    def _counterfactual_simulation(self, trace_data: Dict[str, Any], gap: Optional[str]) -> Dict[str, Any]:
        """Runs a 'What If' scenario to see if a different approach would have worked."""
        prompt = f"""
        ### SYSTEM: COUNTERFACTUAL SIMULATOR
        We identified a gap in a previous run: "{gap or 'Sub-optimal tool selection'}"
        
        TRACE DATA:
        {json.dumps(trace_data['planning'], indent=2)}
        
        SIMULATION TASK:
        If we had a 'Recipe' (complex workflow) or a new 'Tool' specifically designed for: "{gap or 'improving performance'}", 
        how would the outcome change? 
        
        Special Case Analysis:
        If the user requested something like "completely offline high-temp mixture of experts recipe for gemma 4", 
        and the current system failed or used an online model, simulate the benefit of a "gemma-4-offline-moe" Recipe.
        
        Output in JSON format:
        {{
            "insight": "...",
            "requires_new_tool": boolean,
            "requires_new_recipe": boolean,
            "suggested_type": "recipe" | "tool",
            "suggested_name": "..."
        }}
        """
        try:
            response = self.runner.execute_task(prompt)
            start = response.find('{')
            end = response.rfind('}') + 1
            return json.loads(response[start:end])
        except Exception as e:
            self.logger.error(f"Error during counterfactual simulation: {e}")
            return {"insight": "Simulation failed", "requires_new_tool": False, "requires_new_recipe": False}

    def _update_router_scores(self, trace_data: Dict[str, Any], score: float):
        """Adjusts WC scores in the router registry based on performance."""
        intent = trace_data.get("planning", {}).get("initial_description", "")[:100]
        matches = self.router.route(intent)
        
        if matches:
            top_tool = matches[0]["tool_name"]
            current_score = matches[0].get("wc_score", 1.0)
            
            # Dampened update
            alpha = 0.2
            new_score = current_score * (1 - alpha) + score * alpha
            
            self.logger.info(f"Updating WC score for {top_tool}: {current_score} -> {new_score}")
            self.router.register_tool(
                intent=matches[0]["intent"],
                tool_name=top_tool,
                path=matches[0]["path"],
                score=new_score,
                preferred_model=matches[0].get("preferred_model"),
                metadata=matches[0].get("metadata")
            )

    def _synthesize_recipe(self, gap: str):
        """Synthesizes a new Recipe manifest to fill a capability gap."""
        prompt = f"""
        ### SYSTEM: RECIPE ARCHITECT
        Identify a complex capability gap: {gap}
        
        Design a 'Recipe' manifest (JSON) to address this gap.
        The recipe should follow this schema:
        {{
            "recipe_id": "string-id",
            "version": "1.0.0",
            "description": "...",
            "intent_match": "keywords for routing",
            "workflow": {{
                "engine": "core.module.ClassName",
                "method": "method_to_call",
                "params": {{ ... }}
            }},
            "metadata": {{ "tags": [...], "wc_score": 1.0 }}
        }}
        
        Available engines: core.moe.HighTempMoE, core.evolution.EvolutionEngine, core.toolsmith.Toolsmith
        
        Output ONLY the JSON manifest.
        """
        try:
            self.logger.info(f"Synthesizing recipe for gap: {gap}")
            response = self.runner.execute_task(prompt)
            start = response.find('{')
            end = response.rfind('}') + 1
            recipe_data = json.loads(response[start:end])
            self.recipe_manager.register_recipe(recipe_data)
            self.logger.info(f"New recipe registered: {recipe_data.get('recipe_id')}")
        except Exception as e:
            self.logger.error(f"Error synthesizing recipe: {e}")

    def _trigger_evolution(self, gap: str):
        """Calls the Toolsmith to synthesize a new tool."""
        tool_name_prompt = f"Given this gap: '{gap}', suggest a short, snake_case tool name. Output ONLY the name."
        try:
            suggested_name = self.runner.execute_task(tool_name_prompt).strip()
            suggested_name = "".join(c for c in suggested_name if c.isalnum() or c == "_")
            self.toolsmith.bridge_gap(gap, suggested_name)
        except Exception as e:
            self.logger.error(f"Error triggering evolution: {e}")

if __name__ == "__main__":
    dreamer = AetherDreamMode()
    dreamer.run_dream_cycle()
