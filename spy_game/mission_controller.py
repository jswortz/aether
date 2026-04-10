from spy_game.state import SpyGameState
from spy_game.agents import Mole, Gatekeeper, Decoy
from typing import Dict, Any

class MissionController:
    """
    The Mission Controller (Supervisor) orchestrates the Spy Swarm.
    It follows the SCION pattern by delegating tasks to specialized workers.
    """
    def __init__(self, session_id: str):
        self.state_manager = SpyGameState(session_id)
        self.workers = {
            "mole": Mole(),
            "gatekeeper": Gatekeeper(),
            "decoy": Decoy()
        }

    def process_player_action(self, player_id: str, target_agent: str, message: str) -> str:
        game_state = self.state_manager.get_state()
        
        if target_agent not in self.workers:
            return f"System Error: Unknown agent '{target_agent}'. Available agents: {', '.join(self.workers.keys())}"

        worker = self.workers[target_agent]
        
        # Delegation step (SCION pattern)
        response = worker.interact(message, game_state)
        
        # Update global state via Gas Town persistence
        self.state_manager.add_interaction(target_agent, player_id, message, response)
        
        # Check for state changes based on interaction
        if target_agent == "gatekeeper" and "gate is now open" in response:
            self.state_manager.update_state({"gatekeeper_status": "unlocked", "mission_status": "mole_identified"})
            
        return response

    def get_summary(self) -> Dict[str, Any]:
        return self.state_manager.get_state()
