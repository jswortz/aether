import logging
from typing import List, Dict, Any, Optional
from core.headless_runner import HeadlessGeminiRunner

class EvolutionEngine:
    """
    The EvolutionEngine implements meta-evolution loops for Project Aether,
    enabling agents to self-improve through adversarial debate and 
    trajectory compression.
    """
    
    def __init__(self, runner: Optional[HeadlessGeminiRunner] = None):
        self.runner = runner or HeadlessGeminiRunner()
        self.logger = logging.getLogger("aether.core.evolution")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO)

    def adversarial_debate(self, agent_name: str, current_instructions: str, iterations: int = 3) -> str:
        """
        Refines agent instructions through an iterative debate between an 
        Optimizer agent and a Critic agent.
        
        Args:
            agent_name: The name of the agent whose instructions are being refined.
            current_instructions: The starting instructions for the agent.
            iterations: Number of debate cycles to perform.
            
        Returns:
            The final, refined agent instructions.
        """
        self.logger.info(f"Starting Adversarial Debate for agent: {agent_name}")
        refined_instructions = current_instructions

        for i in range(iterations):
            self.logger.info(f"Iteration {i+1}/{iterations}")
            
            try:
                # 1. Critic phase: Identify weaknesses in the current instructions
                critic_query = (
                    f"### SYSTEM: CRITIC AGENT\n"
                    f"Your mission is to rigorously analyze the following instructions for the '{agent_name}' agent. "
                    f"Search for logical fallacies, security vulnerabilities, prompt injection risks, "
                    f"and areas of ambiguity that could lead to sub-optimal performance.\n\n"
                    f"CURRENT INSTRUCTIONS:\n{refined_instructions}\n\n"
                    f"Provide your critique as a structured list of actionable improvements."
                )
                critique = self.runner.execute_task(critic_query)
                self.logger.info(f"Critic feedback received.")

                # 2. Optimizer phase: Revise instructions based on the critique
                optimizer_query = (
                    f"### SYSTEM: OPTIMIZER AGENT\n"
                    f"Your mission is to evolve the instructions for the '{agent_name}' agent. "
                    f"Take the following Critic feedback and synthesize it into a superior version of the instructions. "
                    f"Ensure the new version is more robust, clear, and effective while retaining all core functionality.\n\n"
                    f"FEEDBACK:\n{critique}\n\n"
                    f"ORIGINAL INSTRUCTIONS:\n{refined_instructions}\n\n"
                    f"Output ONLY the final REVISED INSTRUCTIONS. Do not include preamble or explanations."
                )
                refined_instructions = self.runner.execute_task(optimizer_query)
                self.logger.info(f"Optimizer refinement complete.")
            except Exception as e:
                self.logger.error(f"Error during debate iteration {i+1}: {e}")
                break

        return refined_instructions

    def trajectory_compression(self, traces: List[str]) -> List[str]:
        """
        Analyzes session traces to prune redundant reasoning steps and optimize 
        agent trajectories.
        
        Args:
            traces: A list of session traces (strings) representing agent interactions.
            
        Returns:
            A list of compressed session traces.
        """
        self.logger.info(f"Starting Trajectory Compression for {len(traces)} traces")
        compressed_traces = []

        for idx, trace in enumerate(traces):
            try:
                compression_query = (
                    f"### SYSTEM: TRAJECTORY COMPRESSOR\n"
                    f"Analyze the following successful agent session trace. Your goal is to "
                    f"perform 'Lossless Compression' of the reasoning steps. Remove any "
                    f"redundant thoughts, circular explorations, or 'stuttering' in the "
                    f"logic chain. The resulting trace should be the most efficient path "
                    f"that leads to the same successful outcome.\n\n"
                    f"TRACE:\n{trace}\n\n"
                    f"Output the compressed version of the trace."
                )
                compressed_trace = self.runner.execute_task(compression_query)
                compressed_traces.append(compressed_trace)
                self.logger.info(f"Compressed trace {idx+1}/{len(traces)}")
            except Exception as e:
                self.logger.error(f"Error compressing trace {idx+1}: {e}")
                compressed_traces.append(trace) # Fallback to original

        return compressed_traces

if __name__ == "__main__":
    # Example usage for testing
    engine = EvolutionEngine()
    
    # Test Adversarial Debate
    initial_instructions = "You are a helpful assistant that answers questions clearly."
    # refined = engine.adversarial_debate("Assistant", initial_instructions, iterations=1)
    # print(f"REFINED:\n{refined}")
    
    # Test Trajectory Compression
    sample_trace = "Step 1: Thought: I need to find the capital of France. Step 2: Action: Search for capital of France. Step 3: Thought: I found that Paris is the capital. Step 4: Answer: Paris."
    # compressed = engine.trajectory_compression([sample_trace])
    # print(f"COMPRESSED:\n{compressed[0]}")
