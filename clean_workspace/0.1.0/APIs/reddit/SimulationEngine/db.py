# gmail/SimulationEngine/db.py

import json
import os

DB = {
    # -----------------------------------
    # Resource-based keys:
    # -----------------------------------
    "accounts": {},  # e.g. {username: {...}}
    "announcements": [],  # list of announcement objects
    "captcha_needed": False,  # whether captcha is required
    "collections": {},  # {collection_id: {title, sr_fullname, links, etc.}}
    "emoji": {},  # {subreddit_name: {emoji_name: {...}}}
    "flair": {},  # storing flair settings, e.g. {subreddit: {...}}
    "links": {},  # link (post) data, keyed by fullname or ID
    "comments": {},  # comment data, keyed by fullname or ID
    "listings": {},  # any data relevant to listing endpoints
    "live_threads": {},  # {thread_id: {...}}
    "messages": {},  # {message_id: {...}}
    "misc_data": {},  # for /misc
    "moderation": {},  # storing mod data
    "modmail": {},  # modmail conversations
    "modnotes": {},  # {user: [notes]}
    "multis": {},  # {multi_path: {...}}
    "search_index": {},  # mocked data for search
    "subreddits": {},  # {subreddit_name: {...}}
    "users": {},  # storing user info (like profiles)
    "widgets": {},  # {subreddit: {widget_id: {...}}}
    "wiki": {},  # {subreddit: {page_name: {...}}}
    # -----------------------------------
}

###############################################################################
# HELPER FUNCTIONS FOR PERSISTENCE
###############################################################################
# def save_state(filepath: str) -> None:
#     """
#     Save the current DB state to a JSON file at `filepath`.
#     """
#     with open(filepath, 'w', encoding='utf-8') as f:
#         json.dump(DB, f, indent=2)


# def load_state(filepath: str) -> None:
#     """
#     Load the DB state from a JSON file at `filepath`.
#     Overwrites the current in-memory DB with the loaded content.
#     """
#     global DB
#     if not os.path.isfile(filepath):
#         return
#     with open(filepath, 'r', encoding='utf-8') as f:
#         loaded = json.load(f)
#     DB = loaded


def save_state(filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str) -> None:
    global DB
    with open(filepath, "r") as f:
        state = json.load(f)
    # Instead of reassigning DB, update it in place:
    DB.clear()
    DB.update(state)
    

