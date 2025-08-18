# APIs/google_calendar/SimulationEngine/utils.py
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..SimulationEngine.db import DB
from gmail.Users.Messages import insert as gmail_insert
from gmail.SimulationEngine.db import DB as GmailDB

def parse_iso_datetime(iso_string):
    return datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ") if iso_string else None


def get_primary_calendar_list_entry():
    # The DB["calendar_list"] is a dict of {id: {id, summary, description, timeZone, primary}}
    # Find the entry where "primary" is True
    primary_calendar_list_entry = next(
        (entry for entry in DB["calendar_list"].values() if entry.get("primary") is True),
        None
    )
    if primary_calendar_list_entry is None:
        raise ValueError("Primary calendar list entry not found.")
    return primary_calendar_list_entry

def get_primary_calendar_entry():
    primary_calendar_entry = next(
        (entry for entry in DB["calendars"].values() if entry.get("primary") is True),
        None
    )
    if primary_calendar_entry is None:
        raise ValueError("Primary calendar not found.")
    return primary_calendar_entry


# --- Notification Helper Functions ---

def get_calendar_owner_email(calendar_id: str) -> Optional[str]:
    """
    Best-effort extraction of the calendar owner's email using ACL rules.
    Returns None if not determinable.
    """
    try:
        acl_rules = DB.get("acl_rules", {})
        for rule in acl_rules.values():
            if (
                isinstance(rule, dict)
                and rule.get("calendarId") == calendar_id
                and rule.get("role") == "owner"
            ):
                scope = rule.get("scope", {})
                if scope.get("type") == "user" and isinstance(scope.get("value"), str):
                    return scope.get("value")
    except Exception:
        pass
    return None


def extract_email_domain(email_address: Optional[str]) -> Optional[str]:
    """Extract domain from email address."""
    if not email_address or "@" not in email_address:
        return None
    return email_address.split("@", 1)[-1].lower()


def select_attendee_recipients(
    attendees: Optional[List[Dict[str, Any]]],
    send_updates_mode: Optional[str],
    organizer_domain: Optional[str],
) -> List[str]:
    """
    Determine which attendees should receive notifications based on sendUpdates.
    - none or no attendees: []
    - all: all attendees with a valid email, excluding organizer/self
    - externalOnly: attendees whose domain differs from organizer_domain
      If organizer_domain is unknown, return [].
    """
    if not attendees or not isinstance(attendees, list):
        return []

    mode = (send_updates_mode or "none").lower()
    if mode not in {"all", "externalonly", "none"}:
        mode = "none"
    if mode == "none":
        return []

    candidate_emails: List[str] = []
    for attendee in attendees:
        if not isinstance(attendee, dict):
            continue
        email = attendee.get("email")
        if not isinstance(email, str) or "@" not in email:
            continue
        if attendee.get("organizer") is True:
            continue
        if attendee.get("self") is True:
            continue
        candidate_emails.append(email)

    if not candidate_emails:
        return []

    if mode == "all":
        seen = set()
        unique: List[str] = []
        for e in candidate_emails:
            if e not in seen:
                seen.add(e)
                unique.append(e)
        return unique

    # externalOnly
    if organizer_domain is None:
        return []
    seen = set()
    filtered: List[str] = []
    for e in candidate_emails:
        domain = extract_email_domain(e)
        if domain and domain != organizer_domain and e not in seen:
            seen.add(e)
            filtered.append(e)
    return filtered


def build_invitation_email_payload(
    organizer_email: Optional[str],
    recipient_email: str,
    event: Dict[str, Any],
    subject_prefix: str = "Invitation",
) -> Dict[str, Any]:
    """Build email payload for calendar event notifications."""
    summary = (event.get("summary") or "Event").strip() or "Event"
    description = (event.get("description") or "").strip()
    start_dt = event.get("start", {}).get("dateTime") or ""
    end_dt = event.get("end", {}).get("dateTime") or ""
    location = (event.get("location") or "").strip()

    subject = f"{subject_prefix}: {summary}"
    lines: List[str] = [f"You're invited to: {summary}"]
    if description:
        lines.append("")
        lines.append(description)
    if start_dt or end_dt:
        lines.append("")
        if start_dt:
            lines.append(f"Starts: {start_dt}")
        if end_dt:
            lines.append(f"Ends:   {end_dt}")
    if location:
        lines.append("")
        lines.append(f"Location: {location}")
    if organizer_email:
        lines.append("")
        lines.append(f"Organizer: {organizer_email}")

    body = "\n".join(lines)

    return {
        "sender": organizer_email or "",
        "recipient": recipient_email,
        "subject": subject,
        "body": body,
    }


def notify_attendees(
    calendar_id: str,
    event_obj: Dict[str, Any],
    send_updates_mode: Optional[str],
    subject_prefix: str,
) -> None:
    """Send Gmail notifications to event attendees based on sendUpdates mode."""
    if send_updates_mode not in {"all", "externalOnly"}:
        return
    attendees: Optional[List[Dict[str, Any]]] = event_obj.get("attendees")
    organizer_email = get_calendar_owner_email(calendar_id)
    organizer_domain = extract_email_domain(organizer_email)

    recipients = select_attendee_recipients(attendees, send_updates_mode, organizer_domain)

    for recipient_email in recipients:
        payload = build_invitation_email_payload(
            organizer_email, recipient_email, event_obj, subject_prefix
        )
        user_id = None
        for uid, user_data in GmailDB["users"].items():
            if user_data.get("profile", {}).get("emailAddress") == recipient_email:
                user_id = uid
                break
        
        # If user not found, use email as fallback
        if user_id is None:
            user_id = recipient_email
        
        try:
            gmail_insert(userId=user_id, msg=payload)
        except Exception:
            # Non-fatal in simulation
            pass
