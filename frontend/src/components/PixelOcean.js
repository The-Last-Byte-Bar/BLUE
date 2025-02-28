import React, { useState, useEffect, useRef } from 'react';
import styled, { keyframes } from 'styled-components';

// Wave animation
const waveAnimation = keyframes`
  0% { background-position: 0 0; }
  100% { background-position: 500px 0; }
`;

// Container for the ocean
const OceanContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -10;
  overflow: hidden;
  background-color: var(--deep-blue);
  image-rendering: pixelated;
`;

// Canvas for the ocean
const OceanCanvas = styled.canvas`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
`;

// Waves overlay
const WavesOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z' opacity='.25' fill='%23addcf7'%3E%3C/path%3E%3Cpath d='M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z' opacity='.5' fill='%237cbdec'%3E%3C/path%3E%3Cpath d='M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z' opacity='.5' fill='%233a75c4'%3E%3C/path%3E%3C/svg%3E") repeat-x;
  background-size: 1200px 100px;
  animation: ${waveAnimation} 20s linear infinite;
  opacity: 0.3;
`;

// Sun/light effect
const SunLight = styled.div`
  position: absolute;
  top: 5%;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 70%);
  opacity: 0.8;
`;

// Pixelated cloud component
const PixelCloud = styled.div`
  position: absolute;
  width: ${props => props.size || 80}px;
  height: ${props => props.size / 3 || 30}px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  top: ${props => props.$top || '10%'};
  left: ${props => props.$left || '10%'};
  animation: ${props => props.$animation} ${props => props.$duration || 60}s linear infinite;
  animation-delay: ${props => props.$delay || 0}s;
  opacity: 0.7;
  
  &::before {
    content: '';
    position: absolute;
    top: -15px;
    left: 15px;
    width: ${props => props.size / 2.5 || 30}px;
    height: ${props => props.size / 2.5 || 30}px;
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: -10px;
    right: 15px;
    width: ${props => props.size / 3 || 20}px;
    height: ${props => props.size / 3 || 20}px;
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
  }
`;

// Cloud animation
const cloudMove = (startPos, endPos) => keyframes`
  0% { transform: translateX(${startPos}vw); }
  100% { transform: translateX(${endPos}vw); }
`;

// Main PixelOcean component
const PixelOcean = () => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });
  const pixelSize = 6; // Size of each "pixel" in our ocean
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Draw the pixelated ocean
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw pixelated ocean
    const cols = Math.ceil(dimensions.width / pixelSize);
    const rows = Math.ceil(dimensions.height / pixelSize);
    
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        // Create variation in blue colors for a more dynamic ocean
        const depthFactor = Math.min(1, j / (rows * 0.7)); // Darker as we go deeper
        const randomFactor = Math.random() * 0.1 - 0.05; // Small random variation
        
        // Base colors from CSS variables
        const r = 58 + (124 - 58) * (1 - depthFactor) + randomFactor * 255;
        const g = 117 + (189 - 117) * (1 - depthFactor) + randomFactor * 255;
        const b = 196 + (236 - 196) * (1 - depthFactor) + randomFactor * 255;
        
        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
        ctx.fillRect(i * pixelSize, j * pixelSize, pixelSize, pixelSize);
      }
    }
    
    // Add some random "sparkles" to simulate light reflecting off water
    for (let s = 0; s < dimensions.width / 20; s++) {
      const x = Math.floor(Math.random() * cols) * pixelSize;
      const y = Math.floor(Math.random() * (rows / 2)) * pixelSize; // Keep sparkles in upper half
      
      // Make the sparkle lighter and more transparent
      ctx.fillStyle = `rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1})`;
      ctx.fillRect(x, y, pixelSize, pixelSize);
    }
    
  }, [dimensions]);
  
  return (
    <OceanContainer>
      <OceanCanvas ref={canvasRef} />
      <WavesOverlay />
      <SunLight />
      
      {/* Add some pixelated clouds */}
      <PixelCloud 
        size={100} 
        $top="5%" 
        $left="0%" 
        $animation={cloudMove(-20, 120)} 
        $duration={120} 
      />
      <PixelCloud 
        size={60} 
        $top="15%" 
        $left="20%" 
        $animation={cloudMove(-20, 120)} 
        $duration={180}
        $delay={30}
      />
      <PixelCloud 
        size={80} 
        $top="8%" 
        $left="60%" 
        $animation={cloudMove(-20, 120)} 
        $duration={150}
        $delay={60}
      />
    </OceanContainer>
  );
};

export default PixelOcean; 