import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

// Define keyframe animations
const sharkSwim = keyframes`
  0% { transform: translateX(0) rotate(0deg); }
  25% { transform: translateX(10px) rotate(5deg); }
  50% { transform: translateX(0) rotate(0deg); }
  75% { transform: translateX(-10px) rotate(-5deg); }
  100% { transform: translateX(0) rotate(0deg); }
`;

const hairBob = keyframes`
  0% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
  100% { transform: translateY(0); }
`;

const spikesBob = keyframes`
  0% { transform: rotate(-5deg) translateY(0); }
  50% { transform: rotate(-5deg) translateY(-2px); }
  100% { transform: rotate(-5deg) translateY(0); }
`;

const finWave = keyframes`
  0% { transform: rotate(0deg); }
  50% { transform: rotate(15deg); }
  100% { transform: rotate(0deg); }
`;

const bubbleFloat = keyframes`
  0% { 
    transform: translateY(0) scale(1);
    opacity: 0; 
  }
  50% { 
    transform: translateY(-15px) scale(1.2);
    opacity: 0.7; 
  }
  100% { 
    transform: translateY(-30px) scale(0.8);
    opacity: 0; 
  }
`;

// Container for Marc
const SharkContainer = styled.div`
  position: ${props => props.$fixed ? 'fixed' : 'absolute'};
  bottom: ${props => props.$position === 'bottom' ? '20px' : 'auto'};
  top: ${props => props.$position === 'top' ? '20px' : 'auto'};
  right: ${props => props.$position === 'right' ? '20px' : 'auto'};
  left: ${props => props.$position === 'left' ? '20px' : 'auto'};
  z-index: 1000;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: ${sharkSwim} 6s infinite ease-in-out;
  
  &:hover {
    transform: scale(1.1);
  }
`;

// Marc's body - using CSS to create pixelated shark
const SharkBody = styled.div`
  position: relative;
  width: 80px;
  height: 40px;
  background-color: #5d9bc7;
  border: 3px solid #2c4e6e;
  border-radius: 40px 60px 30px 0;
  image-rendering: pixelated;
  
  &::before {
    content: "";
    position: absolute;
    top: 5px;
    right: 10px;
    width: 8px;
    height: 8px;
    background-color: #2c4e6e;
    border-radius: 50%;
    box-shadow: 0 0 0 2px #5d9bc7, 0 0 0 4px #2c4e6e;
  }
`;

// Marc's glorious red hair
const SharkHair = styled.div`
  position: absolute;
  top: -12px;
  right: 15px;
  width: 30px;
  height: 15px;
  background-color: #ff5733; /* Vibrant red color */
  border: 2px solid #c0392b; /* Darker red border */
  border-radius: 5px 5px 0 0;
  z-index: 3;
  transform-origin: bottom center;
  animation: ${hairBob} 4s infinite ease-in-out;
  
  /* Create spiky hair effect */
  &::before {
    content: "";
    position: absolute;
    top: -10px;
    left: 2px;
    width: 8px;
    height: 15px;
    background-color: #ff5733;
    border: 2px solid #c0392b;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
    transform: rotate(-15deg);
  }

  &::after {
    content: "";
    position: absolute;
    top: -12px;
    left: 15px;
    width: 10px;
    height: 18px;
    background-color: #ff5733;
    border: 2px solid #c0392b;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
    transform: rotate(10deg);
  }
`;

// Additional hair spikes
const HairSpikes = styled.div`
  position: absolute;
  top: -16px;
  right: 28px;
  width: 6px;
  height: 16px;
  background-color: #ff5733;
  border: 2px solid #c0392b;
  border-bottom: none;
  border-radius: 3px 3px 0 0;
  transform: rotate(-5deg);
  z-index: 4;
  animation: ${spikesBob} 3.5s infinite ease-in-out;
  animation-delay: 0.2s;
`;

// Shark fin
const SharkFin = styled.div`
  position: absolute;
  top: -20px;
  left: 30px;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 25px solid #5d9bc7;
  border-radius: 2px;
  transform-origin: bottom center;
  animation: ${finWave} 3s infinite ease-in-out;
  
  &::after {
    content: "";
    position: absolute;
    top: 2px;
    left: -7px;
    width: 14px;
    height: 20px;
    background-color: #5d9bc7;
    border: 3px solid #2c4e6e;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
  }
`;

// Shark tail
const SharkTail = styled.div`
  position: absolute;
  top: 10px;
  left: -15px;
  width: 20px;
  height: 25px;
  background-color: #5d9bc7;
  border: 3px solid #2c4e6e;
  border-radius: 50% 0 0 50%;
  transform: rotate(45deg);
`;

// Speech bubble for Marc's tips
const SpeechBubble = styled.div`
  position: absolute;
  top: -80px;
  right: -20px;
  width: 200px;
  padding: 15px;
  background-color: white;
  border: 3px solid #2c4e6e;
  border-radius: 20px;
  font-size: 14px;
  color: #2c4e6e;
  font-weight: bold;
  opacity: ${props => props.$visible ? 1 : 0};
  transform: ${props => props.$visible ? 'translateY(0)' : 'translateY(20px)'};
  transition: all 0.3s ease;
  
  &::after {
    content: "";
    position: absolute;
    bottom: -15px;
    right: 30px;
    width: 30px;
    height: 15px;
    background-color: white;
    border-right: 3px solid #2c4e6e;
    border-bottom: 3px solid #2c4e6e;
    clip-path: polygon(0 0, 100% 0, 50% 100%);
  }
`;

// Bubbles that appear near Marc
const Bubbles = styled.div`
  position: absolute;
  top: 0;
  left: 10px;
`;

const Bubble = styled.div`
  position: absolute;
  width: ${props => props.$size || 6}px;
  height: ${props => props.$size || 6}px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  bottom: 0;
  left: ${props => props.$left || 0}px;
  animation: ${bubbleFloat} ${props => props.$duration || 3}s infinite ease-out;
  animation-delay: ${props => props.$delay || 0}s;
  opacity: 0;
`;

// Tips Marc can share with the user
const TIPS = [
  "Ahoy! Islands on the map represent blocks in the blockchain.",
  "The deeper the blue, the older the transaction!",
  "Click on an island to explore the treasure (transactions) inside!",
  "Follow the current to track transaction flows between addresses.",
  "Keep an eye out for unusual patterns in the digital sea!",
  "The bigger the island, the more transactions it contains!",
  "Need help navigating? Just click on me for guidance!",
  "Each token type has its own unique treasure chest icon.",
  "Sail through time using the timeline at the bottom of the map!",
  "Collect island tokens by exploring different parts of the blockchain."
];

const MarcTheShark = ({ position = 'right', fixed = false, autoTip = false }) => {
  const [tipVisible, setTipVisible] = useState(autoTip);
  const [currentTip, setCurrentTip] = useState(0);
  
  // Periodically change the tip if autoTip is enabled
  useEffect(() => {
    if (!autoTip) return;
    
    const interval = setInterval(() => {
      setCurrentTip(prevTip => (prevTip + 1) % TIPS.length);
    }, 8000);
    
    return () => clearInterval(interval);
  }, [autoTip]);
  
  // Toggle the visibility of Marc's tip
  const toggleTip = () => {
    if (!tipVisible) {
      // Show a random tip when manually clicking
      setCurrentTip(Math.floor(Math.random() * TIPS.length));
    }
    setTipVisible(!tipVisible);
  };
  
  return (
    <SharkContainer 
      onClick={toggleTip} 
      $position={position}
      $fixed={fixed}
    >
      <SpeechBubble $visible={tipVisible}>
        {TIPS[currentTip]}
      </SpeechBubble>
      
      <SharkBody>
        <SharkFin />
        <SharkHair />
        <HairSpikes />
        <SharkTail />
      </SharkBody>
      
      <Bubbles>
        <Bubble $size={8} $delay={0} $left={5} $duration={4} />
        <Bubble $size={5} $delay={1} $left={15} $duration={3} />
        <Bubble $size={6} $delay={2} $left={0} $duration={5} />
      </Bubbles>
    </SharkContainer>
  );
};

export default MarcTheShark; 