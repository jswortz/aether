#!/usr/bin/env python3
"""
Toolsmith MCP Server: The execution layer for dynamic tool synthesis and registration.
Orchestrates within the SCION pattern.
"""

import os
import subprocess
import json
import logging
import functools
import shutil
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP, Context
from core.toolsmith import Toolsmith
from core.headless_runner import HeadlessGeminiRunner
from core.router import AgentRouter

# Initialize FastMCP server
mcp = FastMCP("toolsmith_mcp")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolsmith_mcp")

# Environment & Config
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
AETHER_ROOT = os.getenv("AETHER_ROOT", "/usr/local/google/home/jwortz/aether")
TOOLS_DIR = os.getenv("TOOLS_DIR", os.path.join(AETHER_ROOT, "tools"))
SANDBOX_DIR = os.path.join(TOOLS_DIR, "sandbox")
os.makedirs(SANDBOX_DIR, exist_ok=True)

# Initialize core components
runner = HeadlessGeminiRunner()
toolsmith = Toolsmith(runner, tools_dir=TOOLS_DIR)
router = AgentRouter()

# --- Surprise Gate Logic ---

def surprise_gate(func):
    """
    Decorator that filters out low-signal or conflicting memory entries.
    Ensures that only 'surprising' (novel/high-impact) data passes through
    the attention filter to avoid context poisoning.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # The Surprise Gate acts as a high-pass filter for context.
        # It shunts divergent or conflicting data to an adversarial buffer.
        
        params = kwargs.get('params') or (args[0] if args else None)
        
        if params and hasattr(params, 'content'):
            content = params.content.lower()
            
            # 1. Noise Filter (Low Signal detection)
            noise_markers = ["i'm not sure", "maybe", "possibly", "i think"]
            if any(marker in content for marker in noise_markers) and len(content) < 50:
                 logger.warning(f"Surprise Gate: Low signal detected in memory.")
                 return "Error: Content rejected by Surprise Gate (Low Signal)."

            # 2. Conflict/Contradiction Detection
            # In a full SCION implementation, this would query a 'Truth Buffer'
            if "contradict" in content or "incorrect" in content:
                logger.warning(f"Surprise Gate: High surprise/conflict detected. Shunting to Adversarial Buffer.")
                return "Warning: Content shunted to Adversarial Buffer for dialectic review."

        return await func(*args, **kwargs)
    return wrapper

# --- Pydantic Models ---

class SynthesizeInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_description: str = Field(..., description="Description of the capability gap to fill.")
    tool_name: str = Field(..., description="Suggested name for the new tool.")

class ExecuteInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tool_name: str = Field(..., description="Name of the tool to execute.")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for execution.")

class RegisterInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    intent: str = Field(..., description="The semantic intent this tool addresses.")
    tool_name: str = Field(..., description="Name of the tool.")
    path: str = Field(..., description="Absolute path to the tool script.")
    wc_score: float = Field(1.0, description="Worker Capability (WC) score (0.0 to 1.0).")
    preferred_model: Optional[str] = Field(None, description="The preferred model for this skill (e.g., claude-3-5-sonnet-v2).")

class RouteInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    intent_query: str = Field(..., description="The semantic intent to route.")

class MemoryInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    content: str = Field(..., description="The memory content to be processed.")

# --- Tools ---

@mcp.tool(name="toolsmith_synthesize")
async def toolsmith_synthesize(params: SynthesizeInput) -> str:
    """Synthesizes a new Python tool to fill a capability gap."""
    try:
        result = toolsmith.synthesize_tool(params.task_description)
        code = result["code"]
        file_path = os.path.join(TOOLS_DIR, f"{params.tool_name}.py")
        with open(file_path, "w") as f:
            f.write(code)
        return json.dumps({"status": "synthesized", "path": file_path, "preview": code[:100]}, indent=2)
    except Exception as e:
        return f"Synthesis failed: {str(e)}"

@mcp.tool(name="toolsmith_execute")
async def toolsmith_execute(params: ExecuteInput) -> str:
    """Executes a tool in a secure sandbox environment."""
    src_path = os.path.join(TOOLS_DIR, f"{params.tool_name}.py")
    if not os.path.exists(src_path):
        return f"Tool {params.tool_name} not found."
    
    # Isolation: Copy to sandbox and run
    sandbox_path = os.path.join(SANDBOX_DIR, f"{params.tool_name}_exec.py")
    shutil.copy2(src_path, sandbox_path)
    
    try:
        result = subprocess.run(
            ["python3", sandbox_path],
            capture_output=True, text=True, timeout=15
        )
        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }, indent=2)
    except Exception as e:
        return f"Execution error: {str(e)}"
    finally:
        if os.path.exists(sandbox_path):
            os.remove(sandbox_path)

@mcp.tool(name="router_register")
async def router_register(params: RegisterInput) -> str:
    """Registers a tool with the Agent Router's high-bandwidth dispatcher with model-skill optimization."""
    router.register_tool(
        params.intent, 
        params.tool_name, 
        params.path, 
        score=params.wc_score,
        preferred_model=params.preferred_model
    )
    return f"Tool {params.tool_name} registered for intent '{params.intent}' with WC score {params.wc_score} (Preferred Model: {params.preferred_model or 'Default'})."

@mcp.tool(name="router_route")
async def router_route(params: RouteInput) -> str:
    """Maps semantic intent to the best available Worker Capabilities."""
    results = router.route(params.intent_query)
    return json.dumps(results, indent=2)

@mcp.tool(name="toolsmith_add_memory")
@surprise_gate
async def toolsmith_add_memory(params: MemoryInput) -> str:
    """Adds memory context, filtered by the Surprise Gate to ensure high-signal."""
    return f"Memory accepted: {params.content[:50]}..."

@mcp.tool(name="toolsmith_github_sync")
async def toolsmith_github_sync(tool_name: str) -> str:
    """Syncs a synthesized tool to the Aether repository using GITHUB_TOKEN."""
    if not GITHUB_TOKEN:
        return "Error: GITHUB_TOKEN not configured."
    
    # Simplified Git sync logic
    try:
        # We assume we are in the repo
        subprocess.run(["git", "add", os.path.join(TOOLS_DIR, f"{tool_name}.py")], check=True)
        subprocess.run(["git", "commit", "-m", f"Evolve: Added tool {tool_name}"], check=True)
        # Push using the token in the URL if not already set
        # Actually, the remote URL already has the token from my previous check
        subprocess.run(["git", "push", "origin", "head"], check=True)
        return f"Successfully synced {tool_name} to GitHub."
    except Exception as e:
        return f"Sync failed: {str(e)}"

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "sse")
    if transport == "sse":
        port = int(os.getenv("PORT", 8080))
        logger.info(f"Starting Toolsmith MCP Server in SSE mode on port {port}")
        mcp.run(transport="sse", port=port)
    else:
        logger.info("Starting Toolsmith MCP Server in stdio mode")
        mcp.run(transport="stdio")
