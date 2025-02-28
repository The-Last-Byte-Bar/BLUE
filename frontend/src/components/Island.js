import React from 'react';
import styled, { keyframes } from 'styled-components';
import { Link } from 'react-router-dom';

// Animations for the island
const floatAnimation = keyframes`
  0% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
  100% { transform: translateY(0); }
`;

const glowAnimation = keyframes`
  0% { box-shadow: 0 0 5px rgba(255, 255, 0, 0.3); }
  50% { box-shadow: 0 0 15px rgba(255, 255, 0, 0.6); }
  100% { box-shadow: 0 0 5px rgba(255, 255, 0, 0.3); }
`;

const waveAnimation = keyframes`
  0% { transform: translateX(0) translateY(0); }
  25% { transform: translateX(5px) translateY(2px); }
  50% { transform: translateX(0) translateY(0); }
  75% { transform: translateX(-5px) translateY(2px); }
  100% { transform: translateX(0) translateY(0); }
`;

// Main island container
const IslandContainer = styled(Link)`
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  margin: 1rem;
  transition: transform 0.3s ease;
  animation: ${floatAnimation} ${props => 3 + Math.random() * 2}s infinite ease-in-out;
  animation-delay: ${props => Math.random() * 2}s;
  cursor: pointer;
  
  &:hover {
    transform: scale(1.1);
    z-index: 10;
    
    .island-body {
      animation: ${glowAnimation} 1.5s infinite;
    }
    
    .island-label {
      opacity: 1;
      transform: translateY(0);
    }
    
    .island-water {
      animation: ${waveAnimation} 2s infinite ease-in-out;
    }
  }
`;

// The actual island shape
const IslandBody = styled.div`
  width: ${props => props.size || 100}px;
  height: ${props => Math.max(props.size * 0.4, 40) || 40}px;
  background-color: var(--sand-yellow);
  border: 3px solid var(--island-outline);
  border-radius: 50%;
  position: relative;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  image-rendering: pixelated;
  
  /* Mountain/terrain features on the island */
  &::before {
    content: "";
    position: absolute;
    top: -${props => Math.max(props.size * 0.3, 20)}px;
    left: ${props => props.size * 0.3 || 30}px;
    width: ${props => Math.max(props.size * 0.4, 20)}px;
    height: ${props => Math.max(props.size * 0.5, 30)}px;
    background-color: ${props => 
      props.$featureType === 'transaction' ? 'var(--forest-green)' : 
      props.$featureType === 'block' ? 'var(--wood-brown)' : 
      props.$featureType === 'token' ? 'var(--sunset-orange)' : 
      'var(--forest-green)'
    };
    border: 3px solid var(--island-outline);
    border-radius: 50% 50% 0 0;
    z-index: 1;
  }
  
  /* Optional second feature */
  &::after {
    content: ${props => props.$hasSecondFeature ? "''" : 'none'};
    position: absolute;
    top: -${props => Math.max(props.size * 0.15, 15)}px;
    right: ${props => props.size * 0.2 || 20}px;
    width: ${props => Math.max(props.size * 0.25, 15)}px;
    height: ${props => Math.max(props.size * 0.25, 15)}px;
    background-color: var(--hero-green);
    border: 2px solid var(--island-outline);
    border-radius: 50% 50% 0 0;
    z-index: 0;
  }
`;

// Water ripples around the island
const IslandWater = styled.div`
  position: absolute;
  bottom: -10px;
  left: -10px;
  right: -10px;
  height: 20px;
  background: radial-gradient(
    ellipse at center,
    rgba(173, 216, 230, 0.7) 0%,
    rgba(173, 216, 230, 0) 70%
  );
  border-radius: 50%;
  z-index: -1;
  opacity: 0.7;
`;

// Label for the island
const IslandLabel = styled.div`
  margin-top: 15px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  color: var(--dark-text);
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  border: 2px solid var(--island-outline);
  opacity: 0.8;
  transform: translateY(5px);
  transition: all 0.3s ease;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

// Optional treasure icon based on feature type
const Treasure = styled.div`
  position: absolute;
  top: -5px;
  right: ${props => props.size * 0.2 || 20}px;
  width: 20px;
  height: 15px;
  background-color: #D4AF37; /* Gold color */
  border: 2px solid #8B4513;
  border-radius: 3px;
  z-index: 2;
  
  /* Treasure chest lid */
  &::before {
    content: "";
    position: absolute;
    top: -5px;
    left: -2px;
    width: 20px;
    height: 5px;
    background-color: #FFD700;
    border: 2px solid #8B4513;
    border-bottom: none;
    border-radius: 3px 3px 0 0;
  }
  
  /* Lock on chest */
  &::after {
    content: "";
    position: absolute;
    top: 5px;
    left: 7px;
    width: 6px;
    height: 6px;
    background-color: #8B4513;
    border-radius: 50%;
  }
`;

// Island component representing a blockchain feature
const Island = ({ 
  to, 
  size = 100, 
  label, 
  featureType = 'block', 
  hasTreasure = false,
  hasSecondFeature = false,
  onClick
}) => {
  return (
    <IslandContainer to={to} onClick={onClick}>
      <IslandBody 
        className="island-body" 
        size={size} 
        $featureType={featureType}
        $hasSecondFeature={hasSecondFeature}
      >
        {hasTreasure && <Treasure size={size} />}
        <IslandWater className="island-water" />
      </IslandBody>
      <IslandLabel className="island-label">{label}</IslandLabel>
    </IslandContainer>
  );
};

export default Island; 