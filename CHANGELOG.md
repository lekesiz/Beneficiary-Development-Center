# Changelog

All notable changes to the Beneficiary Development Center (BDC) platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0-alpha] - 2025-06-25

### Added
- Initial alpha release establishing baseline functionality
- Core authentication system with JWT tokens
- Multi-tenant architecture support
- Program Management module with CRUD operations
- AI-powered adaptive assessment engine (MVP)
- WebSocket support for real-time features
- Comprehensive test suite structure
- Docker support for local development
- Initial database models and relationships

### Technical Stack
- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended, Celery
- **Frontend**: React, TypeScript, Socket.io-client
- **Database**: PostgreSQL with Alembic migrations
- **Cache**: Redis
- **AI/ML**: OpenAI API integration for adaptive assessments

### Known Issues
- E2E test coverage incomplete
- CI/CD pipeline not yet configured
- Some database migrations need consolidation
- Production deployment configuration pending

### Contributors
- Initial development team
- AI pair programming assistance

[0.5.0-alpha]: https://github.com/lekesiz/Beneficiary-Development-Center/releases/tag/v0.5.0-alpha