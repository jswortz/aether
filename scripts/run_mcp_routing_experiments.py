import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.router import AgentRouter
import json

def run_experiments():
    router = AgentRouter(registry_path="core/router_registry.json")
    router.register_tool("text processing data transformation", "mcp_transformer", "/usr/bin/transformer", score=1.0)
    router.register_tool("run test verify application", "mcp_verifier", "/usr/bin/verifier", score=0.8)
    
    print("=========================================")
    print("EXPERIMENT 1: Pass-Through Routing (Opus 4.6)")
    print("=========================================")
    res1 = router.route("run test verify application", force_model="opus 4.6")
    print(json.dumps(res1[0], indent=2))
    
    print("\n=========================================")
    print("EXPERIMENT 2: Offline / Airgapped Trigger (Gemma 4)")
    print("=========================================")
    res2 = router.route("run test verify application offline")
    print(json.dumps(res2[0], indent=2))
    
    print("\n=========================================")
    print("EXPERIMENT 3: Mixture of Experts (MoE)")
    print("=========================================")
    res3 = router.route("text processing data transformation", use_moe=True)
    print(json.dumps(res3[0], indent=2))

if __name__ == "__main__":
    run_experiments()
