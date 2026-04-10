import requests
import sys
import argparse

BASE_URL = "http://localhost:8000"

def start_session():
    resp = requests.post(f"{BASE_URL}/session")
    resp.raise_for_status()
    return resp.json()["session_id"]

def send_action(session_id, player_id, agent, message):
    payload = {
        "session_id": session_id,
        "player_id": player_id,
        "target_agent": agent,
        "message": message
    }
    resp = requests.post(f"{BASE_URL}/action", json=payload)
    resp.raise_for_status()
    return resp.json()["response"]

def get_state(session_id):
    resp = requests.get(f"{BASE_URL}/state/{session_id}")
    resp.raise_for_status()
    return resp.json()

def main():
    parser = argparse.ArgumentParser(description="Aether Spy Game CLI")
    parser.add_index = False # Not a real arg, just for clarity
    
    print("--- Welcome to Aether Spy Game ---")
    player_id = input("Enter your Agent Name: ")
    
    session_id = start_session()
    print(f"Session started: {session_id}")
    
    while True:
        print("\nAvailable Agents: mole, gatekeeper, decoy")
        agent = input("Which agent do you want to talk to? (or 'quit'): ").lower()
        if agent == 'quit':
            break
        
        if agent not in ['mole', 'gatekeeper', 'decoy']:
            print("Invalid agent.")
            continue
            
        message = input(f"Your message to {agent}: ")
        response = send_action(session_id, player_id, agent, message)
        print(f"\n{response}")
        
        state = get_state(session_id)
        if state.get("mission_status") == "mole_identified":
            print("\n*** MISSION ACCOMPLISHED! You identified the Mole! ***")
            break

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Is it running?")
    except KeyboardInterrupt:
        print("\nGoodbye, Agent.")
