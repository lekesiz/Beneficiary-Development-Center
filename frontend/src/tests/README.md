# Frontend Tests

## Overview

This directory contains the test suite for the BDC frontend application.

## Test Structure

```
src/tests/
├── setup/
│   └── setup.ts         # Test environment setup
├── utils/
│   └── test-utils.tsx   # Custom render functions with providers
├── mocks/
│   ├── beneficiary.ts   # Mock data for beneficiaries
│   ├── handlers.ts      # MSW request handlers
│   └── server.ts        # MSW server setup
└── README.md
```

## Component Tests

### UI Components

- **TagInput**: Full interaction testing including keyboard events
- **Badge**: Variant and size testing
- **Modal**: Open/close behavior, backdrop clicks, confirm dialogs

### Beneficiary Components

- **BeneficiaryForm**:
  - Create/Edit modes
  - Form validation
  - Role-based field visibility
  - Submit handling
- **BeneficiaryDetail**:
  - Data display
  - Loading/error states
  - Role-based actions
  - Delete confirmation

### Hooks

- **useBeneficiaries**:
  - Data fetching with parameters
  - Mutations (create, update, delete)
  - Error handling
  - Cache invalidation

## Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui
```

## Coverage Goals

- **Overall**: >90%
- **Components**: >95%
- **Hooks**: >90%
- **Utils**: >85%

## Test Patterns

### Component Testing

```tsx
import { render, screen } from '@/tests/utils/test-utils';
import { ComponentName } from '../ComponentName';

describe('ComponentName', () => {
  it('renders correctly', () => {
    render(<ComponentName />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Hook Testing

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { useCustomHook } from '../useCustomHook';

describe('useCustomHook', () => {
  it('returns expected data', async () => {
    const { result } = renderHook(() => useCustomHook());

    await waitFor(() => {
      expect(result.current.data).toBeDefined();
    });
  });
});
```

### API Mocking with MSW

```tsx
import { rest } from 'msw';
import { server } from '@/tests/mocks/server';

// Override default handler for specific test
server.use(
  rest.get('/api/endpoint', (req, res, ctx) => {
    return res(ctx.json({ custom: 'response' }));
  })
);
```

## Best Practices

1. **Use custom render**: Always use the custom render function that includes
   providers
2. **Mock at the network level**: Use MSW for API mocking instead of module
   mocks
3. **Test user interactions**: Focus on how users interact with components
4. **Avoid implementation details**: Test behavior, not implementation
5. **Use data-testid sparingly**: Prefer accessible queries (role, label, text)
6. **Keep tests focused**: One test should verify one behavior
7. **Use proper async handling**: Always use waitFor for async operations

## Debugging Tests

1. **Console logs**: Add console.log in test to debug
2. **Debug helper**: Use screen.debug() to see current DOM
3. **Vitest UI**: Run `npm run test:ui` for interactive debugging
4. **Coverage report**: Check `coverage/index.html` for detailed coverage
