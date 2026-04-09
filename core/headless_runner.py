import subprocess
import json
import logging
from typing import Dict, Any, List, Optional

class HeadlessGeminiRunner:
    """
    A headless wrapper for the Gemini CLI, allowing programmatic interaction
    and integration into the Aether orchestration framework.
    """
    
    def __init__(self, executable_path: str = "/tmp/sar.gemini.879027.f0382b00bd357cadcbbc575a1c2336cb6b5aa334/gemini_impl.runfiles/google3/third_party/javascript/node_modules/google_gemini_cli/wrapper.sh"):
        self.executable_path = executable_path
        self.logger = logging.getLogger("aether.core.headless_runner")
        logging.basicConfig(level=logging.INFO)

    def run_command(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a command via the Gemini CLI and captures the output.
        """
        # Using --prompt for headless execution and --approval-mode yolo for autonomous tool approval
        cmd = [self.executable_path, "--prompt", query, "--approval-mode", "yolo"]
        
        if context:
            cmd.extend(["--context", context])
            
        try:
            self.logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            return {
                "status": "success",
                "output": result.stdout.strip(),
                "error": result.stderr.strip()
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e.stderr}")
            return {
                "status": "error",
                "output": e.stdout.strip(),
                "error": e.stderr.strip(),
                "exit_code": e.returncode
            }

    def execute_task(self, task_description: str, agent_name: Optional[str] = None) -> str:
        """
        Executes a complex task, optionally specifying a target agent.
        """
        query = task_description
        if agent_name:
            query = f"@{agent_name} {task_description}"
            
        response = self.run_command(query)
        if response["status"] == "success":
            return response["output"]
        else:
            raise RuntimeError(f"Task failed: {response['error']}")

if __name__ == "__main__":
    runner = HeadlessGeminiRunner()
    # Example usage:
    # print(runner.execute_task("list files in the current directory"))
