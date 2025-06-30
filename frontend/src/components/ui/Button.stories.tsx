import type { Meta, StoryObj } from '@storybook/react';
import { Plus, Download, Edit, Trash2, Eye } from 'lucide-react';

import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Uygulamada kullanılan temel buton bileşeni. Farklı varyantlar, boyutlar ve durumları destekler.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger', 'success', 'warning', 'ghost', 'outline', 'link'],
      description: 'Butonun görsel stili',
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Butonun boyutu',
    },
    loading: {
      control: 'boolean',
      description: 'Yüklenme durumunu gösterir',
    },
    disabled: {
      control: 'boolean',
      description: 'Butonu devre dışı bırakır',
    },
    loadingText: {
      control: 'text',
      description: 'Yüklenme sırasında gösterilecek metin',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Primary Button
export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
    size: 'md',
  },
};

// Secondary Button
export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
    size: 'md',
  },
};

// Danger Button
export const Danger: Story = {
  args: {
    children: 'Delete Item',
    variant: 'danger',
    size: 'md',
  },
};

// Success Button
export const Success: Story = {
  args: {
    children: 'Save Changes',
    variant: 'success',
    size: 'md',
  },
};

// Warning Button
export const Warning: Story = {
  args: {
    children: 'Warning Action',
    variant: 'warning',
    size: 'md',
  },
};

// Ghost Button
export const Ghost: Story = {
  args: {
    children: 'Ghost Button',
    variant: 'ghost',
    size: 'md',
  },
};

// Outline Button
export const Outline: Story = {
  args: {
    children: 'Outline Button',
    variant: 'outline',
    size: 'md',
  },
};

// Link Button
export const Link: Story = {
  args: {
    children: 'Link Button',
    variant: 'link',
    size: 'md',
  },
};

// Loading State
export const Loading: Story = {
  args: {
    children: 'Loading Button',
    variant: 'primary',
    size: 'md',
    loading: true,
  },
};

// Loading with Custom Text
export const LoadingWithCustomText: Story = {
  args: {
    children: 'Save Data',
    variant: 'primary',
    size: 'md',
    loading: true,
    loadingText: 'Kayıt ediliyor...',
  },
};

// Disabled State
export const Disabled: Story = {
  args: {
    children: 'Disabled Button',
    variant: 'primary',
    size: 'md',
    disabled: true,
  },
};

// With Left Icon
export const WithLeftIcon: Story = {
  args: {
    children: 'Yeni Ekle',
    variant: 'primary',
    size: 'md',
    leftIcon: <Plus size={16} />,
  },
};

// With Right Icon
export const WithRightIcon: Story = {
  args: {
    children: 'İndir',
    variant: 'secondary',
    size: 'md',
    rightIcon: <Download size={16} />,
  },
};

// Size Variations
export const SizeVariations: Story = {
  render: () => (
    <div className="flex items-center gap-4 flex-wrap">
      <Button size="xs" variant="primary">
        Extra Small
      </Button>
      <Button size="sm" variant="primary">
        Small
      </Button>
      <Button size="md" variant="primary">
        Medium
      </Button>
      <Button size="lg" variant="primary">
        Large
      </Button>
      <Button size="xl" variant="primary">
        Extra Large
      </Button>
    </div>
  ),
};

// All Variants
export const AllVariants: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-4 max-w-md">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="danger">Danger</Button>
      <Button variant="success">Success</Button>
      <Button variant="warning">Warning</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="link">Link</Button>
    </div>
  ),
};

// Action Buttons
export const ActionButtons: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <Button variant="primary" size="sm" leftIcon={<Plus size={14} />}>
        Yeni
      </Button>
      <Button variant="ghost" size="sm">
        <Edit size={14} />
      </Button>
      <Button variant="ghost" size="sm">
        <Eye size={14} />
      </Button>
      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-800">
        <Trash2 size={14} />
      </Button>
    </div>
  ),
};

// Form Buttons
export const FormButtons: Story = {
  render: () => (
    <div className="flex items-center justify-end gap-3">
      <Button variant="outline">İptal</Button>
      <Button variant="primary">Kaydet</Button>
    </div>
  ),
};

// Loading States
export const LoadingStates: Story = {
  render: () => (
    <div className="flex items-center gap-4 flex-wrap">
      <Button variant="primary" loading>
        Primary Loading
      </Button>
      <Button variant="secondary" loading>
        Secondary Loading
      </Button>
      <Button variant="danger" loading loadingText="Siliniyor...">
        Delete Loading
      </Button>
      <Button variant="success" loading loadingText="Kaydediliyor...">
        Save Loading
      </Button>
    </div>
  ),
};
