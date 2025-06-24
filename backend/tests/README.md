# BDC Backend Tests

## Overview
This directory contains comprehensive test suite for the BDC backend application.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── unit/               # Unit tests
│   ├── services/       # Service layer tests
│   │   └── test_beneficiary_service.py
│   └── api/           # API endpoint tests
│       └── v1/
│           └── test_beneficiaries.py
└── integration/       # Integration tests (to be added)
```

## Running Tests

### Run all tests with coverage:
```bash
./run_tests.sh
```

### Run specific test file:
```bash
python -m pytest tests/unit/services/test_beneficiary_service.py -v
```

### Run tests by marker:
```bash
# Run only service tests
python -m pytest -m service -v

# Run only API tests
python -m pytest -m api -v
```

### Run tests with specific coverage report:
```bash
python -m pytest --cov=app.services --cov-report=term-missing
```

## Test Coverage

Current test coverage targets:
- **Overall**: >90%
- **Services**: >95%
- **API Endpoints**: >90%
- **Models**: >85%

## Fixtures

Key fixtures available in `conftest.py`:

- `app`: Flask application instance
- `client`: Test client for API requests
- `db_session`: Database session for tests
- `test_tenant`: Test tenant instance
- `admin_user`, `trainer_user`, `student_user`: Test users with different roles
- `test_beneficiary`: Single test beneficiary
- `multiple_beneficiaries`: Multiple test beneficiaries
- `auth_headers`: JWT authentication headers

## Writing Tests

### Service Tests Example:
```python
def test_create_beneficiary_success(self, db_session, admin_user):
    service = BeneficiaryService(db_session, admin_user)
    
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@test.com'
    }
    
    beneficiary = service.create(data)
    
    assert beneficiary.first_name == 'John'
    assert beneficiary.email == 'john.doe@test.com'
```

### API Tests Example:
```python
def test_get_beneficiaries_success(self, client, auth_headers):
    response = client.get('/api/v1/beneficiaries', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'beneficiaries' in data
```

## Test Categories

### Happy Path Tests
- Test successful operations with valid data
- Test expected behavior under normal conditions

### Edge Cases
- Test boundary conditions
- Test with empty/null values
- Test with maximum/minimum values

### Error Cases
- Test with invalid data
- Test permission denied scenarios
- Test not found scenarios
- Test validation errors

### Security Tests
- Test role-based access control
- Test authentication requirements
- Test tenant isolation

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should clearly describe what they test
3. **Coverage**: Aim for high coverage but focus on meaningful tests
4. **Performance**: Keep unit tests fast (< 1 second per test)
5. **Fixtures**: Use fixtures to reduce code duplication
6. **Assertions**: Use specific assertions with clear messages

## Continuous Integration

Tests are automatically run on:
- Every push to main branch
- Every pull request
- Can be triggered manually

Coverage reports are generated and stored as artifacts.