# APIs/hubspot/MarketingEvents.py
from typing import Optional, Dict, Any, List
import uuid
from hubspot.SimulationEngine.db import DB
import hashlib
import datetime


def get_events(
    occurredAfter: Optional[str] = None,
    occurredBefore: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> Dict[str, Any]:
    """Get all marketing events.

    Args:
        occurredAfter (Optional[str]): Filter events that occurred after this timestamp.
        occurredBefore (Optional[str]): Filter events that occurred before this timestamp.
        limit (Optional[int]): Maximum number of events to return.
        after (Optional[str]): Cursor for pagination.

    Returns:
        Dict[str, Any]: A dictionary containing a list of marketing events under the 'results' key.
            The results list contains dictionaries with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (List[Dict[str, Any]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    return {"results": list(DB["marketing_events"].values())}


def create_event(
    externalEventId: str,
    externalAccountId: str,
    event_name: str,
    event_type: str,
    event_organizer: str,
    start_date_time: Optional[str] = None,
    end_date_time: Optional[str] = None,
    event_description: Optional[str] = None,
    event_url: Optional[str] = None,
    custom_properties: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Create a marketing event.
    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        externalAccountId (str): The unique identifier for the account(external system) where the event was created.
        event_name (str): The name of the marketing event.
        event_type (str): The type of the marketing event.
        event_organizer (str): The organizer of the marketing event.
        start_date_time (Optional[str]): The start date and time of the marketing event.
        end_date_time (Optional[str]): The end date and time of the marketing event.
        event_description (Optional[str]): A description of the marketing event.
        event_url (Optional[str]): A URL for more information about the marketing event.
        custom_properties (Optional[List[Dict]]): Custom properties associated with the marketing event.
            Each property is a dictionary with the following structure:
            - sourceId (str): Source identifier.
            - selectedByUser (bool): Whether the property was selected by the user.
            - sourceLabel (str): Label of the source.
            - source (str): Source of the property.
            - updatedByUserId (int): ID of the user who last updated the property.
            - persistenceTimestamp (int): Timestamp for persistence.
            - sourceMetadata (str): Source metadata encoded as a base64 string.
            - dataSensitivity (str): Data sensitivity level.
            - unit (str): Unit of measurement.
            - requestId (str): Request identifier.
            - isEncrypted (bool): Whether the value is encrypted.
            - name (str): Property name.
            - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
            - value (str): Property value.
            - selectedByUserTimestamp (int): Timestamp when selected by user.
            - timestamp (int): Property timestamp.
            - isLargeValue (bool): Whether the value is large.

    Returns:
        Dict[str, Any]: A dictionary representing the created marketing event with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (List[Dict[str, Any]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    event_id = externalEventId

    if not externalEventId:
        return {"error": "External Event ID is required."}
    if not externalAccountId:
        return {"error": "External Account ID is required."}

    event = {
        "externalEventId": externalEventId,
        "eventName": event_name,
        "eventType": event_type,
        "eventOrganizer": event_organizer,
        "startDateTime": start_date_time,
        "endDateTime": end_date_time,
        "eventDescription": event_description,
        "eventUrl": event_url,
        "customProperties": custom_properties,
        "externalAccountId": externalAccountId,
    }
    DB["marketing_events"][event_id] = event
    return event


def get_event(externalEventId: str, externalAccountId: str) -> Dict[str, Any]:
    """Get a marketing event by its external ID.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        externalAccountId (str): The unique identifier for the account where the event was created.

    Returns:
        Dict[str, Any]: A dictionary representing the marketing event with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (List[Dict[str, Any]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    if not externalEventId:
        return {"error": "External Event ID is required."}
    if not externalAccountId:
        return {"error": "External Account ID is required."}

    if (
        externalEventId in DB["marketing_events"]
        and DB["marketing_events"][externalEventId]["externalAccountId"]
        == externalAccountId
    ):
        return DB["marketing_events"][externalEventId]
    return {}


def delete_event(externalEventId: str, externalAccountId: str) -> None:
    """Delete a marketing event.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        externalAccountId (str): The unique identifier for the account where the event was created.

    Returns:
        None
    """
    if not externalEventId:
        return {"error": "External Event ID is required."}
    if not externalAccountId:
        return {"error": "External Account ID is required."}
    if (
        externalEventId in DB["marketing_events"]
        and DB["marketing_events"][externalEventId]["externalAccountId"]
        == externalAccountId
    ):
        del DB["marketing_events"][externalEventId]


def update_event(
    externalEventId: str,
    externalAccountId: str,
    event_name: Optional[str] = None,
    event_type: Optional[str] = None,
    start_date_time: Optional[str] = None,
    end_date_time: Optional[str] = None,
    event_organizer: Optional[str] = None,
    event_description: Optional[str] = None,
    event_url: Optional[str] = None,
    custom_properties: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Update a marketing event.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        externalAccountId (str): The unique identifier for the account where the event was created.
        event_name (Optional[str]): The name of the marketing event.
        event_type (Optional[str]): The type of the marketing event.
        start_date_time (Optional[str]): The start date and time of the marketing event.
        end_date_time (Optional[str]): The end date and time of the marketing event.
        event_organizer (Optional[str]): The organizer of the marketing event.
        event_description (Optional[str]): A description of the marketing event.
        event_url (Optional[str]): A URL for more information about the marketing event.
        custom_properties (Optional[List[Dict]]): Custom properties associated with the marketing event.
            Each property is a dictionary with the following structure:
            - sourceId (str): Source identifier.
            - selectedByUser (bool): Whether the property was selected by the user.
            - sourceLabel (str): Label of the source.
            - source (str): Source of the property.
            - updatedByUserId (int): ID of the user who last updated the property.
            - persistenceTimestamp (int): Timestamp for persistence.
            - sourceMetadata (str): Source metadata encoded as a base64 string.
            - dataSensitivity (str): Data sensitivity level.
            - unit (str): Unit of measurement.
            - requestId (str): Request identifier.
            - isEncrypted (bool): Whether the value is encrypted.
            - name (str): Property name.
            - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
            - value (str): Property value.
            - selectedByUserTimestamp (int): Timestamp when selected by user.
            - timestamp (int): Property timestamp.
            - isLargeValue (bool): Whether the value is large.

    Returns:
        Dict[str, Any]: A dictionary representing the updated marketing event with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (List[Dict[str, Any]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    if not externalEventId:
        return {"error": "External Event ID is required."}
    if not externalAccountId:
        return {"error": "External Account ID is required."}

    if (
        externalEventId in DB["marketing_events"]
        and DB["marketing_events"][externalEventId]["externalAccountId"]
        == externalAccountId
    ):
        event = DB["marketing_events"][externalEventId]
        if event_name:
            event["eventName"] = event_name
        if event_type:
            event["eventType"] = event_type
        if start_date_time:
            event["startDateTime"] = start_date_time
        if end_date_time:
            event["endDateTime"] = end_date_time
        if event_organizer:
            event["eventOrganizer"] = event_organizer
        if event_description:
            event["eventDescription"] = event_description
        if event_url:
            event["eventUrl"] = event_url
        if custom_properties:
            event["customProperties"] = custom_properties

        DB["marketing_events"][externalEventId] = event
        return event
    return {}


def cancel_event(externalEventId: str, externalAccountId: str) -> Dict[str, Any]:
    """Marks an event as cancelled.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        externalAccountId (str): The unique identifier for the account where the event was created.

    Returns:
        Dict[str, Any]: A dictionary representing the cancelled marketing event with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (List[Dict[str, Any]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    if not externalEventId:
        return {"error": "External Event ID is required."}
    if not externalAccountId:
        return {"error": "External Account ID is required."}

    if (
        externalEventId in DB["marketing_events"]
        and DB["marketing_events"][externalEventId]["externalAccountId"]
        == externalAccountId
    ):
        DB["marketing_events"][externalEventId]["eventStatus"] = "CANCELED"
        return DB["marketing_events"][externalEventId]
    return {}


def create_or_update_attendee(
    externalEventId: str, externalAccountId: str, email: str, joinedAt: str, leftAt: str
) -> Dict[str, Any]:
    """Create or update an attendee for a marketing event.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        externalAccountId (str): The unique identifier for the account where the event was created.
        email (str): The email address of the attendee.
        joinedAt (str): The date and time when the attendee joined the event.
        leftAt (str): The date and time when the attendee left the event.

    Returns:
        Dict[str, Any]: A dictionary representing the attendee with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (List[Dict[str, Any]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    if not all([externalEventId, externalAccountId, email, joinedAt, leftAt]):
        return {"error": "Missing required parameters."}

    if not externalEventId in DB["marketing_events"]:
        return {"error": "Event not found."}

    if (
        externalEventId not in DB["marketing_events"]
        or DB["marketing_events"][externalEventId]["externalAccountId"]
        != externalAccountId
    ):
        return {}

    if not "attendees" in DB["marketing_events"][externalEventId]:
        DB["marketing_events"][externalEventId]["attendees"] = {}

    for attendee in DB["marketing_events"][externalEventId]["attendees"].values():
        if attendee["email"] == email:
            attendee["joinedAt"] = joinedAt
            attendee["leftAt"] = leftAt
            return attendee

    attendee_id = hashlib.sha256(f"{externalEventId}-{email}".encode()).hexdigest()[:8]
    attendee = {
        "attendeeId": attendee_id,
        "email": email,
        "eventId": externalEventId,
        "externalAccountId": externalAccountId,
    }

    DB["marketing_events"][externalEventId]["attendees"][attendee_id] = attendee
    return attendee


def get_attendees(
    externalEventId: str, limit: int = 10, after: Optional[str] = None
) -> Dict[str, Any]:
    """Get attendees of a marketing event.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        limit (int): The maximum number of attendees to return. Default to 10. The Maximum is 100.
        after (Optional[str]): A cursor for pagination.

    Returns:
        Dict[str, Any]: A dictionary containing a list of attendees under the 'results' key.
            Each attendee is a dictionary with the following structure:
            - registrants (int): The number of HubSpot contacts that registered for this marketing event.
            - eventOrganizer (str): The name of the organizer of the marketing event.
            - eventUrl (str): A URL in the external event application where the marketing event can be managed.
            - attendees (int): The number of HubSpot contacts that attended this marketing event.
            - eventType (str): The type of the marketing event.
            - eventCompleted (bool): Whether the event is completed.
            - endDateTime (str): The end date and time of the marketing event.
            - noShows (int): The number of HubSpot contacts that registered for this marketing event, but did not attend. This field only has a value when the event is over.
            - cancellations (int): The number of HubSpot contacts that registered for this marketing event, but later cancelled their registration.
            - createdAt (str): Creation timestamp.
            - startDateTime (str): The start date and time of the marketing event.
            - customProperties (Optional[List[Dict[str, Any]]]): Custom properties associated with the event.
                - sourceId (str): Source identifier.
                - selectedByUser (bool): Whether the property was selected by the user.
                - sourceLabel (str): Label of the source.
                - source (str): Source of the property.
                - updatedByUserId (int): ID of the user who last updated the property.
                - persistenceTimestamp (int): Timestamp for persistence.
                - sourceMetadata (str): Source metadata encoded as a base64 string.
                - dataSensitivity (str): Data sensitivity level.
                - unit (str): Unit of measurement.
                - requestId (str): Request identifier.
                - isEncrypted (bool): Whether the value is encrypted.
                - name (str): Property name.
                - useTimestampAsPersistenceTimestamp (bool): Whether to use timestamp as persistence timestamp.
                - value (str): Property value.
                - selectedByUserTimestamp (int): Timestamp when selected by user.
                - timestamp (int): Property timestamp.
                - isLargeValue (bool): Whether the value is large.
            - eventCancelled (bool): Indicates if the marketing event has been cancelled.
            - externalEventId (str): The id of the marketing event in the external event application.
            - eventDescription (str): The description of the marketing event.
            - eventName (str): The name of the marketing event.
            - id (str): Internal ID of the event.
            - objectId (str): Object ID.
            - updatedAt (str): Last update timestamp.
    """
    if not externalEventId:
        return {"error": "Event ID is required."}
    if externalEventId not in DB["marketing_events"]:
        return {"error": "Event not found."}
    attendees = list(
        DB["marketing_events"][externalEventId].get("attendees", {}).values()
    )
    if limit:
        attendees = attendees[:limit]
    return {"results": attendees}


def delete_attendee(
    externalEventId: str, attendeeId: str, externalAccountId: str
) -> None:
    """Remove an attendee from a marketing event.

    Args:
        externalEventId (str): The unique identifier for the marketing event as per the external system where the event was created.
        attendeeId (str): The unique identifier for the attendee.
        externalAccountId (str): The unique identifier for the account where the event was created.

    Returns:
        None
    """
    if not externalEventId:
        return {"error": "Event ID is required."}
    if not attendeeId:
        return {"error": "Attendee ID is required."}
    if not externalAccountId:
        return {"error": "External Account ID is required."}

    if externalEventId not in DB["marketing_events"]:
        return {"error": "Event not found."}
    if "attendees" not in DB["marketing_events"][externalEventId]:
        return {"error": "Attendees not found."}
    if attendeeId not in DB["marketing_events"][externalEventId]["attendees"]:
        return {"error": "Attendee not found."}

    if (
        DB["marketing_events"][externalEventId]["externalAccountId"]
        == externalAccountId
    ):
        deleted = DB["marketing_events"][externalEventId]["attendees"].pop(
            attendeeId, None
        )
        return deleted
    else:
        return {"error": "Invalid external account ID."}
