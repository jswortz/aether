import pytest
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from anthropic import AnthropicVertex

# Configuration - update with your actual project/location if needed
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id") 
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

@pytest.mark.skipif(os.getenv("GOOGLE_CLOUD_PROJECT") is None, reason="GCP Project not configured")
def test_gemini_connectivity():
    """Verify Gemini (Vertex AI) connectivity and basic generation."""
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content("Say 'Gemini Online'")
    assert response.text is not None
    assert "Gemini" in response.text

@pytest.mark.skipif(os.getenv("GOOGLE_CLOUD_PROJECT") is None, reason="GCP Project not configured")
def test_claude_connectivity():
    """Verify Claude (Vertex AI) connectivity and basic generation."""
    client = AnthropicVertex(project_id=PROJECT_ID, region=LOCATION)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=10,
        messages=[
            {"role": "user", "content": "Say 'Claude Online'"}
        ]
    )
    assert message.content[0].text is not None
    assert "Claude" in message.content[0].text
