# APIs/youtube/SimulationEngine/db.py
import json
import os

DB = {
    "activities": [],
    "captions": {},
    "channels": {},
    "channelSections": {},
    "channelStatistics": {
        "commentCount": 0,
        "hiddenSubscriberCount": False,
        "subscriberCount": 0,
        "videoCount": 0,
        "viewCount": 0,
    },
    "channelBanners": [],
    "comments": {},
    "commentThreads": {},
    "subscriptions": {},
    "videoCategories": {},
    "memberships": {},
    "videos": {},
}

# -------------------------------------------------------------------
# Persistence Helpers
# -------------------------------------------------------------------


def save_state(filepath: str) -> None:
    """Saves the in-memory DB to a file."""
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str) -> object:
    """Loads the DB from a file."""
    global DB
    with open(filepath, "r") as f:
        state = json.load(f)
    # Instead of reassigning DB, update it in place:
    DB.clear()
    DB.update(state)
