/**
 * Checkbox component for consent forms.
 */

import React from 'react';
import './Checkbox.css';

interface CheckboxProps {
  label: string | React.ReactNode;
  checked: boolean;
  onChange: (checked: boolean) => void;
  required?: boolean;
  error?: string;
  disabled?: boolean;
}

const Checkbox: React.FC<CheckboxProps> = ({
  label,
  checked,
  onChange,
  required = false,
  error,
  disabled = false
}) => {
  return (
    <div className="checkbox-wrapper">
      <label className={`checkbox-label ${error ? 'checkbox-error' : ''}`}>
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          required={required}
          disabled={disabled}
          className="checkbox-input"
        />
        <span className="checkbox-text">
          {label}
          {required && <span className="checkbox-required">*</span>}
        </span>
      </label>
      {error && <span className="checkbox-error-message">{error}</span>}
    </div>
  );
};

export default Checkbox;

