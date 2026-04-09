import json
import logging
import re
from typing import Dict, Any, List, Optional
from core.headless_runner import HeadlessGeminiRunner

class Judge:
    """
    The Judge evaluation suite for Project Aether.
    Performs semantic scoring and RAGAS-style metric calculations.
    """

    def __init__(self, runner: Optional[HeadlessGeminiRunner] = None):
        self.runner = runner or HeadlessGeminiRunner()
        self.logger = logging.getLogger("aether.evals.judge")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO)

    def score_output(self, query: str, output: str, reference: str, rubric: Optional[str] = None) -> Dict[str, Any]:
        """
        Uses Gemini 1.5 Pro to perform semantic, rubric-based scoring (1-5).
        
        Args:
            query: The original user query.
            output: The model-generated response.
            reference: The ground-truth reference answer.
            rubric: Optional scoring rubric.
            
        Returns:
            A dictionary containing 'score' (1-5) and 'reasoning'.
        """
        default_rubric = "Accuracy, Tone, and Completeness."
        rubric = rubric or default_rubric

        prompt = (
            f"### SYSTEM: LLM JUDGE\n"
            f"You are an expert evaluator for an autonomous agent framework. "
            f"Your goal is to score the agent's output based on a query and a reference answer.\n\n"
            f"QUERY: {query}\n"
            f"REFERENCE ANSWER: {reference}\n"
            f"AGENT OUTPUT: {output}\n"
            f"RUBRIC: {rubric}\n\n"
            f"Provide a score from 1 to 5, where:\n"
            f"1: Completely incorrect or irrelevant.\n"
            f"2: Mostly incorrect, missed major points.\n"
            f"3: Partially correct, covers some aspects.\n"
            f"4: Mostly correct, minor omissions.\n"
            f"5: Perfect or near-perfect.\n\n"
            f"Output ONLY a valid JSON object with keys 'score' (integer) and 'reasoning' (string)."
        )

        try:
            response_text = self.runner.execute_task(prompt)
            # Extract JSON from potential markdown backticks
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return result
            else:
                self.logger.error(f"Failed to parse JSON from response: {response_text}")
                return {"score": 0, "reasoning": "Error parsing judge response"}
        except Exception as e:
            self.logger.error(f"Error during scoring: {e}")
            return {"score": 0, "reasoning": f"Exception: {str(e)}"}

    def calculate_context_precision(self, query: str, retrieved_contexts: List[str], reference: str) -> float:
        """
        Calculates Context Precision: how relevant retrieved chunks are to the query.
        
        Args:
            query: The original query.
            retrieved_contexts: List of strings retrieved by the agent.
            reference: The ground-truth answer.
            
        Returns:
            A float score between 0.0 and 1.0.
        """
        if not retrieved_contexts:
            return 0.0

        relevant_count = 0
        for context in retrieved_contexts:
            relevance_prompt = (
                f"### SYSTEM: RELEVANCE JUDGE\n"
                f"Determine if the following context is relevant for answering the query.\n\n"
                f"QUERY: {query}\n"
                f"REFERENCE: {reference}\n"
                f"CONTEXT: {context}\n\n"
                f"Is the context relevant? Output 'YES' or 'NO' and nothing else."
            )
            try:
                response = self.runner.execute_task(relevance_prompt).strip().upper()
                if "YES" in response:
                    relevant_count += 1
            except Exception as e:
                self.logger.error(f"Error judging context relevance: {e}")

        return relevant_count / len(retrieved_contexts)

    def calculate_tool_selection_accuracy(self, actual_calls: List[Dict[str, Any]], expected_calls: List[Dict[str, Any]]) -> float:
        """
        Calculates Tool Selection Accuracy based on session traces.
        Validates that the right tools were called with correct parameters.
        
        Args:
            actual_calls: List of dicts with 'tool' and 'parameters'.
            expected_calls: List of dicts with 'tool' and 'parameters'.
            
        Returns:
            A float score between 0.0 and 1.0.
        """
        if not expected_calls:
            return 1.0 if not actual_calls else 0.0
        
        if not actual_calls:
            return 0.0

        correct_calls = 0
        # Compare actual calls against expected calls.
        # This implementation uses a simple positional match.
        for i in range(min(len(actual_calls), len(expected_calls))):
            actual = actual_calls[i]
            expected = expected_calls[i]
            
            if actual.get("tool") == expected.get("tool"):
                # Semantic parameter check could be added here, 
                # but we'll start with strict equality.
                if actual.get("parameters") == expected.get("parameters"):
                    correct_calls += 1
                else:
                    # Fallback to LLM if parameters are complex strings
                    param_prompt = (
                        f"### SYSTEM: PARAMETER JUDGE\n"
                        f"Are these two sets of tool parameters semantically equivalent?\n"
                        f"ACTUAL: {json.dumps(actual.get('parameters'))}\n"
                        f"EXPECTED: {json.dumps(expected.get('parameters'))}\n\n"
                        f"Output 'YES' or 'NO' and nothing else."
                    )
                    try:
                        resp = self.runner.execute_task(param_prompt).strip().upper()
                        if "YES" in resp:
                            correct_calls += 1
                    except:
                        pass
        
        # Penalize for extra or missing calls
        denominator = max(len(actual_calls), len(expected_calls))
        return correct_calls / denominator

if __name__ == "__main__":
    # Example usage / sanity check
    judge = Judge()
    # print(judge.score_output("Who is the CEO of Google?", "Sundar Pichai", "Sundar Pichai"))
