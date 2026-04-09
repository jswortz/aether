import os
import subprocess
import logging
from typing import Dict, Any, Optional
from aether.core.headless_runner import HeadlessGeminiRunner

class Toolsmith:
    """
    The Toolsmith handles the dynamic synthesis, testing, and registration
    of new tools based on capability gaps identified by the Supervisor.
    """
    
    def __init__(self, runner: HeadlessGeminiRunner, tools_dir: str = "aether/tools"):
        self.runner = runner
        self.tools_dir = tools_dir
        self.logger = logging.getLogger("aether.core.toolsmith")
        os.makedirs(self.tools_dir, exist_ok=True)

    def synthesize_tool(self, gap_description: str) -> Dict[str, Any]:
        """
        Delegates to the Toolsmith Agent to write a Python tool that fills the identified gap.
        """
        prompt = f"""
        Identify a capability gap: {gap_description}
        Write a robust Python function that addresses this gap.
        Requirements:
        1. Pure Python (standard library preferred).
        2. Type hinted and documented.
        3. Include a simple test function 'test_tool()' within the same file.
        4. Return only the Python code.
        """
        
        self.logger.info(f"Synthesizing tool for gap: {gap_description}")
        tool_code = self.runner.execute_task(prompt, agent_name="toolsmith-worker")
        
        # Extract code if wrapped in markdown blocks
        if "```python" in tool_code:
            tool_code = tool_code.split("```python")[1].split("```")[0].strip()
        elif "```" in tool_code:
             tool_code = tool_code.split("```")[1].split("```")[0].strip()
             
        return {"code": tool_code.strip()}

    def test_and_register(self, tool_name: str, tool_code: str) -> bool:
        """
        Writes the tool to a file, runs its internal tests, and registers it.
        """
        file_path = os.path.join(self.tools_dir, f"{tool_name}.py")
        
        with open(file_path, "w") as f:
            f.write(tool_code)
            
        try:
            self.logger.info(f"Testing tool: {tool_name}")
            # Run the tool as a script to trigger its internal test_tool()
            subprocess.run(["python3", file_path], check=True, capture_output=True)
            self.logger.info(f"Tool {tool_name} passed tests and is now registered.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Tool {tool_name} failed tests: {e.stderr.decode()}")
            # Move to a quarantine or failed directory
            return False

    def bridge_gap(self, gap_description: str, tool_name: str) -> bool:
        """
        High-level orchestration for filling a capability gap.
        """
        synthesis_result = self.synthesize_tool(gap_description)
        return self.test_and_register(tool_name, synthesis_result["code"])

if __name__ == "__main__":
    pass
    # Example integration test
    # runner = HeadlessGeminiRunner()
    # ts = Toolsmith(runner)
    # ts.bridge_gap("I need a way to calculate the Fibonacci sequence up to N", "fibonacci_tool")
