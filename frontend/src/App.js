import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import styled from 'styled-components';

// Pages
import Home from './pages/Home';
import WalletAnalysis from './pages/WalletAnalysis';
import TransactionAnalysis from './pages/TransactionAnalysis';
import NetworkAnalysis from './pages/NetworkAnalysis';
import ForensicAnalysis from './pages/ForensicAnalysis';

// New components
import MarcTheShark from './components/MarcTheShark';
import PixelOcean from './components/PixelOcean';

// Styled components with Wind Waker theme
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  image-rendering: pixelated;
  position: relative;
`;

const Header = styled.header`
  background-color: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  padding: 1rem 2rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 4px solid var(--hero-green);
  position: relative;
  z-index: 100;

  /* Pixel art border */
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 100%;
    height: 4px;
    background-image: linear-gradient(
      to right,
      transparent 0%,
      transparent 25%,
      var(--hero-green) 25%,
      var(--hero-green) 75%,
      transparent 75%,
      transparent 100%
    );
    background-size: 8px 4px;
  }

  @media (max-width: 768px) {
    flex-direction: column;
    padding: 1rem;
  }
`;

const Logo = styled.div`
  font-size: 2.8rem;
  font-weight: bold;
  color: var(--hero-green);
  text-shadow: 2px 2px 0 white, -2px 2px 0 white, 2px -2px 0 white, -2px -2px 0 white;
  margin-right: 2rem;
  display: flex;
  align-items: center;
  font-family: 'Press Start 2P', 'Courier New', monospace;

  /* Wind Waker-inspired arrow icon */
  &::before {
    content: "";
    display: inline-block;
    width: 40px;
    height: 40px;
    margin-right: 15px;
    background-color: var(--hero-green);
    clip-path: polygon(0% 20%, 60% 20%, 60% 0%, 100% 50%, 60% 100%, 60% 80%, 0% 80%);
  }
`;

const Nav = styled.nav`
  display: flex;
  gap: 1.5rem;
  align-items: center;

  @media (max-width: 768px) {
    margin-top: 1rem;
    flex-wrap: wrap;
    justify-content: center;
  }
`;

const NavLink = styled(Link)`
  color: var(--dark-text);
  font-size: 1.1rem;
  font-weight: 600;
  padding: 0.8rem 1.2rem;
  text-decoration: none;
  position: relative;
  transition: all 0.3s ease;
  border-radius: 8px;
  border: 2px solid transparent;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
    border-color: var(--hero-green);
    transform: translateY(-2px);
    
    &::before {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Pixel art decorative element */
  &::before {
    content: '✦';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%) translateY(10px);
    color: var(--sunset-orange);
    opacity: 0;
    transition: all 0.3s ease;
  }
`;

const Main = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
`;

const Footer = styled.footer`
  text-align: center;
  padding: 1.5rem;
  margin-top: auto;
  background-color: rgba(0, 0, 0, 0.3);
  font-size: 0.9rem;
  border-top: 4px solid var(--hero-green);
  color: var(--light-text);
  position: relative;
  z-index: 100;
  
  /* Pixel art border */
  &::before {
    content: '';
    position: absolute;
    top: -8px;
    left: 0;
    width: 100%;
    height: 4px;
    background-image: linear-gradient(
      to right,
      transparent 0%,
      transparent 25%,
      var(--hero-green) 25%,
      var(--hero-green) 75%,
      transparent 75%,
      transparent 100%
    );
    background-size: 8px 4px;
  }
`;

function App() {
  return (
    <Router>
      <AppContainer>
        {/* Pixelated Ocean Background */}
        <PixelOcean />
        
        <Header>
          <Logo>BLUE</Logo>
          <Nav>
            <NavLink to="/">Home</NavLink>
            <NavLink to="/wallet">Wallet Analysis</NavLink>
            <NavLink to="/transaction">Transaction Analysis</NavLink>
            <NavLink to="/network">Network Analysis</NavLink>
            <NavLink to="/forensic">Forensic Analysis</NavLink>
          </Nav>
        </Header>
        
        <Main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/wallet" element={<WalletAnalysis />} />
            <Route path="/transaction" element={<TransactionAnalysis />} />
            <Route path="/network" element={<NetworkAnalysis />} />
            <Route path="/forensic" element={<ForensicAnalysis />} />
          </Routes>
        </Main>
        
        {/* Marc the Shark Guide */}
        <MarcTheShark position="right" fixed={true} />
        
        <Footer>
          <p>BLUE Blockchain Analysis Tool © {new Date().getFullYear()}</p>
        </Footer>
      </AppContainer>
    </Router>
  );
}

export default App; 