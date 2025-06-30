# Bilan de Compétence API Documentation

## Overview

The Bilan de Compétence API provides comprehensive endpoints for managing the French skills assessment process. The system consists of four integrated modules:

1. **360° Assessment System** - Multi-source feedback and evaluations
2. **Career Intelligence System** - Job market data and career planning
3. **Legal Compliance System** - French Labor Code compliance tracking
4. **Advanced Learning System** - AI-powered personalized learning paths

## API Endpoints

### 1. 360° Assessment System (`/api/v1/assessments`)

#### Assessments Management
- `GET /api/v1/assessments` - List all assessments
- `POST /api/v1/assessments` - Create new assessment
- `GET /api/v1/assessments/{id}` - Get assessment details
- `PUT /api/v1/assessments/{id}` - Update assessment
- `POST /api/v1/assessments/{id}/complete` - Mark assessment as completed

#### Questions Management
- `GET /api/v1/assessments/{id}/questions` - Get assessment questions
- `POST /api/v1/assessments/{id}/questions` - Add questions to assessment

#### Invitations & Responses
- `GET /api/v1/assessments/{id}/invitations` - List invitations
- `POST /api/v1/assessments/{id}/invitations` - Send invitations
- `GET /api/v1/assessments/{id}/responses` - Get responses
- `POST /api/v1/assessments/{id}/submit` - Submit assessment response

#### Public Access
- `GET /api/v1/assessments/public/{token}` - Access assessment via invitation token
- `POST /api/v1/assessments/public/{token}/submit` - Submit response as external evaluator

#### Reference Data
- `GET /api/v1/assessments/competencies` - List all competencies

### 2. Career Intelligence System (`/api/v1/career`)

#### Market Intelligence
- `GET /api/v1/career/market-data` - Search job market data
- `GET /api/v1/career/market-data/{id}` - Get detailed market data

#### Career Planning
- `GET /api/v1/career/paths` - List user's career paths
- `POST /api/v1/career/paths` - Create career path
- `GET /api/v1/career/paths/{id}` - Get career path details
- `POST /api/v1/career/paths/{id}/milestones` - Add milestone
- `POST /api/v1/career/milestones/{id}/complete` - Complete milestone

#### Skills Analysis
- `POST /api/v1/career/skill-gap-analysis` - Create skill gap analysis
- `GET /api/v1/career/skill-gap-analysis/{id}` - Get analysis details

#### Job Opportunities
- `GET /api/v1/career/opportunities` - List job opportunities
- `POST /api/v1/career/opportunities/search` - Search and save opportunities
- `POST /api/v1/career/opportunities/{id}/apply` - Mark as applied

#### Documents
- `GET /api/v1/career/documents` - List career documents
- `POST /api/v1/career/documents` - Upload document (resume, portfolio)

#### Insights
- `GET /api/v1/career/insights` - Get AI-powered career insights

### 3. Legal Compliance System (`/api/v1/compliance`)

#### Session Management
- `GET /api/v1/compliance/sessions` - List Bilan sessions
- `POST /api/v1/compliance/sessions` - Create session
- `GET /api/v1/compliance/sessions/{id}` - Get session details
- `POST /api/v1/compliance/sessions/{id}/start` - Start session
- `POST /api/v1/compliance/sessions/{id}/complete` - Complete session

#### Time Tracking
- `POST /api/v1/compliance/time-logs` - Create time log entry

#### Consultants
- `GET /api/v1/compliance/consultants` - List certified consultants
- `POST /api/v1/compliance/consultants/register` - Register as consultant

#### Compliance Monitoring
- `POST /api/v1/compliance/check/{session_id}` - Check session compliance
- `GET /api/v1/compliance/statistics` - Get compliance statistics

#### GDPR & Privacy
- `POST /api/v1/compliance/gdpr/consent` - Record GDPR consent
- `GET /api/v1/compliance/gdpr/consent` - List consents
- `POST /api/v1/compliance/gdpr/consent/{id}/withdraw` - Withdraw consent

#### Reports
- `POST /api/v1/compliance/reports/synthesis/{beneficiary_id}` - Generate synthesis report
- `POST /api/v1/compliance/reports/{id}/validate` - Validate report

#### Data Retention
- `GET /api/v1/compliance/data-retention` - Get retention policies

### 4. Advanced Learning System (`/api/v1/learning`)

#### Content Discovery
- `GET /api/v1/learning/content` - Browse learning content
- `GET /api/v1/learning/content/{id}` - Get content details

#### Learning Paths
- `GET /api/v1/learning/paths` - List learning paths
- `POST /api/v1/learning/paths` - Create personalized path
- `GET /api/v1/learning/paths/{id}` - Get path details
- `POST /api/v1/learning/paths/{id}/activate` - Activate path
- `POST /api/v1/learning/paths/{path_id}/content/{content_id}/complete` - Complete content

#### Mentorship
- `GET /api/v1/learning/mentorship/available` - Find available mentors
- `POST /api/v1/learning/mentorship/request` - Request mentorship
- `POST /api/v1/learning/mentorship/{id}/accept` - Accept mentorship
- `POST /api/v1/learning/mentorship/{id}/sessions` - Create session

#### Job Simulations
- `GET /api/v1/learning/simulations` - List simulations
- `POST /api/v1/learning/simulations/{id}/start` - Start simulation
- `POST /api/v1/learning/simulations/{id}/attempts/{attempt_id}/complete` - Complete simulation

#### Recommendations & Progress
- `GET /api/v1/learning/recommendations` - Get content recommendations
- `POST /api/v1/learning/recommendations/{id}/view` - Mark as viewed
- `GET /api/v1/learning/progress/summary` - Get learning progress

### 5. Integrated Dashboard (`/api/v1/bilan`)

#### Dashboard Views
- `GET /api/v1/bilan/dashboard` - Get comprehensive dashboard data
- `GET /api/v1/bilan/timeline/{beneficiary_id}` - Get Bilan timeline
- `GET /api/v1/bilan/progress/{beneficiary_id}` - Get detailed progress
- `GET /api/v1/bilan/recommendations/{beneficiary_id}` - Get AI recommendations

## Authentication

All endpoints require JWT authentication with the following headers:
- `Authorization: Bearer {jwt_token}`
- `X-Tenant-ID: {tenant_id}`

## Request/Response Format

All requests and responses use JSON format.

### Common Response Structure
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_prev": false,
    "has_next": true
  }
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": {}
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate-limited to:
- 1000 requests per hour
- 100 requests per minute

## Next Steps

1. **Frontend Integration** - Create React components for each system
2. **AI Integration** - Implement AI-powered recommendations and analysis
3. **Testing** - Comprehensive API testing with Pytest
4. **Documentation** - OpenAPI/Swagger documentation
5. **Deployment** - Production deployment with monitoring