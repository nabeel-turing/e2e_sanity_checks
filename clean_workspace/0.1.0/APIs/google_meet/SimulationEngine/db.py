import json
import os


"""
Database structure for the Meet API simulation.
"""

# In-Memory Database Structure for Conference Records and Related Data
# This database stores conference records, recordings, transcripts, entries, participants, and participant sessions.

DB = {
    "conferenceRecords": {},
    "recordings": {},
    "transcripts": {},
    "entries": {},
    "participants": {},
    "participantSessions": {},
    "spaces": {} 
} 


def save_state(filepath: str) -> None:
    """
    Saves the current state of the in-memory database to a JSON file.

    Args:
        filepath (str): The path to the JSON file where the state should be saved.
    """
    with open(filepath, 'w') as f:
        json.dump(DB, f, indent=4)

def load_state(filepath: str) -> None:
    """
    Loads the state of the in-memory database from a JSON file.

    Args:
        filepath (str): The path to the JSON file from which the state should be loaded.
    """
    global DB
    try:
        with open(filepath, 'r') as f:
            DB.update(json.load(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"State file {filepath} not found. Starting with default state.")