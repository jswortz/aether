import pytest
import os
import json
from core.router import AgentRouter

@pytest.fixture
def router(tmp_path):
    registry = tmp_path / "model_router_registry.json"
    return AgentRouter(registry_path=str(registry))

def test_model_skill_routing_default(router):
    router.register_tool("general task", "generic_tool", "/path/1", score=1.0)
    
    # Should default to gemini-2.0-flash
    results = router.route("perform a general task")
    assert results[0]["recommended_model"] == "gemini-2.0-flash"

def test_model_skill_routing_explicit_preference(router):
    router.register_tool("complex reasoning", "reasoner", "/path/2", score=1.0, preferred_model="claude-3-5-sonnet-v2")
    
    results = router.route("complex reasoning")
    assert results[0]["recommended_model"] == "claude-3-5-sonnet-v2"

def test_model_skill_routing_auto_upgrade(router):
    # Register with a default model
    router.register_tool("architectural review", "architect", "/path/3", score=1.0, preferred_model="gemini-2.0-flash")
    
    # Query with high-reasoning keyword 'architect' should trigger auto-upgrade
    results = router.route("perform an architectural review")
    assert results[0]["recommended_model"] == "claude-3-5-sonnet-v2"

def test_model_skill_routing_intent_ranking(router):
    router.register_tool("fix bugs", "fast_fixer", "/path/4", score=0.8, preferred_model="gemini-2.0-flash")
    router.register_tool("deep debug", "deep_fixer", "/path/5", score=1.0, preferred_model="claude-3-5-sonnet-v2")
    
    # 'debug' is a high-reasoning keyword, but deep_fixer has a better WC score and explicit claude preference
    results = router.route("deep debug")
    assert results[0]["tool_name"] == "deep_fixer"
    assert results[0]["recommended_model"] == "claude-3-5-sonnet-v2"
