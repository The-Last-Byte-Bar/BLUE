import React from 'react';
import styled from 'styled-components';

const CardContainer = styled.div`
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 10px;
  box-shadow: 0 6px 0 var(--island-outline), 0 10px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 2px solid var(--island-outline);
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 0 var(--island-outline), 0 14px 24px rgba(0, 0, 0, 0.15);
  }
  
  /* Wind Waker-style cel-shaded border effect */
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: linear-gradient(to bottom, rgba(255, 255, 255, 0.8), transparent);
  }
  
  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 10px;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.1), transparent);
    border-radius: 0 0 10px 10px;
  }
`;

const Title = styled.h2`
  color: var(--hero-green);
  position: relative;
  padding-bottom: 0.5rem;
  margin-top: 0.5rem;
  
  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 80px;
    height: 3px;
    background-color: var(--hero-green);
    border-radius: 3px;
  }
`;

// Optional decorative element to add Wind Waker charm
const WaveDecoration = styled.div`
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 30px;
  height: 30px;
  opacity: 0.4;
  
  &::before {
    content: "〰";
    font-size: 24px;
    color: var(--deep-blue);
  }
`;

const Card = ({ title, children }) => {
  return (
    <CardContainer>
      <WaveDecoration />
      {title && <Title>{title}</Title>}
      {children}
    </CardContainer>
  );
};

export default Card; 