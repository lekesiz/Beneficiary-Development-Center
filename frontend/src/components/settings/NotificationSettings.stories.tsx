import type { Meta, StoryObj } from '@storybook/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { rest } from 'msw';

import { NotificationSettings } from './NotificationSettings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const meta = {
  title: 'Components/Settings/NotificationSettings',
  component: NotificationSettings,
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <div className="max-w-4xl mx-auto p-6">
          <Story />
        </div>
      </QueryClientProvider>
    ),
  ],
  parameters: {
    msw: {
      handlers: [
        rest.get('/api/v1/users/me/preferences', (req, res, ctx) => {
          return res(
            ctx.json({
              preferences: {
                notifications: {
                  email: {
                    new_message: true,
                    appointment_reminder: true,
                    evaluation_completed: false,
                    course_enrollment: true,
                    program_update: true,
                  },
                  in_app: {
                    new_message: true,
                    appointment_reminder: true,
                    evaluation_completed: true,
                    course_enrollment: true,
                    program_update: true,
                  },
                },
              },
            })
          );
        }),
        rest.put('/api/v1/users/me/preferences', (req, res, ctx) => {
          return res(
            ctx.json({
              message: 'Preferences updated successfully',
              preferences: req.body,
            })
          );
        }),
      ],
    },
  },
} satisfies Meta<typeof NotificationSettings>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Loading: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/api/v1/users/me/preferences', (req, res, ctx) => {
          return res(ctx.delay('infinite'));
        }),
      ],
    },
  },
};

export const AllEnabled: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/api/v1/users/me/preferences', (req, res, ctx) => {
          return res(
            ctx.json({
              preferences: {
                notifications: {
                  email: {
                    new_message: true,
                    appointment_reminder: true,
                    evaluation_completed: true,
                    course_enrollment: true,
                    program_update: true,
                  },
                  in_app: {
                    new_message: true,
                    appointment_reminder: true,
                    evaluation_completed: true,
                    course_enrollment: true,
                    program_update: true,
                  },
                },
              },
            })
          );
        }),
      ],
    },
  },
};

export const AllDisabled: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/api/v1/users/me/preferences', (req, res, ctx) => {
          return res(
            ctx.json({
              preferences: {
                notifications: {
                  email: {
                    new_message: false,
                    appointment_reminder: false,
                    evaluation_completed: false,
                    course_enrollment: false,
                    program_update: false,
                  },
                  in_app: {
                    new_message: false,
                    appointment_reminder: false,
                    evaluation_completed: false,
                    course_enrollment: false,
                    program_update: false,
                  },
                },
              },
            })
          );
        }),
      ],
    },
  },
};

export const Error: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/api/v1/users/me/preferences', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ message: 'Server error' }));
        }),
      ],
    },
  },
};
