# Program Management API

## Overview

The Program Management API provides endpoints for creating, reading, updating, and deleting educational programs. Programs are the main organizational units that contain courses and enrollments.

## Base URL

```
/api/v1/programs
```

## Authentication

All endpoints require JWT authentication. Include the bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. List Programs

Get a paginated list of programs with optional filtering.

**Endpoint:** `GET /api/v1/programs`

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 20)
- `status` (string, optional): Filter by status (draft, published, active, suspended, completed, cancelled)
- `type` (string, optional): Filter by program type (vocational, academic, certification, workshop, bootcamp, other)
- `search` (string, optional): Search in title, description, and code
- `upcoming_only` (boolean, optional): Show only upcoming programs
- `active_only` (boolean, optional): Show only currently active programs

**Response:**
```json
{
  "programs": [
    {
      "id": 1,
      "code": "PROG001",
      "title": "Web Development Bootcamp",
      "description": "Comprehensive web development training",
      "program_type": "bootcamp",
      "status": "active",
      "start_date": "2024-02-01",
      "end_date": "2024-05-01",
      "enrollment_start": "2024-01-01",
      "enrollment_end": "2024-01-31",
      "min_participants": 10,
      "max_participants": 30,
      "current_enrollment": 25,
      "requirements": {
        "prerequisites": ["Basic computer skills"],
        "age_min": 18
      },
      "location": "Paris, France",
      "is_online": false,
      "is_hybrid": true,
      "online_link": "https://meet.example.com/web-dev",
      "price": 2500,
      "currency": "EUR",
      "tags": ["web", "development", "coding"],
      "metadata": {},
      "cover_image_url": "https://example.com/images/web-dev.jpg",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3
  }
}
```

### 2. Get Program Details

Get detailed information about a specific program.

**Endpoint:** `GET /api/v1/programs/{program_id}`

**Path Parameters:**
- `program_id` (integer, required): Program ID

**Query Parameters:**
- `include_courses` (boolean, optional): Include course list in response

**Response:**
```json
{
  "id": 1,
  "code": "PROG001",
  "title": "Web Development Bootcamp",
  "description": "Comprehensive web development training",
  "objectives": [
    "Master HTML, CSS, and JavaScript",
    "Build responsive web applications",
    "Learn modern frameworks"
  ],
  "program_type": "bootcamp",
  "status": "active",
  "start_date": "2024-02-01",
  "end_date": "2024-05-01",
  "enrollment_start": "2024-01-01",
  "enrollment_end": "2024-01-31",
  "min_participants": 10,
  "max_participants": 30,
  "current_enrollment": 25,
  "requirements": {
    "prerequisites": ["Basic computer skills"],
    "age_min": 18,
    "equipment": ["Laptop", "Internet connection"]
  },
  "location": "Paris, France",
  "is_online": false,
  "is_hybrid": true,
  "online_link": "https://meet.example.com/web-dev",
  "price": 2500,
  "currency": "EUR",
  "tags": ["web", "development", "coding"],
  "metadata": {
    "certification": "Web Developer Certificate",
    "duration_weeks": 12
  },
  "cover_image_url": "https://example.com/images/web-dev.jpg",
  "resources": [
    {
      "name": "Course Materials",
      "url": "https://example.com/materials/web-dev",
      "type": "pdf"
    }
  ],
  "coordinator": {
    "id": 5,
    "name": "John Doe",
    "email": "john.doe@example.com"
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "courses": [
    {
      "id": 1,
      "title": "HTML & CSS Fundamentals",
      "duration_hours": 40
    },
    {
      "id": 2,
      "title": "JavaScript Programming",
      "duration_hours": 60
    }
  ]
}
```

### 3. Create Program

Create a new program. Requires admin or manager role.

**Endpoint:** `POST /api/v1/programs`

**Request Body:**
```json
{
  "code": "PROG002",
  "title": "Data Science Fundamentals",
  "description": "Introduction to data science and analytics",
  "objectives": [
    "Understand data science concepts",
    "Learn Python for data analysis",
    "Master data visualization"
  ],
  "program_type": "certification",
  "start_date": "2024-03-01",
  "end_date": "2024-06-01",
  "enrollment_start": "2024-02-01",
  "enrollment_end": "2024-02-28",
  "min_participants": 15,
  "max_participants": 40,
  "requirements": {
    "prerequisites": ["Basic math", "Computer skills"],
    "age_min": 18
  },
  "location": "Online",
  "is_online": true,
  "is_hybrid": false,
  "price": 1500,
  "currency": "EUR",
  "tags": ["data-science", "python", "analytics"],
  "coordinator_id": 5
}
```

**Response:** 201 Created
```json
{
  "id": 2,
  "code": "PROG002",
  "title": "Data Science Fundamentals",
  "status": "draft",
  // ... full program object
}
```

### 4. Update Program

Update an existing program. Requires admin or manager role.

**Endpoint:** `PUT /api/v1/programs/{program_id}`

**Path Parameters:**
- `program_id` (integer, required): Program ID

**Request Body:** (Partial update supported)
```json
{
  "title": "Advanced Data Science",
  "description": "Advanced concepts in data science",
  "max_participants": 50,
  "tags": ["data-science", "python", "machine-learning"]
}
```

**Response:** 200 OK
```json
{
  "id": 2,
  "title": "Advanced Data Science",
  // ... updated program object
}
```

### 5. Delete Program

Soft delete a program. Requires admin role. Cannot delete programs with active enrollments.

**Endpoint:** `DELETE /api/v1/programs/{program_id}`

**Path Parameters:**
- `program_id` (integer, required): Program ID

**Response:** 204 No Content

### 6. Update Program Status

Update the status of a program. Requires admin or manager role.

**Endpoint:** `PUT /api/v1/programs/{program_id}/status`

**Path Parameters:**
- `program_id` (integer, required): Program ID

**Request Body:**
```json
{
  "status": "published"
}
```

**Valid Status Transitions:**
- `draft` → `published`
- `published` → `active`
- `active` → `suspended` or `completed`
- `suspended` → `active` or `cancelled`

**Response:** 200 OK
```json
{
  "id": 1,
  "status": "published",
  // ... full program object
}
```

### 7. Add Course to Program

Add a new course to a program. Requires admin or manager role.

**Endpoint:** `POST /api/v1/programs/{program_id}/courses`

**Path Parameters:**
- `program_id` (integer, required): Program ID

**Request Body:**
```json
{
  "title": "Advanced JavaScript",
  "subtitle": "ES6+ and Modern Frameworks",
  "description": "Deep dive into modern JavaScript",
  "format": "lecture",
  "difficulty_level": "intermediate",
  "duration_hours": 80,
  "objectives": [
    "Master ES6+ features",
    "Learn React and Vue.js"
  ],
  "instructor_id": 10
}
```

**Response:** 201 Created
```json
{
  "id": 3,
  "program_id": 1,
  "title": "Advanced JavaScript",
  // ... full course object
}
```

### 8. Get Program Statistics

Get aggregated statistics for all programs. Requires admin or manager role.

**Endpoint:** `GET /api/v1/programs/statistics`

**Response:**
```json
{
  "total_programs": 25,
  "status_breakdown": {
    "draft": 5,
    "published": 3,
    "active": 12,
    "suspended": 2,
    "completed": 3,
    "cancelled": 0
  },
  "type_breakdown": {
    "vocational": 8,
    "academic": 6,
    "certification": 5,
    "workshop": 3,
    "bootcamp": 2,
    "other": 1
  },
  "upcoming_programs": 7,
  "active_programs": 12,
  "total_active_enrollments": 385
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "title": ["Missing data for required field."],
    "start_date": ["Not a valid date."]
  }
}
```

### 403 Forbidden
```json
{
  "error": "Only admins and managers can create programs"
}
```

### 404 Not Found
```json
{
  "error": "Program not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create program"
}
```

## Data Types

### Program Status
- `draft`: Initial state, not published
- `published`: Available for enrollment
- `active`: Currently running
- `suspended`: Temporarily halted
- `completed`: Finished successfully
- `cancelled`: Terminated before completion

### Program Type
- `vocational`: Job-oriented training
- `academic`: Educational/theoretical
- `certification`: Leads to certification
- `workshop`: Short-term intensive
- `bootcamp`: Intensive training program
- `other`: Other program types

## Best Practices

1. **Program Codes**: Use unique, meaningful codes for easy identification
2. **Enrollment Dates**: Always set enrollment period before program start
3. **Capacity**: Set realistic min/max participants based on resources
4. **Requirements**: Clearly define prerequisites and equipment needs
5. **Tags**: Use consistent tags for better searchability
6. **Status Management**: Follow proper status transitions
7. **Resources**: Keep resource URLs updated and accessible

## Examples

### Create a Hybrid Workshop
```bash
curl -X POST https://api.example.com/api/v1/programs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "WS2024-01",
    "title": "Digital Marketing Workshop",
    "description": "Learn modern digital marketing strategies",
    "program_type": "workshop",
    "start_date": "2024-03-15",
    "end_date": "2024-03-17",
    "is_hybrid": true,
    "location": "Paris",
    "online_link": "https://meet.example.com/digital-marketing",
    "max_participants": 25
  }'
```

### Search for Active Vocational Programs
```bash
curl -X GET "https://api.example.com/api/v1/programs?status=active&type=vocational" \
  -H "Authorization: Bearer <token>"
```