from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List, Union


"""
    Handles YouTube Caption API operations.
    
    This class provides methods to manage video captions, including uploading,
    downloading, updating, and deleting caption tracks.
"""


def delete(
    id: str,
    onBehalfOf: Optional[str] = None,
    onBehalfOfContentOwner: Optional[str] = None,
) -> Dict[str, bool]:
    """
    Deletes a caption.

    Args:
        id (str): The id parameter identifies the caption track that is being deleted.
        onBehalfOf (Optional[str]): The onBehalfOf parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the onBehalfOfContentOwner parameter. (Currently not used in implementation)
        onBehalfOfContentOwner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value. (Currently not used in implementation)

    Returns:
        Dict[str, bool]: A dictionary containing:
            - success (bool): True if deletion is successful

    Raises:
        ValueError: If the caption ID does not exist in the database.
    """
    if id not in DB["captions"]:
        raise ValueError("Caption not found")

    del DB["captions"][id]
    return {"success": True}


def download(
    id: str,
    onBehalfOf: Optional[str] = None,
    onBehalfOfContentOwner: Optional[str] = None,
    tfmt: Optional[str] = None,
    tlang: Optional[str] = None,
) -> str:
    """
    Downloads a caption track.

    Args:
        id (str): The ID of the caption to be downloaded.
        onBehalfOf (Optional[str]): CMS user making the request on behalf of the content owner. (Currently not used in implementation)
        onBehalfOfContentOwner (Optional[str]): Content owner the user is acting on behalf of. (Currently not used in implementation)
        tfmt (Optional[str]): Desired format of the caption file ('srt', 'vtt', 'sbv').
        tlang (Optional[str]): Target language for translation (simulated).

    Returns:
        str: Caption content or simulated translation.

    Raises:
        ValueError: If caption is not found or format is unsupported.
    """
    if id not in DB.get("captions", {}):
        raise ValueError("Caption not found")

    caption = DB["captions"][id]

    format_mapping = {
        "srt": "Simulated SRT content",
        "vtt": "Simulated VTT content",
        "sbv": "Simulated SBV content",
    }

    if tfmt in format_mapping:
        return format_mapping[tfmt]
    elif tfmt:
        raise ValueError("Unsupported format")

    if tlang:
        return f"Simulated translated caption to {tlang}"

    return caption.get("snippet", {}).get("text", "Caption content")


def insert(
    part: str,
    snippet: Dict[str, Any],
    onBehalfOf: Optional[str] = None,
    onBehalfOfContentOwner: Optional[str] = None,
    sync: bool = False,
) -> Dict[str, Union[bool, Dict, str]]:
    """
    Inserts a new caption.

    Args:
        part (str): The part parameter specifies the caption resource properties that the API response will include.
        snippet (Dict[str, Any]): The snippet object contains details about the caption track.
        onBehalfOf (Optional[str]): The onBehalfOf parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the onBehalfOfContentOwner parameter. (Currently not used in implementation)
        onBehalfOfContentOwner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value. (Currently not used in implementation)
        sync (bool): The sync parameter indicates whether the caption track should be synchronized with the video. (Currently not used in implementation)

    Returns:
        Dict[str, Union[bool, Dict, str]]: A dictionary containing:
            - If part is valid:
                - success (bool): True if caption was successfully inserted
                - caption (Dict): The created caption object containing:
                    - id (str): Generated unique caption ID
                    - snippet (Dict): The provided snippet object

    Raises:
        ValueError: If 'part' is not 'snippet'.

    """
    if part != "snippet":
        raise ValueError("Invalid part parameter")

    new_id = generate_entity_id("caption")
    new_caption = {"id": new_id, "snippet": snippet}
    DB["captions"][new_id] = new_caption
    return {"success": True, "caption": new_caption}


def list(
    part: str,
    videoId: str,
    id: Optional[str] = None,
    onBehalfOf: Optional[str] = None,
    onBehalfOfContentOwner: Optional[str] = None,
) -> Dict[str, List[Dict]]:
    """
    Retrieves a list of captions.

    Args:
        part (str): Must be 'id' or 'snippet'.
        videoId (str): ID of the video to retrieve captions for.
        id (Optional[str]): Specific caption ID to filter results.
        onBehalfOf (Optional[str]): CMS user making the request on behalf of the content owner. (Currently not used in implementation)
        onBehalfOfContentOwner (Optional[str]): Content owner the user is acting on behalf of. (Currently not used in implementation)

    Returns:
        Dict[str, List[Dict]]: A dictionary containing:
            - items (List[Dict]): A list of caption objects, each containing:
                - id (str): Caption ID
                - snippet (Dict): Caption metadata containing at least:
                    - videoId (str): The ID of the video the caption belongs to

    Raises:
        ValueError: If 'part' is not valid.

    """
    if part not in ["id", "snippet"]:
        raise ValueError("Invalid part parameter")

    captions = [
        cap
        for cap in DB["captions"].values()
        if cap.get("snippet", {}).get("videoId") == videoId
    ]
    if id:
        captions = [cap for cap in captions if cap["id"] == id]

    return {"items": captions}


def update(
    part: str,
    id: str,
    snippet: Optional[Dict[str, Any]] = None,
    onBehalfOf: Optional[str] = None,
    onBehalfOfContentOwner: Optional[str] = None,
    sync: Optional[bool] = None,
) -> Dict[str, Union[bool, str]]:
    """
    Updates a caption resource.

    Args:
        part (str): The part parameter specifies the caption resource properties that the API response will include.
        id (str): The id parameter identifies the caption track that is being updated.
        snippet (Optional[Dict[str, Any]]): The snippet object contains details about the caption track.
        onBehalfOf (Optional[str]): The onBehalfOf parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the onBehalfOfContentOwner parameter. (Currently not used in implementation)
        onBehalfOfContentOwner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value. (Currently not used in implementation)
        sync (Optional[bool]): The sync parameter indicates whether the caption track should be synchronized with the video. (Currently not used in implementation)

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing:
            - If caption exists and part is valid:
                - success (bool): True if caption was successfully updated
                - message (str): Confirmation message "Caption updated."
            - If caption not found:
                - error (str): "Caption not found"

    Raises:
        ValueError: If 'part' is not 'snippet'.
    """
    if part not in ["snippet"]:
        raise ValueError("Invalid 'part' parameter. Expected 'id' or 'snippet'.")

    if id not in DB["captions"]:
        return {"error": "Caption not found"}

    if snippet:
        DB["captions"][id]["snippet"] = snippet

    return {"success": True, "message": "Caption updated."}
