#!/usr/bin/env python3
"""
Claude Editor: Bridge between Aether Agent Router and Anthropic's Claude Code CLI.
Enables autonomous code modifications within the SCION pattern.
"""
import subprocess
import sys
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude_editor")

def modify_code(prompt: str) -> str:
    """
    Invokes the Claude CLI to perform code modifications.
    Assumes 'claude auth login' has been completed.
    """
    logger.info(f"Executing Claude Code with prompt: {prompt[:50]}...")
    
    # Using --yes to auto-confirm changes if supported, or -p for the prompt
    # Adjust flags based on the specific version of Claude Code installed
    cmd = ["claude", "-p", prompt]
    
    try:
        # We use a shell-like execution if needed, but subprocess.run is safer
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300 # Code modification can take time
        )
        
        if result.returncode != 0:
            logger.error(f"Claude Code failed: {result.stderr}")
            return f"Error: {result.stderr}"
            
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Claude Code timed out.")
        return "Error: Timeout during code modification."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 claude_editor.py <prompt>")
        sys.exit(1)
        
    user_prompt = " ".join(sys.argv[1:])
    print(modify_code(user_prompt))
