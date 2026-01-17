import React from 'react';

interface GradientCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
}

const GradientCard = React.forwardRef<HTMLDivElement, GradientCardProps>(
  ({ className = '', children, hover = false, ...props }, ref) => {
    const baseClasses = `
      relative rounded-2xl bg-[#1a1625] p-6 shadow-card border border-white/10
      backdrop-blur-sm
      ${hover ? 'transition-all duration-300 hover:shadow-soft hover:border-primary/20 hover:-translate-y-0.5' : ''}
      ${className}
    `.trim().replace(/\s+/g, ' ');

    return (
      <div
        ref={ref}
        className={baseClasses}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GradientCard.displayName = 'GradientCard';

export default GradientCard;
