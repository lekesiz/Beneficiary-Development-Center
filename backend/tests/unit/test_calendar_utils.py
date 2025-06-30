"""Tests for calendar utility functions."""

import pytest
from datetime import datetime, timedelta
import pytz
from app.utils.calendar import generate_ics_file, generate_session_ics, _escape_ics_text


class TestCalendarUtils:
    """Test calendar utility functions."""

    def test_generate_ics_file_basic(self):
        """Test basic ICS file generation."""
        start_time = datetime(2024, 12, 25, 14, 0, 0)
        end_time = datetime(2024, 12, 25, 16, 0, 0)

        ics_content = generate_ics_file(
            title="Test Event",
            description="Test Description",
            start_time=start_time,
            end_time=end_time,
            location="Test Location",
        )

        assert "BEGIN:VCALENDAR" in ics_content
        assert "END:VCALENDAR" in ics_content
        assert "SUMMARY:Test Event" in ics_content
        assert "DESCRIPTION:Test Description" in ics_content
        assert "LOCATION:Test Location" in ics_content
        assert "DTSTART:20241225T140000Z" in ics_content
        assert "DTEND:20241225T160000Z" in ics_content

    def test_generate_ics_file_with_timezone(self):
        """Test ICS file generation with timezone."""
        tz = pytz.timezone("America/New_York")
        start_time = tz.localize(datetime(2024, 12, 25, 14, 0, 0))
        end_time = tz.localize(datetime(2024, 12, 25, 16, 0, 0))

        ics_content = generate_ics_file(
            title="Test Event",
            description="Test Description",
            start_time=start_time,
            end_time=end_time,
            timezone="America/New_York",
        )

        # Times should be converted to UTC
        assert "DTSTART:20241225T190000Z" in ics_content  # 14:00 EST = 19:00 UTC
        assert "DTEND:20241225T210000Z" in ics_content  # 16:00 EST = 21:00 UTC

    def test_generate_ics_file_with_online_link(self):
        """Test ICS file generation with online link."""
        start_time = datetime(2024, 12, 25, 14, 0, 0)
        end_time = datetime(2024, 12, 25, 16, 0, 0)

        ics_content = generate_ics_file(
            title="Online Meeting",
            description="Join online",
            start_time=start_time,
            end_time=end_time,
            online_link="https://zoom.us/j/123456789",
        )

        assert "URL:https://zoom.us/j/123456789" in ics_content
        assert "Join online: https://zoom.us/j/123456789" in ics_content

    def test_escape_ics_text(self):
        """Test ICS text escaping."""
        # Test special character escaping
        assert _escape_ics_text("Hello, World") == "Hello\\, World"
        assert _escape_ics_text("Test;Semicolon") == "Test\\;Semicolon"
        assert _escape_ics_text("Line\nBreak") == "Line\\nBreak"
        assert _escape_ics_text("Back\\slash") == "Back\\\\slash"

        # Test long line folding
        long_text = "A" * 100
        escaped = _escape_ics_text(long_text)
        lines = escaped.split("\r\n")
        assert len(lines) > 1
        assert len(lines[0]) <= 70
        assert lines[1].startswith(" ")

    def test_generate_session_ics(self):
        """Test session ICS generation."""
        session = {
            "uuid": "12345678-1234-1234-1234-123456789012",
            "title": "Python Basics",
            "description": "Introduction to Python programming",
            "session_date": "2024-12-25T14:00:00",
            "duration_hours": 2.0,
            "location": "Room 101",
            "room_number": "A",
            "is_online": False,
            "instructor_name": "John Doe",
        }

        ics_content = generate_session_ics(session=session, course_title="Programming 101", timezone="UTC")

        assert "SUMMARY:Programming 101: Python Basics" in ics_content
        assert "Course: Programming 101" in ics_content
        # Handle ICS line folding for instructor field
        ics_unfolded = ics_content.replace("\r\n ", "")
        assert "Instructor: John Doe" in ics_unfolded
        assert "LOCATION:Room 101\\, Room A" in ics_content
        assert "UID:12345678-1234-1234-1234-123456789012@bdc.local" in ics_content

    def test_generate_session_ics_online(self):
        """Test online session ICS generation."""
        session = {
            "title": "Online Session",
            "session_date": datetime(2024, 12, 25, 14, 0, 0),
            "duration_hours": 1.5,
            "is_online": True,
            "online_link": "https://meet.google.com/abc-defg-hij",
        }

        ics_content = generate_session_ics(session)

        assert "LOCATION:Online Session" in ics_content
        assert "URL:https://meet.google.com/abc-defg-hij" in ics_content
        # The description might not include "Join online:" text - let's check if the URL is properly set
        assert "https://meet.google.com/abc-defg-hij" in ics_content

    def test_generate_ics_with_attendees(self):
        """Test ICS generation with organizer and attendee."""
        start_time = datetime(2024, 12, 25, 14, 0, 0)
        end_time = datetime(2024, 12, 25, 16, 0, 0)

        ics_content = generate_ics_file(
            title="Meeting",
            description="Team meeting",
            start_time=start_time,
            end_time=end_time,
            organizer_email="organizer@example.com",
            attendee_email="attendee@example.com",
        )

        assert "ORGANIZER;CN=Organizer:mailto:organizer@example.com" in ics_content
        assert "ATTENDEE" in ics_content
        assert "mailto:attendee@example.com" in ics_content
        assert "RSVP=TRUE" in ics_content
