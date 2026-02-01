import React from 'react';

const Spinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-12 h-12 border-4'
  };

  return (
    <div 
      className={`${sizeClasses[size]} border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin ${className}`}
    />
  );
};

export default Spinner;
