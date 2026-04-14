from core.router import AgentRouter

def configure_game_router():
    router = AgentRouter()
    
    # Register 'deception' intent to prefer Claude-3-5-Sonnet-v2
    router.register_tool(
        intent="deception",
        tool_name="spy_deception_engine",
        path="/dev/null",
        score=1.0,
        preferred_model="claude-3-5-sonnet-v2",
        metadata={"domain": "spy_game", "specialty": "creative lying"}
    )
    
    # Register 'fact checking' intent to prefer Gemini-3-Flash-Preview
    router.register_tool(
        intent="fact checking",
        tool_name="spy_fact_checker",
        path="/dev/null",
        score=1.0,
        preferred_model="gemini-3-flash-preview",
        metadata={"domain": "spy_game", "specialty": "strict validation"}
    )

if __name__ == "__main__":
    configure_game_router()
    print("Router configured for Spy Game.")
