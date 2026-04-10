import logging
import json
import concurrent.futures
import functools
from typing import List, Dict, Any, Optional
from core.headless_runner import HeadlessGeminiRunner

class HighTempMoE:
    """
    Implements the High-Temp Mixture of Experts (MoE) pattern.
    A Moderator triggers multiple high-temperature completions from different
    experts (Gemini, Claude, Gemma) and synthesizes them into a single conclusion.
    """
    def __init__(self, runner: Optional[HeadlessGeminiRunner] = None):
        self.runner = runner or HeadlessGeminiRunner()
        self.logger = logging.getLogger("aether.core.moe")

    def _surprise_gate_filter(self, content: str) -> bool:
        """
        Security: Surprise Gate logic to filter out stochastic noise and low-signal responses.
        Ensures only high-fidelity, novel, or impactful data passes through.
        """
        content_lower = content.lower()
        # Stochastic noise markers
        noise_markers = [
            "i'm not sure", "maybe", "possibly", "i think", 
            "likely", "might be", "hallucination", "unclear"
        ]
        
        # 1. Low Signal Check (Too much uncertainty in a short response)
        noise_count = sum(1 for marker in noise_markers if marker in content_lower)
        if noise_count > 2 and len(content) < 150:
            self.logger.warning(f"MoE Surprise Gate: Stochastic noise detected ({noise_count} markers).")
            return False
        
        # 2. Minimum Substantiality
        if len(content.strip()) < 50:
            self.logger.warning("MoE Surprise Gate: Response too short to be considered high-fidelity.")
            return False
            
        # 3. Conflict Detection (Mock: in a full SCION, this would check against a Truth Buffer)
        if "contradiction" in content_lower or "error in reasoning" in content_lower:
             self.logger.info("MoE Surprise Gate: Self-identified reasoning error detected.")
             return False

        return True

    def trigger_experts(self, prompt: str, models: List[str] = None, temperature: float = 0.9) -> List[Dict[str, Any]]:
        """
        Triggers multiple high-temperature completions from the specified experts.
        """
        if models is None:
            models = ["gemini-2.0-flash", "claude-3-5-sonnet-v2", "gemini-2.5-pro"]
            
        self.logger.info(f"Triggering MoE with experts: {models} at temperature {temperature}")
        
        results = []
        
        # Use ThreadPoolExecutor for parallel expert invocation to minimize latency
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as executor:
            # We wrap the call in a way that includes the temperature directive
            future_to_model = {
                executor.submit(self._call_expert, prompt, model, temperature): model 
                for model in models
            }
            
            for future in concurrent.futures.as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    output = future.result()
                    if self._surprise_gate_filter(output):
                        results.append({"model": model, "output": output})
                        self.logger.info(f"Expert {model} output accepted by Surprise Gate.")
                    else:
                        self.logger.warning(f"Expert {model} output rejected by Surprise Gate (Stochastic Noise).")
                except Exception as exc:
                    self.logger.error(f"Expert {model} failed: {exc}")
                    
        return results

    def _call_expert(self, prompt: str, model: str, temperature: float) -> str:
        """
        Executes a high-temperature prompt for a specific model.
        """
        # System directive to simulate high-temperature if the CLI wrapper doesn't support it directly
        directive = (
            f"[SYSTEM DIRECTIVE: You are an expert specialist. "
            f"Execute with maximum creativity and divergent thinking. "
            f"Set conceptual temperature to {temperature}.]"
        )
        moe_prompt = f"{directive}\n\nTask: {prompt}"
        
        # Using @agent syntax for model selection
        return self.runner.execute_task(moe_prompt, agent_name=model)

    def synthesize(self, prompt: str, expert_outputs: List[Dict[str, Any]], moderator_model: str = "gemini-2.5-pro") -> str:
        """
        The Moderator agent synthesizes the diverse 'Expert' outputs into a single, high-fidelity conclusion.
        """
        if not expert_outputs:
            return "MoE Synthesis Error: No expert outputs survived the Surprise Gate filtering."

        synthesis_prompt = f"""
        You are the Aether MoE Moderator (High-Fidelity Synthesizer).
        I have collected diverse responses from multiple specialized experts for the prompt below.
        
        ORIGINAL PROMPT: {prompt}
        
        EXPERT CONTRIBUTIONS:
        """
        
        for i, res in enumerate(expert_outputs):
            synthesis_prompt += f"\n--- EXPERT {i+1} (Model: {res['model']}) ---\n{res['output']}\n"
            
        synthesis_prompt += """
        MODERATOR TASKS:
        1. Compare and contrast the expert findings.
        2. Filter out any remaining stochastic noise or hallucinations.
        3. Extract the highest-signal insights from each expert.
        4. Resolve any technical contradictions using first-principles reasoning.
        5. Provide a single, unified, high-fidelity conclusion.
        
        If the context is 'Deep Debugging', focus on root cause convergence.
        If the context is 'Creative Architecting', focus on innovative synthesis.
        
        Synthesized Conclusion:
        """
        
        self.logger.info(f"Moderator synthesizing results using {moderator_model}...")
        # Moderator itself should be the highest fidelity model available
        synthesis = self.runner.execute_task(synthesis_prompt, agent_name=moderator_model)
        
        # --- Eval Closed Loop: Adversarial Review ---
        self.logger.info(f"Triggering Adversarial Review using {moderator_model}...")
        review = self._adversarial_review(prompt, synthesis, reviewer_model=moderator_model)
        
        if review["score"] < 4:
            self.logger.warning(f"Adversarial Review flagged low fidelity (Score: {review['score']}). Reasoning: {review['reasoning']}")
            # In a full SCION loop, this might trigger a second synthesis pass
            return f"Synthesized Result (Warning: Low Fidelity Score {review['score']}):\n{synthesis}\n\nReview Feedback: {review['reasoning']}"
        
        return synthesis

    def _adversarial_review(self, query: str, output: str, reviewer_model: str = "claude-3-5-sonnet-v2") -> Dict[str, Any]:
        """
        Closed-loop evaluation: An Adversarial Reviewer attempts to find flaws in the synthesis.
        """
        review_prompt = (
            f"### SYSTEM: ADVERSARIAL REVIEWER\n"
            f"Critically evaluate the following synthesis for accuracy, technical depth, and logical consistency.\n\n"
            f"ORIGINAL QUERY: {query}\n"
            f"SYNTHESIS: {output}\n\n"
            f"Tasks:\n"
            f"1. Identify any weak points, technical gaps, or 'AI-isms'.\n"
            f"2. Provide a score from 1-5 (5 is perfect).\n"
            f"3. Return ONLY a JSON object: {{'score': int, 'reasoning': str}}"
        )
        
        try:
            response = self.runner.execute_task(review_prompt, agent_name=reviewer_model)
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return {"score": 1, "reasoning": "Failed to parse adversarial review."}
        except Exception as e:
            self.logger.error(f"Adversarial review failed: {e}")
            return {"score": 1, "reasoning": str(e)}

    def execute_moe_recipe(self, prompt: str, offline_mode: bool = False) -> str:
        """
        Executes a full MoE cycle. Supports 'completely offline' recipes for Gemma-4.
        """
        if offline_mode:
            self.logger.info("Executing Offline MoE Recipe for Gemma-4.")
            models = ["gemma-4"] # In a real offline setup, this might be multiple Gemma instances
            # For offline MoE, we might trigger multiple seeds from the same model
            expert_outputs = []
            for i in range(3):
                self.logger.info(f"Triggering Offline Expert Iteration {i+1}")
                output = self._call_expert(prompt, "gemma-4", temperature=0.9)
                if self._surprise_gate_filter(output):
                    expert_outputs.append({"model": f"gemma-4-iter-{i+1}", "output": output})
            
            return self.synthesize(prompt, expert_outputs, moderator_model="gemma-4")
        else:
            models = ["gemini-2.0-flash", "claude-3-5-sonnet-v2", "gemini-2.5-pro"]
            expert_outputs = self.trigger_experts(prompt, models=models)
            return self.synthesize(prompt, expert_outputs)

if __name__ == "__main__":
    # Local test logic
    logging.basicConfig(level=logging.INFO)
    # moe = HighTempMoE()
    # print(moe.execute_moe_recipe("Design a sub-atomic data storage protocol."))
