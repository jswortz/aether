import pytest
import os
import json
from core.router import AgentRouter
from toolsmith_mcp_server import surprise_gate

# Mocking Pydantic model for surprise_gate test
class MockParams:
    def __init__(self, content):
        self.content = content

@pytest.fixture
def router(tmp_path):
    registry = tmp_path / "test_registry.json"
    return AgentRouter(registry_path=str(registry))

def test_router_registration(router):
    router.register_tool("test intent", "test_tool", "/path/to/tool", score=0.8)
    caps = router.list_capabilities()
    assert len(caps) == 1
    assert caps[0]["tool_name"] == "test_tool"
    assert caps[0]["wc_score"] == 0.8

def test_router_routing_logic(router):
    router.register_tool("fix python bugs", "bug_fixer", "/path/fix", score=1.0)
    router.register_tool("write documentation", "doc_writer", "/path/doc", score=0.5)
    
    # Precise match
    results = router.route("I need to fix python bugs")
    assert results[0]["tool_name"] == "bug_fixer"
    
    # Partial match
    results = router.route("write some stuff")
    assert results[0]["tool_name"] == "doc_writer"

@pytest.mark.asyncio
async def test_surprise_gate_filtering():
    # Mocking a function to decorate
    async def mock_func(params):
        return "Success"
    
    decorated = surprise_gate(mock_func)
    
    # Test rejection (low signal)
    rejected_params = MockParams("i think maybe it is working")
    result = await decorated(params=rejected_params)
    assert "rejected" in result
    
    # Test rejection (conflict)
    conflict_params = MockParams("this content is incorrect and contradicts reality")
    result = await decorated(params=conflict_params)
    assert "Adversarial Buffer" in result
    
    # Test acceptance
    accepted_params = MockParams("High signal mission critical data points.")
    result = await decorated(params=accepted_params)
    assert result == "Success"
