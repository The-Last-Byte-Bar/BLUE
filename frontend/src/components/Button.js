import React from 'react';
import styled, { css } from 'styled-components';

// Base button styles with Wind Waker aesthetics
const ButtonBase = css`
  display: inline-block;
  font-family: inherit;
  font-size: 1rem;
  font-weight: bold;
  padding: 0.75rem 1.5rem;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 0;
  
  &:hover {
    transform: translateY(2px);
    box-shadow: 0 2px 0;
  }
  
  &:active {
    transform: translateY(4px);
    box-shadow: none;
  }
  
  /* Cel-shaded light effect */
  &::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 50%;
    background: linear-gradient(to bottom, rgba(255, 255, 255, 0.2), transparent);
    pointer-events: none;
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
    box-shadow: none;
  }
`;

const PrimaryButton = styled.button`
  ${ButtonBase}
  background-color: var(--hero-green);
  color: white;
  border-color: var(--forest-green);
  box-shadow-color: var(--forest-green);
`;

const SecondaryButton = styled.button`
  ${ButtonBase}
  background-color: var(--sand-yellow);
  color: var(--dark-text);
  border-color: var(--wood-brown);
  box-shadow-color: var(--wood-brown);
`;

const DangerButton = styled.button`
  ${ButtonBase}
  background-color: var(--sunset-orange);
  color: white;
  border-color: #D2691E;
  box-shadow-color: #D2691E;
`;

const Button = ({ variant = 'primary', children, ...props }) => {
  switch (variant) {
    case 'secondary':
      return <SecondaryButton {...props}>{children}</SecondaryButton>;
    case 'danger':
      return <DangerButton {...props}>{children}</DangerButton>;
    case 'primary':
    default:
      return <PrimaryButton {...props}>{children}</PrimaryButton>;
  }
};

export default Button; 