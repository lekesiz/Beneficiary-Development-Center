import type { Meta, StoryObj } from '@storybook/react';

import { FormSkeleton } from '@/components/common/FormSkeleton';

const meta = {
  title: 'Components/FormSkeleton',
  component: FormSkeleton,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'A skeleton loader for forms that displays placeholder content while form data is loading.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    sections: {
      control: { type: 'number', min: 1, max: 5 },
      description: 'Number of form sections',
    },
    fieldsPerSection: {
      control: { type: 'number', min: 1, max: 8 },
      description: 'Number of fields per section',
    },
    showHeader: {
      control: 'boolean',
      description: 'Whether to show the header skeleton',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
  },
} satisfies Meta<typeof FormSkeleton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    sections: 3,
    fieldsPerSection: 4,
    showHeader: true,
  },
};

export const SimpleForm: Story = {
  args: {
    sections: 1,
    fieldsPerSection: 3,
    showHeader: true,
  },
};

export const ComplexForm: Story = {
  args: {
    sections: 5,
    fieldsPerSection: 6,
    showHeader: true,
  },
};

export const NoHeader: Story = {
  args: {
    sections: 2,
    fieldsPerSection: 4,
    showHeader: false,
  },
};

export const ProfileForm: Story = {
  name: 'Profile Form Example',
  args: {
    sections: 2,
    fieldsPerSection: 5,
    showHeader: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a user profile form with personal information and settings sections.',
      },
    },
  },
};

export const RegistrationForm: Story = {
  name: 'Registration Form Example',
  args: {
    sections: 3,
    fieldsPerSection: 4,
    showHeader: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a multi-step registration form with account details, personal info, and preferences.',
      },
    },
  },
};

export const SettingsForm: Story = {
  name: 'Settings Form Example',
  args: {
    sections: 4,
    fieldsPerSection: 3,
    showHeader: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for an application settings form with multiple configuration sections.',
      },
    },
  },
};

export const WizardForm: Story = {
  name: 'Wizard Form Example',
  args: {
    sections: 1,
    fieldsPerSection: 6,
    showHeader: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a single-step wizard form that loads data dynamically.',
      },
    },
  },
};