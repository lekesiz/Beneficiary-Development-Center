import * as React from 'react';

import { Input } from './Form';

interface DatePickerProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const DatePicker = React.forwardRef<HTMLInputElement, DatePickerProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium leading-none">
            {label}
            {props.required && <span className="text-destructive ml-1">*</span>}
          </label>
        )}
        <Input {...props} type="date" className={className} error={!!error} ref={ref} />
        {error && <p className="text-sm text-destructive">{error}</p>}
      </div>
    );
  }
);

DatePicker.displayName = 'DatePicker';

export default DatePicker;
