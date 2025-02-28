import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { analyzeTransaction } from '../utils/api';

// Define keyframes
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  
  /* Wind Waker-style decorative arrows */
  &::before {
    content: "→";
    position: absolute;
    top: 10px;
    left: -20px;
    font-size: 24px;
    color: var(--hero-green);
    opacity: 0.6;
  }
  
  &::after {
    content: "→";
    position: absolute;
    bottom: 10px;
    right: -20px;
    font-size: 24px;
    color: var(--hero-green);
    opacity: 0.6;
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
  animation: ${spin} 2s linear infinite;
  
  &::after {
    content: "⟳";
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

// Decorative elements
const TransactionFlow = styled.div`
  position: absolute;
  width: 100%;
  height: 4px;
  background-color: var(--hero-green);
  opacity: 0.2;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  z-index: -1;
`;

const TransactionAnalysis = () => {
  const [txId, setTxId] = useState('');
  const [question, setQuestion] = useState('');
  const [provider, setProvider] = useState('claude');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!txId.trim()) {
      setError('Please enter a transaction ID');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await analyzeTransaction(txId, question, provider);
      setResult(response.result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setTxId('');
    setQuestion('');
    setResult(null);
    setError(null);
  };

  return (
    <PageContainer>
      <PageTitle>Transaction Analysis</PageTitle>
      <TransactionFlow />
      
      <FormContainer>
        <FormTitle>Analyze a Blockchain Transaction</FormTitle>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Input
              label="Transaction ID"
              placeholder="Enter a blockchain transaction ID (hash)"
              value={txId}
              onChange={(e) => setTxId(e.target.value)}
              required
            />
            <InfoText>Example: f5eb96783f8c492c533b7a898b52b75b4c0f8a703c4e70d833a5f1167a408fc8</InfoText>
          </FormGroup>
          
          <FormGroup>
            <Input
              label="Question (Optional)"
              placeholder="Ask a specific question about this transaction..."
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
              {loading ? 'Analyzing...' : 'Analyze Transaction'}
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
            <h3>Analyzing transaction...</h3>
            <p>Deciphering the transaction data. This might take a minute.</p>
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

export default TransactionAnalysis; 