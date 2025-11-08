/**
 * Textarea component for long text input.
 */

import React from 'react';
import './Textarea.css';

interface TextareaProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  error?: string;
  disabled?: boolean;
  rows?: number;
  maxLength?: number;
}

const Textarea: React.FC<TextareaProps> = ({
  label,
  value,
  onChange,
  placeholder,
  required = false,
  error,
  disabled = false,
  rows = 6,
  maxLength
}) => {
  return (
    <div className="textarea-wrapper">
      <label className="textarea-label">
        {label}
        {required && <span className="textarea-required">*</span>}
        {maxLength && (
          <span className="textarea-counter">
            {value.length} / {maxLength}
          </span>
        )}
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        rows={rows}
        maxLength={maxLength}
        className={`textarea-field ${error ? 'textarea-error' : ''}`}
      />
      {error && <span className="textarea-error-message">{error}</span>}
    </div>
  );
};

export default Textarea;

