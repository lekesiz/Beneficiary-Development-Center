# BDC - Beneficiary Development Center

A comprehensive multi-tenant SaaS platform that digitalizes France's "Bilan de Compétence" professional skills assessment process.

## 🚀 Overview

BDC is a full-stack web application designed to streamline and digitalize the competency assessment process for training centers, HR departments, and educational institutions. The platform features AI-powered assessments, real-time collaboration, and comprehensive progress tracking.

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Flask 3.0 (Python web framework)
- PostgreSQL (Primary database)
- Redis (Caching and session management)
- Celery (Task queue)
- Socket.IO (Real-time features)
- JWT (Authentication)

**Frontend:**
- React 18 with TypeScript
- Vite (Build tool)
- Tailwind CSS (Styling)
- Radix UI (Component library)
- React Query (State management)
- i18next (Internationalization)

**AI Integration:**
- OpenAI API (GPT-4/GPT-3.5)
- Custom prompt engineering
- Automated content generation

## 📋 Key Features

### Multi-Tenant Architecture
- Complete tenant isolation
- Custom branding per tenant
- Subscription management
- Usage tracking and limits

### User Management
- 4 role types: Super Admin, Admin, Trainer, Student
- JWT-based authentication
- Two-factor authentication (2FA)
- Role-based access control (RBAC)

### Beneficiary Management
- Comprehensive profiles
- Document management
- Progress tracking
- Assignment to trainers

### Assessment Engine
- Multiple question types
- AI-powered evaluations
- Adaptive testing
- Automated grading

### Real-Time Features
- Live notifications
- Collaborative editing
- Instant messaging
- Progress updates

### Reporting & Analytics
- Custom dashboards
- Export capabilities
- AI-generated insights
- Performance metrics

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

1. Clone the repository:
```bash
cd "Beneficiary Development Center/backend"
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed-db  # Optional: Add sample data
```

6. Run the backend:
```bash
python wsgi.py
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd "../frontend"
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📁 Project Structure

```
Beneficiary Development Center/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── api/v1/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper functions
│   │   └── schemas/        # Data validation
│   ├── migrations/         # Database migrations
│   ├── tests/             # Test suite
│   └── config/            # Configuration files
│
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

## 🌍 Internationalization

Supported languages:
- French (default)
- English
- Spanish
- German
- Italian
- Portuguese
- Arabic

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

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
See detailed deployment guide in `/docs/deployment.md`

## 📚 API Documentation

API documentation is available at:
- Development: http://localhost:5000/api/docs
- Swagger UI: http://localhost:5000/api/v1/swagger

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support, email support@bdc-platform.com or join our Slack channel.

## 🙏 Acknowledgments

- Built with Flask and React
- UI components from Radix UI
- Icons from Lucide React
- AI powered by OpenAI