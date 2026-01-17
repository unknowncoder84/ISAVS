import React from 'react';

interface GradientButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  size?: 'default' | 'lg' | 'xl';
  fullWidth?: boolean;
}

const GradientButton = React.forwardRef<HTMLButtonElement, GradientButtonProps>(
  ({ className = '', children, size = 'default', fullWidth = false, disabled, ...props }, ref) => {
    const sizeClasses = {
      default: 'h-11 px-6 text-sm',
      lg: 'h-12 px-8 text-base',
      xl: 'h-14 px-10 text-base font-semibold',
    };

    const baseClasses = `
      relative inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-300
      gradient-primary text-white
      shadow-soft hover:shadow-glow
      hover:scale-[1.02] active:scale-[0.98]
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2
      disabled:pointer-events-none disabled:opacity-50
      ${sizeClasses[size]}
      ${fullWidth ? 'w-full' : ''}
      ${className}
    `.trim().replace(/\s+/g, ' ');

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={baseClasses}
        {...props}
      >
        {children}
      </button>
    );
  }
);

GradientButton.displayName = 'GradientButton';

export default GradientButton;
