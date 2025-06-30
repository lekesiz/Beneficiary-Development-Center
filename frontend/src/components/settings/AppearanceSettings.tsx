import React from 'react';
import { Sun, Moon, Monitor, Palette, Type, Circle, Check } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/Select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';

type Theme = 'light' | 'dark' | 'system';
type AccentColor = 'blue' | 'purple' | 'green' | 'red' | 'orange';
type FontSize = 'small' | 'medium' | 'large';

interface AppearancePreferences {
  accentColor: AccentColor;
  fontSize: FontSize;
  reducedMotion: boolean;
  highContrast: boolean;
}

const accentColors: { value: AccentColor; label: string; class: string }[] = [
  { value: 'blue', label: 'Blue', class: 'bg-blue-600' },
  { value: 'purple', label: 'Purple', class: 'bg-purple-600' },
  { value: 'green', label: 'Green', class: 'bg-green-600' },
  { value: 'red', label: 'Red', class: 'bg-red-600' },
  { value: 'orange', label: 'Orange', class: 'bg-orange-600' },
];

export const AppearanceSettings: React.FC = () => {
  const { theme, setTheme } = useTheme();
  
  // Local state for other preferences (would be stored in localStorage or backend)
  const [preferences, setPreferences] = React.useState<AppearancePreferences>(() => {
    const saved = localStorage.getItem('bdc-appearance-preferences');
    return saved ? JSON.parse(saved) : {
      accentColor: 'blue',
      fontSize: 'medium',
      reducedMotion: false,
      highContrast: false,
    };
  });

  const updatePreference = <K extends keyof AppearancePreferences>(
    key: K,
    value: AppearancePreferences[K]
  ) => {
    const newPreferences = { ...preferences, [key]: value };
    setPreferences(newPreferences);
    localStorage.setItem('bdc-appearance-preferences', JSON.stringify(newPreferences));
    
    // Apply changes to document
    const root = document.documentElement;
    
    // Apply accent color
    if (key === 'accentColor') {
      root.setAttribute('data-accent', value as string);
    }
    
    // Apply font size
    if (key === 'fontSize') {
      root.setAttribute('data-font-size', value as string);
    }
    
    // Apply reduced motion
    if (key === 'reducedMotion') {
      root.setAttribute('data-reduced-motion', value ? 'true' : 'false');
    }
    
    // Apply high contrast
    if (key === 'highContrast') {
      root.setAttribute('data-high-contrast', value ? 'true' : 'false');
    }
  };

  React.useEffect(() => {
    // Apply all preferences on mount
    const root = document.documentElement;
    root.setAttribute('data-accent', preferences.accentColor);
    root.setAttribute('data-font-size', preferences.fontSize);
    root.setAttribute('data-reduced-motion', preferences.reducedMotion.toString());
    root.setAttribute('data-high-contrast', preferences.highContrast.toString());
  }, []);

  return (
    <div className="space-y-6">
      {/* Theme Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Theme</CardTitle>
          <CardDescription>
            Choose how BDC looks to you. Select a single theme, or sync with your system and automatically switch between day and night themes.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <RadioGroup value={theme} onValueChange={(value) => setTheme(value as Theme)}>
            <div className="grid gap-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <RadioGroupItem value="light" id="light" />
                <div className="flex items-center space-x-3 flex-1">
                  <div className="w-10 h-10 rounded-lg bg-white border border-gray-200 flex items-center justify-center">
                    <Sun className="w-5 h-5 text-yellow-500" />
                  </div>
                  <div>
                    <Label htmlFor="light" className="text-base font-medium cursor-pointer">
                      Light
                    </Label>
                    <p className="text-sm text-muted-foreground">Bright theme for daytime use</p>
                  </div>
                </div>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <RadioGroupItem value="dark" id="dark" />
                <div className="flex items-center space-x-3 flex-1">
                  <div className="w-10 h-10 rounded-lg bg-gray-900 border border-gray-700 flex items-center justify-center">
                    <Moon className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <Label htmlFor="dark" className="text-base font-medium cursor-pointer">
                      Dark
                    </Label>
                    <p className="text-sm text-muted-foreground">Dark theme for night time use</p>
                  </div>
                </div>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <RadioGroupItem value="system" id="system" />
                <div className="flex items-center space-x-3 flex-1">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-white to-gray-900 border border-gray-300 flex items-center justify-center">
                    <Monitor className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <Label htmlFor="system" className="text-base font-medium cursor-pointer">
                      System
                    </Label>
                    <p className="text-sm text-muted-foreground">Sync with your system preferences</p>
                  </div>
                </div>
              </label>
            </div>
          </RadioGroup>
        </CardContent>
      </Card>

      {/* Accent Color */}
      <Card>
        <CardHeader>
          <CardTitle>Accent Color</CardTitle>
          <CardDescription>
            Choose your preferred accent color for buttons, links, and other interactive elements.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            {accentColors.map((color) => (
              <button
                key={color.value}
                onClick={() => updatePreference('accentColor', color.value)}
                className={`
                  relative w-12 h-12 rounded-full ${color.class} 
                  hover:scale-110 transition-transform duration-150
                  focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-background
                `}
                aria-label={`Select ${color.label} accent color`}
              >
                {preferences.accentColor === color.value && (
                  <Check className="w-6 h-6 text-white absolute inset-0 m-auto" />
                )}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Font Size */}
      <Card>
        <CardHeader>
          <CardTitle>Font Size</CardTitle>
          <CardDescription>
            Adjust the default font size for better readability.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Select
              value={preferences.fontSize}
              onChange={(e) => updatePreference('fontSize', e.target.value as FontSize)}
              className="w-48"
              options={[
                { value: 'small', label: 'Small' },
                { value: 'medium', label: 'Medium (Default)' },
                { value: 'large', label: 'Large' }
              ]}
            />

            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm">Preview text:</p>
              <p className={`
                mt-2
                ${preferences.fontSize === 'small' && 'text-sm'}
                ${preferences.fontSize === 'medium' && 'text-base'}
                ${preferences.fontSize === 'large' && 'text-lg'}
              `}>
                The quick brown fox jumps over the lazy dog. This is how text will appear with your selected font size.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Accessibility */}
      <Card>
        <CardHeader>
          <CardTitle>Accessibility</CardTitle>
          <CardDescription>
            Make BDC more comfortable to use with accessibility preferences.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="reduced-motion" className="text-base">
                Reduce motion
              </Label>
              <p className="text-sm text-muted-foreground">
                Minimize animations and transitions
              </p>
            </div>
            <Switch
              id="reduced-motion"
              checked={preferences.reducedMotion}
              onCheckedChange={(checked) => updatePreference('reducedMotion', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="high-contrast" className="text-base">
                High contrast
              </Label>
              <p className="text-sm text-muted-foreground">
                Increase contrast for better visibility
              </p>
            </div>
            <Switch
              id="high-contrast"
              checked={preferences.highContrast}
              onCheckedChange={(checked) => updatePreference('highContrast', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Preview Section */}
      <Card>
        <CardHeader>
          <CardTitle>Preview</CardTitle>
          <CardDescription>
            See how your appearance settings look in action.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 p-4 border rounded-lg">
            <h4 className="font-semibold">Sample Interface</h4>
            <p className="text-muted-foreground">
              This is how your content will appear with the current settings.
            </p>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                Primary Button
              </button>
              <button className="px-4 py-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md transition-colors">
                Secondary Button
              </button>
            </div>
            <div className="flex items-center gap-2">
              <Circle className="w-4 h-4 text-green-600" fill="currentColor" />
              <span className="text-sm">Online status indicator</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};