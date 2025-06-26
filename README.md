# BDC - Beneficiary Development Center

A comprehensive multi-tenant SaaS platform that digitalizes France's "Bilan de Compétence" professional skills assessment process.

## 🚀 Overview

BDC is a full-stack web application designed to streamline and digitalize the competency assessment process for training centers, HR departments, and educational institutions. The platform features AI-powered assessments, real-time collaboration, and comprehensive progress tracking.

## 🏗️ Technology Stack

**Backend:**
- Python 3.11
- Flask 3.0
- PostgreSQL 15+
- Redis 7+
- Celery (Task queue)
- Socket.IO (Real-time features)
- SQLAlchemy 2.x
- Alembic (Migrations)
- JWT (Authentication)
- Argon2 (Password hashing)
- Sentry (Monitoring)
- OpenAI API (AI features)
- Docker

**Frontend:**
- React 18 + TypeScript 5.5
- Vite 5
- Tailwind CSS
- Radix UI
- React Query
- Zustand (State management)
- i18next (Internationalization)
- Zod (Validation)
- Cypress (E2E)
- Vitest (Unit/Integration)
- MSW (API mocking)
- Storybook

## 📋 Key Features

- Multi-tenant architecture (tenant isolation, custom branding)
- 4 user roles: Super Admin, Admin, Trainer, Student
- AI-powered adaptive assessment engine (OpenAI GPT-4)
- Real-time chat and notifications (Socket.IO)
- Comprehensive beneficiary and program management
- Document and file upload system
- Progress tracking and analytics dashboards
- Advanced reporting (AI-generated insights, export)
- Role-based access control (RBAC)
- Secure authentication (JWT, Argon2, 2FA)
- Accessibility (ARIA, keyboard navigation)
- Internationalization (French, English, Spanish, German, Italian, Portuguese, Arabic)

## 🧪 Testing & Quality

**Frontend:**
- 211/211 tests passing (100% coverage)
- 24 test files (unit, integration, component, E2E)
- Cypress E2E flows for all critical user journeys
- Fast, stable, CI-ready test suite

**Backend:**
- 272 tests (pytest)
- Core modules: 85%+ pass rate
- Modern SQLAlchemy 2.x ORM
- Coverage: High on core features

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Backend Setup

```bash
cd "Beneficiary Development Center/backend"
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # Edit .env with your configuration
flask db upgrade
python wsgi.py
```

### Frontend Setup

```bash
cd "Beneficiary Development Center/frontend"
npm install
npm run dev
```

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📁 Project Structure

```
Beneficiary Development Center/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper functions
│   │   └── schemas/        # Data validation
│   ├── migrations/         # Database migrations
│   ├── tests/              # Test suite
│   └── config/             # Configuration files
└── frontend/
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── contexts/       # React contexts
    │   ├── hooks/          # Custom hooks
    │   ├── api/            # API client
    │   └── utils/          # Utilities
    └── public/             # Static assets
```

## 🔐 Security Features

- JWT token-based authentication
- Password hashing with Argon2
- CSRF protection
- XSS prevention
- SQL injection protection
- Rate limiting
- Input validation
- Secure file uploads
- Sentry monitoring

## 🌍 Internationalization

Supported languages:
- French (default)
- English
- Spanish
- German
- Italian
- Portuguese
- Arabic

## 📚 API Documentation

- Development: http://localhost:5000/api/docs
- Swagger UI: http://localhost:5000/api/v1/swagger

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### E2E Tests
```bash
cd frontend
npm run test:e2e
```

## 🚀 Deployment

- Docker Compose: `docker-compose up -d`
- Manual: See `/docs/deployment.md`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support, email mikail@lekesiz.org or join our Slack channel.

## 🙏 Acknowledgments

- Built with Flask and React
- UI components from Radix UI
- Icons from Lucide React
- AI powered by OpenAI