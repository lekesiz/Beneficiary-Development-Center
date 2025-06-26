#!/bin/bash

echo "Running frontend tests..."
cd /Users/mikail/Desktop/BDC/Beneficiary\ Development\ Center/frontend

# Run tests with JSON reporter to get structured output
npm test -- --run --reporter=json > test-results.json 2>&1

# Check if tests ran successfully
if [ $? -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed. Analyzing results..."
    
    # Extract failing test information
    echo "Failed tests:"
    cat test-results.json | grep -E '"status":"fail"' -B5 -A5 | head -100
    
    exit 1
fi