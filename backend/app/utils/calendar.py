"""Calendar utilities for generating .ics files."""

from datetime import datetime, timedelta
import pytz
from typing import Optional, Dict, Any
import uuid as uuid_lib


def generate_ics_file(
    title: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    location: Optional[str] = None,
    organizer_email: Optional[str] = None,
    attendee_email: Optional[str] = None,
    timezone: str = "UTC",
    online_link: Optional[str] = None,
    uid: Optional[str] = None,
) -> str:
    """
    Generate an .ics (iCalendar) file content for a calendar event.
    
    Args:
        title: Event title
        description: Event description
        start_time: Event start time (datetime object)
        end_time: Event end time (datetime object)
        location: Physical location or address
        organizer_email: Email of the event organizer
        attendee_email: Email of the attendee
        timezone: Timezone string (e.g., 'America/New_York')
        online_link: Online meeting link if virtual
        uid: Unique identifier for the event
        
    Returns:
        String content of the .ics file
    """
    # Generate UID if not provided
    if not uid:
        uid = f"{uuid_lib.uuid4()}@bdc.local"
    
    # Get timezone object
    try:
        tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.UTC
    
    # Ensure times are timezone-aware
    if start_time.tzinfo is None:
        start_time = tz.localize(start_time)
    else:
        start_time = start_time.astimezone(tz)
        
    if end_time.tzinfo is None:
        end_time = tz.localize(end_time)
    else:
        end_time = end_time.astimezone(tz)
    
    # Convert to UTC for the ICS file
    start_utc = start_time.astimezone(pytz.UTC)
    end_utc = end_time.astimezone(pytz.UTC)
    
    # Format timestamps
    dtstamp = datetime.now(pytz.UTC).strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_utc.strftime("%Y%m%dT%H%M%SZ")
    dtend = end_utc.strftime("%Y%m%dT%H%M%SZ")
    
    # Build ICS content
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Beneficiary Development Center//BDC Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{_escape_ics_text(title)}",
    ]
    
    # Add description
    if description:
        # If there's an online link, add it to the description
        full_description = description
        if online_link:
            full_description += f"\\n\\nJoin online: {online_link}"
        ics_lines.append(f"DESCRIPTION:{_escape_ics_text(full_description)}")
    
    # Add location
    if location:
        ics_lines.append(f"LOCATION:{_escape_ics_text(location)}")
    elif online_link:
        ics_lines.append(f"LOCATION:{_escape_ics_text(online_link)}")
    
    # Add URL if online
    if online_link:
        ics_lines.append(f"URL:{online_link}")
    
    # Add organizer
    if organizer_email:
        ics_lines.append(f"ORGANIZER;CN=Organizer:mailto:{organizer_email}")
    
    # Add attendee
    if attendee_email:
        ics_lines.append(
            f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;"
            f"RSVP=TRUE;CN={attendee_email}:mailto:{attendee_email}"
        )
    
    # Set status and transparency
    ics_lines.extend([
        "STATUS:CONFIRMED",
        "TRANSP:OPAQUE",
        "SEQUENCE:0",
        "BEGIN:VALARM",
        "TRIGGER:-PT30M",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR"
    ])
    
    # Join with CRLF line endings as per RFC 5545
    return "\r\n".join(ics_lines)


def _escape_ics_text(text: str) -> str:
    """
    Escape special characters in ICS text fields.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for ICS format
    """
    if not text:
        return ""
    
    # Replace special characters
    text = text.replace("\\", "\\\\")
    text = text.replace(",", "\\,")
    text = text.replace(";", "\\;")
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")
    
    # Fold long lines (RFC 5545 requires lines to be max 75 octets)
    # We'll use 70 to be safe with multi-byte characters
    if len(text) <= 70:
        return text
    
    # Fold the text
    folded = []
    while text:
        if len(text) <= 70:
            folded.append(text)
            break
        else:
            # Find a safe break point
            break_point = 70
            folded.append(text[:break_point])
            text = " " + text[break_point:]  # Continue with a space
    
    return "\r\n".join(folded)


def generate_session_ics(session: Dict[str, Any], course_title: str = "", timezone: str = "UTC") -> str:
    """
    Generate an ICS file for a course session.
    
    Args:
        session: Session dictionary with required fields
        course_title: Title of the course
        timezone: Timezone for the session
        
    Returns:
        ICS file content as string
    """
    # Build title
    title = f"{course_title}: {session.get('title', 'Course Session')}" if course_title else session.get('title', 'Course Session')
    
    # Build description
    description_parts = []
    if course_title:
        description_parts.append(f"Course: {course_title}")
    if session.get('description'):
        description_parts.append(session['description'])
    if session.get('instructor_name'):
        description_parts.append(f"Instructor: {session['instructor_name']}")
    
    description = "\\n\\n".join(description_parts)
    
    # Get location info
    location = None
    online_link = None
    
    if session.get('is_online') and session.get('online_link'):
        online_link = session['online_link']
        location = "Online Session"
    else:
        location_parts = []
        if session.get('location'):
            location_parts.append(session['location'])
        if session.get('room_number'):
            location_parts.append(f"Room {session['room_number']}")
        location = ", ".join(location_parts) if location_parts else None
    
    # Parse start time
    start_time = session.get('session_date')
    if isinstance(start_time, str):
        # Try to parse ISO format
        try:
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    
    # Calculate end time
    duration_hours = session.get('duration_hours', 1.0)
    end_time = start_time + timedelta(hours=duration_hours)
    
    # Generate UID using session UUID if available
    uid = None
    if session.get('uuid'):
        uid = f"{session['uuid']}@bdc.local"
    
    return generate_ics_file(
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        location=location,
        online_link=online_link,
        timezone=timezone,
        uid=uid
    )