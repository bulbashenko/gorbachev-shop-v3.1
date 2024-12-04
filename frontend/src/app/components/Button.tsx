// src/components/Button.tsx
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ children, ...props }) => {
  return (
    <button
      {...props}
      className={`relative px-6 py-3 font-medium bg-[#030303] text-[#EDEDED] dark:text-[#030303] dark:bg-[#EDEDED] rounded-[6px] dark:shadow-inner hover:shadow-lg focus:outline-none ${props.className}`}
      style={{
        boxShadow: 'inset 0px -4px 9.8px rgba(0, 0, 0, 0.25)',
      }}
    >
      {children}
    </button>
  );
};

export default Button;
