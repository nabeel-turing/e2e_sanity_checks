from common_utils.print_log import print_log
# APIs/google_chat/SimulationEngine/db.py

import json
import os

DB = {
    "media": [{"resourceName": ""}],
    "User": [
        {
            "name": "",
            "displayName": "",
            "domainId": "",
            "type": "",
            "isAnonymous": False,
        }
    ],
    "Space": [
        {
            "name": "",
            "type": "",
            "spaceType": "",
            "singleUserBotDm": False,
            "threaded": False,
            "displayName": "",
            "externalUserAllowed": True,
            "spaceThreadingState": "",
            "spaceDetails": {"description": "", "guidelines": ""},
            "spaceHistoryState": "",
            "importMode": False,
            "createTime": "",
            "lastActiveTime": "",
            "adminInstalled": False,
            "membershipCount": {"joinedDirectHumanUserCount": 0, "joinedGroupCount": 0},
            "accessSettings": {"accessState": "", "audience": ""},
            "spaceUri": "",
            "predefinedPermissionSettings": "",
            "permissionSettings": {
                "manageMembersAndGroups": {},
                "modifySpaceDetails": {},
                "toggleHistory": {},
                "useAtMentionAll": {},
                "manageApps": {},
                "manageWebhooks": {},
                "postMessages": {},
                "replyMessages": {},
            },
            "importModeExpireTime": "",
        }
    ],
    "Message": [
        {
            "name": "",
            "sender": {
                "name": "",
                "displayName": "",
                "domainId": "",
                "type": "",
                "isAnonymous": False,
            },
            "createTime": "",
            "lastUpdateTime": "",
            "deleteTime": "",
            "text": "",
            "formattedText": "",
            "cards": [],
            "cardsV2": [],
            "annotations": [],
            "thread": {"name": "", "threadKey": ""},
            "space": {"name": "", "type": "", "spaceType": ""},
            "fallbackText": "",
            "actionResponse": {},
            "argumentText": "",
            "slashCommand": {},
            "attachment": [
                {
                    "name": "",
                    "contentName": "",
                    "contentType": "",
                    "attachmentDataRef": {},
                    "driveDataRef": {},
                    "thumbnailUri": "",
                    "downloadUri": "",
                    "source": "",
                }
            ],
            "matchedUrl": {},
            "threadReply": False,
            "clientAssignedMessageId": "",
            "emojiReactionSummaries": [],
            "privateMessageViewer": {
                "name": "",
                "displayName": "",
                "domainId": "",
                "type": "",
                "isAnonymous": False,
            },
            "deletionMetadata": {},
            "quotedMessageMetadata": {},
            "attachedGifs": [],
            "accessoryWidgets": [],
        }
    ],
    "Membership": [
        {
            "name": "",
            "state": "",
            "role": "",
            "member": {
                "name": "",
                "displayName": "",
                "domainId": "",
                "type": "",
                "isAnonymous": False,
            },
            "groupMember": {},
            "createTime": "",
            "deleteTime": "",
        }
    ],
    "Reaction": [
        {
            "name": "",
            "user": {
                "name": "",
                "displayName": "",
                "domainId": "",
                "type": "",
                "isAnonymous": False,
            },
            "emoji": {"unicode": ""},
        }
    ],
    "SpaceNotificationSetting": [
        {"name": "", "notificationSetting": "", "muteSetting": ""}
    ],
    "SpaceReadState": [{"name": "", "lastReadTime": ""}],
    "ThreadReadState": [{"name": "", "lastReadTime": ""}],
    "SpaceEvent": [
        {
            "name": "",
            "eventTime": "",
            "eventType": "",
            "messageCreatedEventData": {},
            "messageUpdatedEventData": {},
            "messageDeletedEventData": {},
            "messageBatchCreatedEventData": {},
            "messageBatchUpdatedEventData": {},
            "messageBatchDeletedEventData": {},
            "spaceUpdatedEventData": {},
            "spaceBatchUpdatedEventData": {},
            "membershipCreatedEventData": {},
            "membershipUpdatedEventData": {},
            "membershipDeletedEventData": {},
            "membershipBatchCreatedEventData": {},
            "membershipBatchUpdatedEventData": {},
            "membershipBatchDeletedEventData": {},
            "reactionCreatedEventData": {},
            "reactionDeletedEventData": {},
            "reactionBatchCreatedEventData": {},
            "reactionBatchDeletedEventData": {},
        }
    ],
    "Attachment": [
        {
            "name": "",
            "contentName": "",
            "contentType": "",
            "attachmentDataRef": {},
            "driveDataRef": {},
            "thumbnailUri": "",
            "downloadUri": "",
            "source": "",
        }
    ],
}


def save_state(filepath: str) -> None:
    """Saves the current in-memory DB state to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(DB, f, indent=2)
    print_log(f"State saved to {filepath}")


def load_state(filepath: str) -> None:
    """Loads the in-memory DB state from a JSON file."""
    with open(filepath, "r") as f:
        new_data = json.load(f)
    DB.clear()
    DB.update(new_data)
    print_log(f"State loaded from {filepath}")

CURRENT_USER_ID = {"id": "users/USER123"}
