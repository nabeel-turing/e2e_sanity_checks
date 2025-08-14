# APIs/hubspot/SimulationEngine/utils.py
import hashlib
import random


def generate_hubspot_object_id(source=None):
    if source:
        # Create a consistent 9-digit ID using a hash of the source
        hash_value = int(hashlib.md5(source.encode()).hexdigest(), 16)
        object_id = (hash_value % 900000000) + 100000000  # Ensures exactly 9 digits
    else:
        # Generate a completely random 9-digit ID
        object_id = random.randint(100000000, 999999999)

    return object_id
