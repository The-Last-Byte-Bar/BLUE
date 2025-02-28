import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { analyzeWallet } from '../utils/api';

// Define keyframes
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const bob = keyframes`
  from { transform: translateY(0); }
  to { transform: translateY(-20px); }
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
  
  /* Wind Waker ocean waves decoration at the bottom */
  &::after {
    content: "〰〰〰〰〰〰〰〰〰〰";
    position: absolute;
    bottom: -15px;
    left: 0;
    width: 100%;
    text-align: center;
    color: var(--deep-blue);
    font-size: 20px;
    letter-spacing: -2px;
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
  animation: ${bob} 1.5s infinite alternate;
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

const WalletAnalysis = () => {
  const [address, setAddress] = useState('');
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
      const response = await analyzeWallet(address, question, provider);
      setResult(response.result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setAddress('');
    setQuestion('');
    setResult(null);
    setError(null);
  };

  return (
    <PageContainer>
      <PageTitle>Wallet Analysis</PageTitle>
      
      <FormContainer>
        <FormTitle>Analyze a Blockchain Wallet</FormTitle>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Input
              label="Wallet Address"
              placeholder="Enter a blockchain wallet address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              required
            />
            <InfoText>Example: 9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN</InfoText>
          </FormGroup>
          
          <FormGroup>
            <Input
              label="Question (Optional)"
              placeholder="Ask a specific question about this wallet..."
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
              {loading ? 'Analyzing...' : 'Analyze Wallet'}
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
            <LoadingIcon>⛵</LoadingIcon>
            <h3>Analyzing wallet...</h3>
            <p>Sailing through the blockchain data ocean. This might take a minute.</p>
          </LoadingContainer>
        </ResultContainer>
      )}
      
      {!loading && result && (
        <ResultContainer title="Analysis Results">
          <ResultContent>{result}</ResultContent>
        </ResultContainer>
      )}
    </PageContainer>
  );
};

export default WalletAnalysis; 