import type { Meta, StoryObj } from '@storybook/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

import { Breadcrumbs } from './Breadcrumbs';

// Create a mock query client for stories
const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const meta = {
  title: 'Components/Common/Breadcrumbs',
  component: Breadcrumbs,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Breadcrumbs component provides hierarchical navigation showing the user\'s current location within the application. It supports dynamic segments that fetch actual names from the API.',
      },
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story, context) => {
      const initialPath = context.args.path || '/dashboard';
      return (
        <QueryClientProvider client={mockQueryClient}>
          <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
              <Route path="*" element={<Story />} />
            </Routes>
          </MemoryRouter>
        </QueryClientProvider>
      );
    },
  ],
  argTypes: {
    className: {
      control: 'text',
      description: 'Additional CSS classes for styling',
    },
  },
} satisfies Meta<typeof Breadcrumbs>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Dashboard: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the dashboard page. No breadcrumbs are shown as it\'s the root page.',
      },
    },
  },
};

export const ProgramsList: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the programs listing page showing simple navigation.',
      },
    },
  },
};

export const NewProgram: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs when creating a new program, showing nested navigation.',
      },
    },
  },
};

export const ProgramDetails: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on a program details page with dynamic ID. In production, this would fetch the actual program name.',
      },
    },
  },
};

export const EditProgram: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs when editing a program, showing the full hierarchy with dynamic segments.',
      },
    },
  },
};

export const ProgramCourseReorder: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs for the course reordering page within a program.',
      },
    },
  },
};

export const BeneficiariesList: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the beneficiaries listing page.',
      },
    },
  },
};

export const BeneficiaryDetails: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on a beneficiary details page. In production, this would show the beneficiary\'s actual name.',
      },
    },
  },
};

export const CoursesList: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the courses listing page.',
      },
    },
  },
};

export const CourseEdit: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs when editing a course with dynamic course name.',
      },
    },
  },
};

export const CourseSessionNew: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs when creating a new session within a course.',
      },
    },
  },
};

export const EvaluationsList: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the evaluations listing page.',
      },
    },
  },
};

export const TakeEvaluation: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs when taking an evaluation.',
      },
    },
  },
};

export const EvaluationResults: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs showing evaluation results with multiple dynamic segments.',
      },
    },
  },
};

export const LearningPaths: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the learning paths page.',
      },
    },
  },
};

export const LearningPathDetails: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on a learning path details page.',
      },
    },
  },
};

export const Reports: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the reports page.',
      },
    },
  },
};

export const MyDevelopmentReport: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs for the My Development report page.',
      },
    },
  },
};

export const CoachDashboard: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the coach dashboard.',
      },
    },
  },
};

export const StudentProfile: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on a student profile page viewed by a coach.',
      },
    },
  },
};

export const Settings: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the settings page.',
      },
    },
  },
};

export const Profile: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs on the user profile page.',
      },
    },
  },
};

export const WithCustomStyling: Story = {
  args: {},  parameters: {
    docs: {
      description: {
        story: 'Breadcrumbs with custom styling applied via className prop.',
      },
    },
  },
};

export const DarkMode: Story = {
  args: {},  parameters: {
    backgrounds: { default: 'dark' },
    docs: {
      description: {
        story: 'Breadcrumbs in dark mode showing proper contrast and styling.',
      },
    },
  },
  decorators: [
    (Story, context) => (
      <div className="dark bg-gray-900 p-4">
        {context.decorators[0](Story, context)}
      </div>
    ),
  ],
};