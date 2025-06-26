# Calendar Integration Documentation

## Overview

The BDC platform now supports calendar integration for course sessions/appointments. Users can download .ics files or add sessions directly to their preferred calendar applications.

## Features

### 1. Backend API Endpoints

#### Get Course Sessions
```
GET /api/v1/programs/{program_id}/courses/{course_id}/sessions
```
Returns all sessions for a specific course with calendar URLs.

#### Download Session Calendar
```
GET /api/v1/programs/{program_id}/courses/{course_id}/sessions/{session_id}/calendar
```
Downloads an .ics file for a specific session.

Query Parameters:
- `timezone` (optional): User's timezone (default: UTC)

### 2. Frontend Components

#### CalendarButton Component
A dropdown button that provides multiple options for adding sessions to calendars:
- Download .ics file
- Add to Google Calendar
- Add to Outlook
- Add to Apple Calendar

Usage:
```tsx
<CalendarButton
  session={session}
  courseTitle="Programming 101"
  programId={1}
  courseId={2}
  size="sm"
  variant="outline"
/>
```

#### Sessions List Page
A dedicated page (`/sessions`) showing all upcoming sessions across all courses with:
- Filtering by past/future sessions
- Session details (time, location, instructor)
- Calendar integration buttons
- Online session links

### 3. Calendar File Format

The generated .ics files include:
- Event title (Course + Session name)
- Description with course details and instructor info
- Start and end times with proper timezone handling
- Location (physical address or online link)
- 30-minute reminder
- Unique identifier for updates
- Compatible with all major calendar applications

## Implementation Details

### Backend

1. **Calendar Utility** (`app/utils/calendar.py`):
   - `generate_ics_file()`: Core function for creating ICS content
   - `generate_session_ics()`: Specialized function for course sessions
   - Proper timezone handling using pytz
   - RFC 5545 compliant formatting

2. **API Endpoints** (`app/api/v1/courses.py`):
   - Session calendar download endpoint
   - Sessions list endpoint with calendar URLs

### Frontend

1. **Calendar Utilities** (`src/utils/calendar.ts`):
   - `downloadSessionCalendar()`: Downloads ICS file
   - `openInCalendar()`: Opens in web-based calendars
   - `formatSessionDateTime()`: Formats session times

2. **Components**:
   - `CalendarButton`: Reusable calendar integration button
   - `SessionsList`: Dedicated sessions/appointments page
   - Integration in `CourseDetail` page

## Usage Examples

### For Students/Users
1. Navigate to a course detail page
2. Find the session in the sessions table
3. Click the calendar button in the Actions column
4. Choose your preferred calendar option

### For Developers

#### Adding Calendar Button to a Component
```tsx
import { CalendarButton } from '@/components/ui/CalendarButton';

// In your component
<CalendarButton
  session={sessionData}
  courseTitle={course.title}
  programId={course.program_id}
  courseId={course.id}
/>
```

#### Customizing ICS Content
```python
from app.utils.calendar import generate_ics_file

ics_content = generate_ics_file(
    title="Team Meeting",
    description="Quarterly review",
    start_time=datetime(2024, 12, 25, 14, 0),
    end_time=datetime(2024, 12, 25, 16, 0),
    location="Conference Room A",
    timezone="America/New_York",
    organizer_email="manager@company.com"
)
```

## Security Considerations

- All calendar endpoints require authentication
- Users can only access sessions for courses they're enrolled in
- No sensitive data is included in calendar files
- Calendar URLs include program/course IDs for access control

## Future Enhancements

1. Recurring sessions support
2. Calendar sync (two-way synchronization)
3. Email calendar invitations
4. Bulk calendar export for multiple sessions
5. iCal subscription feeds for automatic updates