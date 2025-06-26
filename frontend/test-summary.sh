#!/bin/bash

echo "Running test summary..."

# List of test files we've been working on
test_files=(
  "src/pages/settings/__tests__/Settings.test.tsx"
  "src/pages/beneficiaries/__tests__/BeneficiaryForm.test.tsx"
  "src/pages/programs/__tests__/ProgramForm.test.tsx"
  "src/components/ui/__tests__/Badge.test.tsx"
  "src/hooks/__tests__/useFiles.test.ts"
  "src/pages/beneficiaries/__tests__/BeneficiaryDetail.test.tsx"
)

for file in "${test_files[@]}"; do
  echo ""
  echo "Testing: $file"
  npm test "$file" -- --run 2>&1 | grep -E "(Test Files|Tests)" | tail -2
done