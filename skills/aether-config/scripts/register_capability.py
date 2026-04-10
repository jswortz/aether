#!/usr/bin/env python3
import argparse
import sys
import os

# Add project root to path to import core.router
sys.path.append(os.getcwd())

try:
    from core.router import AgentRouter
except ImportError:
    print("Error: Could not find core.router. Run this script from the project root.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Register a new capability in the Aether Agent Router.")
    parser.add_argument("--intent", required=True, help="The semantic intent this tool addresses.")
    parser.add_argument("--name", required=True, help="Name of the tool.")
    parser.add_argument("--path", required=True, help="Absolute path to the tool script.")
    parser.add_argument("--score", type=float, default=1.0, help="Worker Capability (WC) score (0.0 to 1.0).")
    parser.add_argument("--model", help="Preferred model (e.g., claude-3-5-sonnet-v2).")

    args = parser.parse_args()

    router = AgentRouter()
    router.register_tool(
        intent=args.intent,
        tool_name=args.name,
        path=args.path,
        score=args.score,
        preferred_model=args.model
    )

    print(f"Successfully registered tool: {args.name}")
    print(f"Intent: {args.intent}")
    print(f"Model: {args.model or 'Default'}")
    print(f"WC Score: {args.score}")

if __name__ == "__main__":
    main()
