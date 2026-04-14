from core.router import AgentRouter
from typing import Dict, Any

class SpyAgent:
    def __init__(self, name: str, role: str, intent: str):
        self.name = name
        self.role = role
        self.intent = intent
        self.router = AgentRouter()

    def get_model(self) -> str:
        # Route based on intent to get recommended model
        results = self.router.route(self.intent)
        if results:
            return results[0]["recommended_model"]
        return "gemini-3-flash-preview" # Fallback

    def interact(self, message: str, game_state: Dict[str, Any]) -> str:
        model = self.get_model()
        # In a real scenario, this would call the actual LLM with the recommended model.
        # For this engine, we'll simulate the response based on the agent's role.
        return f"[{self.name} ({model})]: Simulating response for '{message}' as a {self.role}."

class Mole(SpyAgent):
    def __init__(self):
        super().__init__("Mole", "Infiltrator", "deception")
    
    def interact(self, message: str, game_state: Dict[str, Any]) -> str:
        model = self.get_model()
        # Mole tries to lead you away from the truth or give half-truths.
        return f"[{self.name} ({model})]: I've heard rumors about {game_state.get('mole_identity', 'someone')}, but they are just that... rumors. Why don't you look into the 'Raven' instead?"

class Gatekeeper(SpyAgent):
    def __init__(self):
        super().__init__("Gatekeeper", "Guardian", "fact checking")

    def interact(self, message: str, game_state: Dict[str, Any]) -> str:
        model = self.get_model()
        # Gatekeeper checks if what you say is true and unlocks things.
        if "Agent X" in message:
            return f"[{self.name} ({model})]: You have identified the Mole. The gate is now open."
        return f"[{self.name} ({model})]: Access denied. Your information is incorrect."

class Decoy(SpyAgent):
    def __init__(self):
        super().__init__("Decoy", "Distraction", "deception")

    def interact(self, message: str, game_state: Dict[str, Any]) -> str:
        model = self.get_model()
        # Decoy just says random confusing things.
        return f"[{self.name} ({model})]: The moon is made of green cheese, and the secret is hidden in the fridge!"
