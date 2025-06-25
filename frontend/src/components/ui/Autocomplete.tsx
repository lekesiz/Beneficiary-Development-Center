import * as React from 'react';
import { useState } from 'react';

import { cn } from '@/lib/utils';

import { Input } from './Form';


interface AutocompleteOption {
  value: string | number;
  label: string;
}

interface AutocompleteProps {
  label?: string;
  error?: string;
  value?: string | number;
  onChange: (value: string | number | undefined) => void;
  options: AutocompleteOption[];
  placeholder?: string;
  disabled?: boolean;
}

export const Autocomplete: React.FC<AutocompleteProps> = ({
  label,
  error,
  value,
  onChange,
  options,
  placeholder,
  disabled,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');

  const selectedOption = options.find((option) => option.value === value);
  const displayValue = selectedOption ? selectedOption.label : '';

  const filteredOptions = options.filter((option) =>
    option.label.toLowerCase().includes(searchValue.toLowerCase())
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(e.target.value);
    setIsOpen(true);
  };

  const handleOptionSelect = (option: AutocompleteOption) => {
    onChange(option.value);
    setSearchValue('');
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(undefined);
    setSearchValue('');
    setIsOpen(false);
  };

  return (
    <div className="relative space-y-2">
      {label && (
        <label className="text-sm font-medium leading-none">{label}</label>
      )}

      <div className="relative">
        <Input
          value={isOpen ? searchValue : displayValue}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          error={!!error}
          disabled={disabled}
          autoComplete="off"
        />

        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>

      {isOpen && filteredOptions.length > 0 && (
        <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {filteredOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleOptionSelect(option)}
              className={cn(
                'w-full px-3 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none',
                option.value === value && 'bg-blue-50'
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
};

export default Autocomplete;
