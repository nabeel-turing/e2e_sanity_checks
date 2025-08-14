# APIs/tiktokApi/Business/Publish/Status/__init__.py
import uuid


def get(access_token: str, business_id: str, publish_id: str) -> dict:
    """
    Get the publishing status of a TikTok video or photo post.

    This endpoint allows you to check the current status of a post publishing task,
    including whether it has completed successfully or is still in progress.

    Args:
        access_token (str): Access token authorized by TikTok creators.
        business_id (str): Application specific unique identifier for the TikTok account.
        publish_id (str): Unique identifier for a post publishing task.

    Returns:
        dict: A dictionary containing:
            - code (int): HTTP status code (200 for success, 400 for bad request)
            - message (str): Status message describing the result
            - request_id (str): Unique identifier for the request
            - data (dict): Publishing status information containing:
                - status (str): Current status of the publishing task (e.g., "PUBLISH_COMPLETE")
                - post_ids (list[str]): List of IDs for the published posts

    Raises:
        ValueError: If any of the required parameters (access_token, business_id, publish_id) are missing
    """
    if not access_token:
        return {"code": 400, "message": "Access-Token is required", "data": None}
    if not business_id:
        return {"code": 400, "message": "business_id is required", "data": None}
    if not publish_id:
        return {"code": 400, "message": "publish_id is required", "data": None}

    # Simulate publish status retrieval
    # For simplicity, let's assume all requests are successful.
    return {
        "code": 200,
        "message": "OK",
        "request_id": str(uuid.uuid4()),
        "data": {
            "status": "PUBLISH_COMPLETE",  #
            "post_ids": ["video_id_" + str(uuid.uuid4())],  #
        },
    }
