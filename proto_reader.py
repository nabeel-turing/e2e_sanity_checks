#!/usr/bin/env python3
"""
Proto Reader Script

This script helps read proto files and convert them to JSON format.
Based on the proto parsing logic from runner.py.
"""

import json
import os
import sys
from typing import Dict, List, Any
from google.protobuf import json_format

# CONFIGURATION - Update this path to your .pb file
PROTO_FILE_PATH = "proto_files/tool_use_metadata_set_v2.pb"

try:
    import tool_use_task_metadata_v2_pb2 as pb
except ImportError:
    print("Warning: Could not import proto module. Make sure proto_files is in your Python path.")
    print("You may need to add the proto_files directory to your PYTHONPATH.")
    sys.exit(1)


def parse_proto_file(proto_file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a proto file and return the tasks as JSON.

    Args:
        proto_file_path: Path to the .pb file

    Returns:
        List of task dictionaries
    """
    if not os.path.exists(proto_file_path):
        raise FileNotFoundError(f"Proto file not found: {proto_file_path}")

    with open(proto_file_path, "rb") as f:
        proto_bytes = f.read()

    proto_content = pb.ToolUseMetadataSet()
    proto_content.ParseFromString(proto_bytes)

    json_data = json.loads(json_format.MessageToJson(proto_content, preserving_proto_field_name=True))

    return json_data.get('tasks', [])


def main():
    try:
        print(f"Parsing proto file: {PROTO_FILE_PATH}")
        samples = parse_proto_file(PROTO_FILE_PATH)
        with open('proto_data/pb_jsons.json', 'w') as f:
            json.dump({'result': samples}, f, indent=4)        
        # print(f"Found {len(samples)} samples")

        # print(f"\n{'='*60}")
        # print("SAMPLE SUMMARY")
        # print(f"{'='*60}")
        # for i, sample in enumerate(samples[:10]):
        #     colab_id = sample.get('colab_id', 'N/A')
        #     task_category = sample.get('task_properties', {}).get('task_category', 'N/A')
        #     print(f"Sample {i}: {colab_id} ({task_category})")

        # if len(samples) > 10:
        #     print(f"... and {len(samples) - 10} more samples")

        # print(f"\nAll {len(samples)} samples are now available in memory as JSON objects.")
        # print("You can access them programmatically or use the 'samples' variable.")

        # if samples:
        #     print(f"\n{'='*60}")
        #     print("FIRST SAMPLE STRUCTURE")
        #     print(f"{'='*60}")
        #     first_sample = samples[0]
        #     print(f"Keys in first sample: {list(first_sample.keys())}")

        #     print(f"\nColab ID: {first_sample.get('colab_id', 'N/A')}")
        #     print(f"Task Category: {first_sample.get('task_properties', {}).get('task_category', 'N/A')}")

        #     user_query = first_sample.get('user_simulation_metadata', {}).get('initial_query', 'N/A')
        #     print(f"User Query Preview: {user_query[:100]}{'...' if len(user_query) > 100 else ''}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# if __name__ == "__main__":
#     main()
