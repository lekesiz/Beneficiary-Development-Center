import { User, Bell, Shield, Palette } from 'lucide-react';
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { NotificationSettings } from '@/components/settings/NotificationSettings';
import { AppearanceSettings } from '@/components/settings/AppearanceSettings';
import { ProfileSettings } from '@/components/settings/ProfileSettings';
import { SecuritySettings } from '@/components/settings/SecuritySettings';
import { Card } from '@/components/ui/Card';

interface Tab {
  id: string;
  label: string;
  icon: React.ElementType;
  component: React.ComponentType;
}

const ProfileTab: React.FC = () => {
  return <ProfileSettings />;
};

const SecurityTab: React.FC = () => {
  return <SecuritySettings />;
};

const AppearanceTab: React.FC = () => {
  return <AppearanceSettings />;
};

const tabs: Tab[] = [
  {
    id: 'profile',
    label: 'Profile',
    icon: User,
    component: ProfileTab,
  },
  {
    id: 'notifications',
    label: 'Notifications',
    icon: Bell,
    component: NotificationSettings,
  },
  {
    id: 'security',
    label: 'Security',
    icon: Shield,
    component: SecurityTab,
  },
  {
    id: 'appearance',
    label: 'Appearance',
    icon: Palette,
    component: AppearanceTab,
  },
];

export default function Settings() {
  const navigate = useNavigate();
  const location = useLocation();

  // Get initial tab from URL or default to 'profile'
  const getInitialTab = () => {
    const hash = location.hash.replace('#', '');
    return tabs.find((tab) => tab.id === hash) ? hash : 'profile';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab());

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    navigate(`#${tabId}`, { replace: true });
  };

  const ActiveComponent = tabs.find((tab) => tab.id === activeTab)?.component || ProfileTab;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">Manage your account settings and preferences</p>
      </div>

      <div className="grid grid-cols-12 gap-8">
        {/* Sidebar Navigation */}
        <div className="col-span-12 md:col-span-3">
          <nav className="space-y-1" aria-label="Settings navigation">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`
                    w-full flex items-center space-x-3 px-3 py-2 text-sm font-medium rounded-md
                    transition-colors duration-150 ease-in-out
                    ${
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                  aria-current={activeTab === tab.id ? 'page' : undefined}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content Area */}
        <div className="col-span-12 md:col-span-9">
          <ActiveComponent />
        </div>
      </div>
    </div>
  );
}
