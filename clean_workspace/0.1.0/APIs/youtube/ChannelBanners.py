from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List

"""
    Handles YouTube Channel Banners API operations.
    
    This class provides methods to manage channel banner images,
    which are the large banner images that appear at the top of a YouTube channel page.
"""


def insert(
    channel_id: Optional[str] = None,
    on_behalf_of_content_owner: Optional[str] = None,
    on_behalf_of_content_owner_channel: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """
    Inserts a new channel banner.

    Args:
        channel_id(Optional[str]): The ID of the channel for which to insert a banner.
        on_behalf_of_content_owner(Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value.
        on_behalf_of_content_owner_channel(Optional[str]): The onBehalfOfContentOwnerChannel parameter specifies the YouTube channel ID of the channel to which the user is being added.

    Returns:
        Dict[str, Optional[str]]:
            A dictionary containing the newly created banner resource.
            - channelId (Optional[str]): The ID of the channel for which to insert a banner.
            - onBehalfOfContentOwner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value.
            - onBehalfOfContentOwnerChannel (Optional[str]): The onBehalfOfContentOwnerChannel parameter specifies the YouTube channel ID of the channel to which the user is being added.
    """
    new_banner = {
        "channelId": channel_id,
        "onBehalfOfContentOwner": on_behalf_of_content_owner,
        "onBehalfOfContentOwnerChannel": on_behalf_of_content_owner_channel,
    }
    DB.setdefault("channelBanners", []).append(new_banner)
    return new_banner
