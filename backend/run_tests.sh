#!/bin/bash

# Script to run tests with coverage

echo "🧪 Running BDC Backend Tests..."
echo "================================"

# Set test environment
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:

# Run tests with coverage
echo "Running unit tests..."
python -m pytest tests/unit -v --cov=app --cov-report=term-missing --cov-report=html

# Check coverage threshold
coverage_result=$(python -m coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
threshold=90

echo ""
echo "================================"
echo "📊 Coverage Report Summary"
echo "================================"

if (( $(echo "$coverage_result >= $threshold" | bc -l) )); then
    echo "✅ Coverage: $coverage_result% (Target: $threshold%)"
    echo "✅ All tests passed with sufficient coverage!"
else
    echo "❌ Coverage: $coverage_result% (Target: $threshold%)"
    echo "❌ Coverage is below the required threshold!"
    exit 1
fi

echo ""
echo "📁 Detailed HTML coverage report available at: htmlcov/index.html"
echo ""

# Run specific test categories if requested
if [ "$1" == "service" ]; then
    echo "Running service tests only..."
    python -m pytest tests/unit/services -v -m service
elif [ "$1" == "api" ]; then
    echo "Running API tests only..."
    python -m pytest tests/unit/api -v -m api
fi