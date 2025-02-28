import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { performForensicAnalysis } from '../utils/api';

// Define keyframes
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const investigate = keyframes`
  0% { transform: rotate(-20deg) translateX(-10px); }
  50% { transform: rotate(20deg) translateX(10px); }
  100% { transform: rotate(-20deg) translateX(-10px); }
`;

// Wind Waker Styled Components
const PageContainer = styled.div`
  animation: ${fadeIn} 0.5s ease-in;
`;

const PageTitle = styled.h1`
  margin-bottom: 2rem;
  color: var(--hero-green);
  text-align: center;
  position: relative;

  &::after {
    content: "";
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 4px;
    background-color: var(--hero-green);
    border-radius: 2px;
  }
`;

const FormContainer = styled(Card)`
  max-width: 800px;
  margin: 0 auto 2rem;
`;

const FormTitle = styled.h2`
  color: var(--hero-green);
  margin-top: 0;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;

  @media (max-width: 576px) {
    flex-direction: column;
  }
`;

const ResultContainer = styled(Card)`
  margin-top: 2rem;
  position: relative;
  
  /* Forensic magnifying glass decoration */
  &::before {
    content: "🔍";
    position: absolute;
    top: -15px;
    right: 20px;
    font-size: 24px;
    transform: rotate(-15deg);
  }
`;

const ResultContent = styled.div`
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 1rem;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
`;

const LoadingIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: ${investigate} 2s infinite;
  
  &::after {
    content: "🔍";
  }
`;

const InfoText = styled.p`
  margin-top: 0.5rem;
  color: var(--dark-text);
  font-style: italic;
`;

const ErrorMessage = styled.div`
  background-color: rgba(255, 99, 71, 0.1);
  border-left: 4px solid tomato;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  color: tomato;
`;

// Wind Waker theme decorative element
const CloudDecoration = styled.div`
  position: absolute;
  top: 100px;
  right: 10%;
  width: 120px;
  height: 60px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50px;
  box-shadow: 
    50px 0 0 -10px rgba(255, 255, 255, 0.8),
    30px 0 0 -5px rgba(255, 255, 255, 0.8);
  opacity: 0.7;
  z-index: -1;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const ForensicAnalysis = () => {
  const [address, setAddress] = useState('');
  const [depth, setDepth] = useState(2);
  const [question, setQuestion] = useState('');
  const [provider, setProvider] = useState('claude');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!address.trim()) {
      setError('Please enter a wallet address');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await performForensicAnalysis(address, depth, question, provider);
      setResult(response.result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setAddress('');
    setDepth(2);
    setQuestion('');
    setResult(null);
    setError(null);
  };

  return (
    <PageContainer>
      <PageTitle>Forensic Analysis</PageTitle>
      <CloudDecoration />
      
      <FormContainer>
        <FormTitle>Analyze Blockchain Transactions Trail</FormTitle>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Input
              label="Starting Address"
              placeholder="Enter a blockchain wallet address to investigate"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              required
            />
            <InfoText>Example: 9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN</InfoText>
          </FormGroup>
          
          <FormGroup>
            <label>Trace Depth</label>
            <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center' }}>
              <input
                type="range"
                min="1"
                max="5"
                value={depth}
                onChange={(e) => setDepth(parseInt(e.target.value))}
                style={{ flexGrow: 1, marginRight: '1rem' }}
              />
              <span>{depth} hop{depth > 1 ? 's' : ''}</span>
            </div>
            <InfoText>Higher depth values will analyze more transaction hops but take longer</InfoText>
          </FormGroup>
          
          <FormGroup>
            <Input
              label="Question (Optional)"
              placeholder="Ask specific forensic questions about this address..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              multiline
            />
          </FormGroup>
          
          <FormGroup>
            <label>LLM Provider</label>
            <div style={{ marginTop: '0.5rem' }}>
              <label style={{ marginRight: '1rem' }}>
                <input
                  type="radio"
                  value="claude"
                  checked={provider === 'claude'}
                  onChange={() => setProvider('claude')}
                  style={{ marginRight: '0.5rem' }}
                />
                Claude
              </label>
              <label>
                <input
                  type="radio"
                  value="ollama"
                  checked={provider === 'ollama'}
                  onChange={() => setProvider('ollama')}
                  style={{ marginRight: '0.5rem' }}
                />
                Ollama (Local)
              </label>
            </div>
          </FormGroup>
          
          <ButtonGroup>
            <Button type="submit" disabled={loading}>
              {loading ? 'Analyzing...' : 'Perform Forensic Analysis'}
            </Button>
            <Button 
              type="button" 
              variant="secondary" 
              onClick={handleClear}
              disabled={loading}
            >
              Clear
            </Button>
          </ButtonGroup>
        </form>
      </FormContainer>
      
      {loading && (
        <ResultContainer>
          <LoadingContainer>
            <LoadingIcon />
            <h3>Performing forensic analysis...</h3>
            <p>Investigating transaction trails. This might take a few minutes due to the complexity.</p>
          </LoadingContainer>
        </ResultContainer>
      )}
      
      {!loading && result && (
        <ResultContainer title="Forensic Analysis Results">
          <ResultContent>{result}</ResultContent>
        </ResultContainer>
      )}
    </PageContainer>
  );
};

export default ForensicAnalysis; 