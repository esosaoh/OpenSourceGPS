import React from 'react';

interface ResetButtonProps {
  onReset: () => void;
  className?: string;
}

const ResetButton: React.FC<ResetButtonProps> = ({ onReset, className }) => {
  return (
    <button
      onClick={onReset}
      className={`mt-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors ${className || ''}`}
    >
      Ask Another Question
    </button>
  );
};

export default ResetButton;
