import json
import logging
from typing import Dict, Any, List, Optional
from core.gas_town_engine import GasTownEngine

class SpyGameState:
    _session_cache = {}

    def __init__(self, session_id: str, state_bucket: str = "aether-spy-game-state"):
        self.engine = GasTownEngine(state_bucket=state_bucket, session_id=session_id)
        self.session_id = session_id
        
        # Try to resurrect from GCS
        resurrected = self.engine.resurrect()
        
        if not resurrected:
            if session_id in SpyGameState._session_cache:
                # Use in-memory cache if GCS failed but we have it locally
                self.engine.state = SpyGameState._session_cache[session_id]
                logging.info(f"Resumed session {session_id} from in-memory cache.")
            else:
                # Initialize default game state
                self.engine.state.update({
                    "players": {},
                    "mission_status": "not_started",
                    "secrets_found": [],
                    "agent_interactions": [],
                    "current_clues": ["The shadow falls at midnight.", "The raven flies west."],
                    "mole_identity": "Agent X",
                    "gatekeeper_status": "locked"
                })
                self.engine.checkpoint()
        
        # Always update cache
        SpyGameState._session_cache[session_id] = self.engine.state

    def get_state(self) -> Dict[str, Any]:
        return self.engine.state

    def update_state(self, updates: Dict[str, Any]):
        self.engine.state.update(updates)
        SpyGameState._session_cache[self.session_id] = self.engine.state
        self.engine.checkpoint()

    def add_interaction(self, agent: str, player: str, message: str, response: str):
        self.engine.state["agent_interactions"].append({
            "agent": agent,
            "player": player,
            "message": message,
            "response": response
        })
        SpyGameState._session_cache[self.session_id] = self.engine.state
        self.engine.checkpoint()
