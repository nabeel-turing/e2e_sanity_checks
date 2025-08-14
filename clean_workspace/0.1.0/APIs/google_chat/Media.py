from common_utils.print_log import print_log
# APIs/google_chat/Media.py

from typing import Any, Dict
from .SimulationEngine.db import DB


def download(resourceName: str) -> None:
    """
    Downloads media using the specified resource name.

    Args:
        resourceName (str): Name of the media to download.
            See ReadRequest.resource_name.
    """
    print_log(f"Downloading media with resource name: {resourceName}")


def upload(parent: str, attachment_request: dict) -> Dict[str, Any]:
    """
    Uploads an attachment to the specified Chat space.

    Args:
        parent (str): Required. Resource name of the Chat space in which the attachment is uploaded. Format "spaces/{space}".
        attachment_request (dict): Dictionary with keys:
            - filename (str): Filename of the uploaded attachment.

    Returns:
        Dict[str, Any]: A dictionary containing references to the uploaded attachment.
            - resourceName (str): Optional. Resource name used with the media API to download the attachment.
            - attachmentUploadToken (str): Optional. Opaque token used to attach the uploaded file to a message.
    """
    # Generate a new attachment ID based on the current count in DB["Attachment"]
    new_id = str(len(DB.get("Attachment", [])) + 1)
    resource_name = f"{parent}/attachments/{new_id}"

    # Build the new attachment object based on the schema.
    attachment = {
        "name": resource_name,
        "contentName": attachment_request.get("contentName", "unknown"),
        "contentType": attachment_request.get(
            "contentType", "application/octet-stream"
        ),
        "attachmentDataRef": {},
        "driveDataRef": {},
        "thumbnailUri": "",
        "downloadUri": "",
        "source": "UPLOADED_CONTENT",
    }

    # Ensure DB["Attachment"] exists.
    if "Attachment" not in DB:
        DB["Attachment"] = []
    DB["Attachment"].append(attachment)
    print_log(f"Uploaded attachment: {resource_name}")
    return attachment
