from common_utils.print_log import print_log
# APIs/google_chat/Spaces/Messages/Attachments.py

import sys
import os

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB


def get(name: str) -> dict:
    """
    Retrieves attachment metadata by its resource name.

    Args:
        name (str): Required. Resource name of the attachment.
            Format: "spaces/{space}/messages/{message}/attachments/{attachment}"

    Returns:
        dict: The attachment metadata if found, with fields:
            - name (str): Resource name of the attachment.
            - contentName (str): Original filename of the content.
            - contentType (str): MIME type of the file.
            - thumbnailUri (str): Thumbnail URL for preview.
            - downloadUri (str): Download URL for the file.
            - source (str): Enum - SOURCE_UNSPECIFIED, DRIVE_FILE, UPLOADED_CONTENT
            - attachmentDataRef (dict):
                - resourceName (str): Media API resource name for the data.
                - attachmentUploadToken (str): Opaque upload token.
            - driveDataRef (dict):
                - driveFileId (str): ID for the Drive file.

            Returns an empty dictionary if the attachment or parent message is not found.
    """
    print_log(f"Attachments.get called with name={name}")

    # 1) Extract the parent portion => "spaces/AAA/messages/123"
    parts = name.split("/")
    if (
        len(parts) < 5
        or parts[0] != "spaces"
        or parts[2] != "messages"
        or parts[4] != "attachments"
    ):
        print_log("Invalid attachment name format.")
        return {}

    # Rejoin the first 4 segments => "spaces/AAA/messages/123"
    parent_message_name = "/".join(parts[:4])  # e.g. "spaces/AAA/messages/123"
    attachment_id = parts[4]  # Should be "attachments", but we already check above
    # Actually the real attachment ID is parts[5], if it exists
    if len(parts) < 6:
        print_log("Attachment ID is missing.")
        return {}

    attachment_res_id = parts[5]  # e.g. "ATT1"

    # So the full name is "spaces/AAA/messages/123/attachments/ATT1"
    # But we already have that in 'name'. We'll just confirm if it matches.

    # 2) Find the message in DB
    found_message = None
    for msg in DB["Message"]:
        if msg.get("name") == parent_message_name:
            found_message = msg
            break

    if not found_message:
        print_log(f"Parent message not found: {parent_message_name}")
        return {}

    # 3) Search the message's "attachment" list for one with "name" == full 'name'
    for att in found_message.get("attachment", []):
        if att.get("name") == name:
            print_log(f"Found attachment => {att}")
            return att

    # Not found
    print_log(f"No attachment found with name={name}")
    return {}
