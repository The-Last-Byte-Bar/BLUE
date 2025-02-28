import React from 'react';
import { Link } from 'react-router-dom';
import styled, { keyframes } from 'styled-components';
import Card from '../components/Card';
import Button from '../components/Button';
import Island from '../components/Island';

// Wind Waker-inspired animations
const floatAnimation = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
  100% { transform: translateY(0px); }
`;

const fadeInAnimation = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const waveAnimation = keyframes`
  0% { transform: rotate(0deg); }
  10% { transform: rotate(14deg); }
  20% { transform: rotate(-8deg); }
  30% { transform: rotate(14deg); }
  40% { transform: rotate(-4deg); }
  50% { transform: rotate(10deg); }
  60% { transform: rotate(0deg); }
  100% { transform: rotate(0deg); }
`;

// Styled components
const HomeContainer = styled.div`
  animation: ${fadeInAnimation} 0.6s ease-out;
`;

const Hero = styled.div`
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  position: relative;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(5px);
  border: 3px solid var(--island-outline);
  box-shadow: 0 8px 0 rgba(0, 0, 0, 0.2);
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: var(--hero-green);
  text-shadow: 3px 3px 0 white, -3px 3px 0 white, 3px -3px 0 white, -3px -3px 0 white;
  position: relative;
  
  @media (max-width: 768px) {
    font-size: 2rem;
  }
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: var(--light-text);
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
`;

const IslandSection = styled.div`
  display: flex;
  justify-content: center;
  align-items: flex-end;
  flex-wrap: wrap;
  margin: 3rem 0;
  position: relative;
  min-height: 200px;
`;

const Ocean = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: rgba(58, 117, 196, 0.3);
  border-radius: 0 0 10px 10px;
`;

const FeatureSection = styled.div`
  margin-top: 4rem;
  position: relative;
`;

const SectionTitle = styled.h2`
  text-align: center;
  margin-bottom: 2rem;
  color: var(--hero-green);
  position: relative;
  padding-bottom: 0.5rem;
  
  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 4px;
    background-color: var(--hero-green);
    border-radius: 2px;
  }
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
`;

const FeatureCard = styled(Card)`
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-10px);
  }
`;

const FeatureIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: var(--hero-green);
  animation: ${floatAnimation} 6s ease-in-out infinite;
  animation-delay: ${props => props.delay || '0s'};
  display: flex;
  justify-content: center;
`;

const FeatureTitle = styled.h3`
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: var(--hero-green);
`;

const FeatureDescription = styled.p`
  flex-grow: 1;
  line-height: 1.6;
`;

const FeatureButton = styled(Link)`
  text-decoration: none;
  margin-top: 1.5rem;
  display: inline-block;
`;

// Decorative element
const WaveHand = styled.div`
  display: inline-block;
  font-size: 2rem;
  margin-left: 1rem;
  animation: ${waveAnimation} 2.5s infinite;
  transform-origin: 70% 70%;
`;

const Home = () => {
  return (
    <HomeContainer>
      <Hero>
        <Title>
          BLUE Blockchain Explorer
          <WaveHand>👋</WaveHand>
        </Title>
        <Subtitle>
          Set sail on the digital ocean of the Ergo blockchain! Navigate through islands of 
          transactions, explore treasure troves of wallet data, and chart your course with 
          our Wind Waker-inspired analysis tools.
        </Subtitle>
      </Hero>
      
      <IslandSection>
        <Ocean />
        <Island 
          to="/wallet" 
          size={120} 
          label="Wallet Island" 
          featureType="block"
          hasTreasure={true}
        />
        <Island 
          to="/transaction" 
          size={100} 
          label="Transaction Bay" 
          featureType="transaction"
          hasSecondFeature={true}
        />
        <Island 
          to="/network" 
          size={140} 
          label="Network Archipelago" 
          featureType="token"
        />
        <Island 
          to="/forensic" 
          size={110} 
          label="Forensic Depths" 
          featureType="block"
          hasTreasure={true}
          hasSecondFeature={true}
        />
      </IslandSection>
      
      <FeatureSection>
        <SectionTitle>Begin Your Adventure</SectionTitle>
        <FeatureGrid>
          <FeatureCard>
            <FeatureIcon delay="0s">💰</FeatureIcon>
            <FeatureTitle>Wallet Analysis</FeatureTitle>
            <FeatureDescription>
              Explore wallets and their transaction history. Get detailed insights about wallet behavior,
              balance history, and potential connections to other addresses.
            </FeatureDescription>
            <FeatureButton to="/wallet">
              <Button>Explore Wallets</Button>
            </FeatureButton>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon delay="0.2s">🔄</FeatureIcon>
            <FeatureTitle>Transaction Analysis</FeatureTitle>
            <FeatureDescription>
              Dive deep into individual transactions. Understand complex token transfers,
              contract interactions, and decode the purpose of any transaction.
            </FeatureDescription>
            <FeatureButton to="/transaction">
              <Button>Discover Transactions</Button>
            </FeatureButton>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon delay="0.4s">📊</FeatureIcon>
            <FeatureTitle>Network Analysis</FeatureTitle>
            <FeatureDescription>
              Examine network-wide metrics and trends. Monitor blockchain health,
              transaction volumes, gas prices, and identify network patterns.
            </FeatureDescription>
            <FeatureButton to="/network">
              <Button>Chart Networks</Button>
            </FeatureButton>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon delay="0.6s">🕵️</FeatureIcon>
            <FeatureTitle>Forensic Analysis</FeatureTitle>
            <FeatureDescription>
              Conduct deep forensic investigations. Track fund flows across multiple
              hops, identify suspicious patterns, and visualize complex relationships.
            </FeatureDescription>
            <FeatureButton to="/forensic">
              <Button>Investigate Patterns</Button>
            </FeatureButton>
          </FeatureCard>
        </FeatureGrid>
      </FeatureSection>
    </HomeContainer>
  );
};

export default Home; 