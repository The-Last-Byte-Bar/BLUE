import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { analyzeNetwork } from '../utils/api';

// Define keyframes
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const pulse = keyframes`
  from { transform: scale(1); opacity: 0.5; }
  to { transform: scale(1.2); opacity: 1; }
`;

const waveAnimation = keyframes`
  0% { transform: translateX(0) translateY(0) rotate(0); }
  50% { transform: translateX(-25px) translateY(10px) rotate(10deg); }
  100% { transform: translateX(0) translateY(0) rotate(0); }
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
  animation: ${pulse} 1.5s infinite alternate;
`;

const ErrorMessage = styled.div`
  background-color: rgba(255, 99, 71, 0.1);
  border-left: 4px solid tomato;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  color: tomato;
`;

// Ocean wave decoration
const OceanWaves = styled.div`
  position: fixed;
  bottom: -50px;
  left: 0;
  width: 100%;
  height: 100px;
  background: linear-gradient(to bottom, transparent, var(--deep-blue));
  z-index: -1;
  opacity: 0.5;
  
  &::before {
    content: "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰";
    position: absolute;
    bottom: 40px;
    left: 0;
    width: 200%;
    font-size: 40px;
    color: var(--light-blue);
    letter-spacing: -10px;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
    animation: ${waveAnimation} 8s infinite ease-in-out;
  }
  
  &::after {
    content: "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰";
    position: absolute;
    bottom: 20px;
    left: -50px;
    width: 200%;
    font-size: 30px;
    color: var(--sand-yellow);
    letter-spacing: -5px;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
    animation: ${waveAnimation} 6s infinite ease-in-out reverse;
  }
`;

const NetworkAnalysis = () => {
  const [question, setQuestion] = useState('');
  const [metrics, setMetrics] = useState(['hash_rate', 'difficulty', 'transaction_count']);
  const [provider, setProvider] = useState('claude');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await analyzeNetwork(metrics, question, provider);
      // Make sure we're dealing with a string result
      const resultText = typeof response.result === 'string' 
        ? response.result 
        : JSON.stringify(response.result, null, 2);
      setResult(resultText);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    setMetrics(['hash_rate', 'difficulty', 'transaction_count']);
    setResult(null);
    setError(null);
  };

  const handleMetricChange = (metric) => {
    if (metrics.includes(metric)) {
      setMetrics(metrics.filter(m => m !== metric));
    } else {
      setMetrics([...metrics, metric]);
    }
  };

  return (
    <PageContainer>
      <PageTitle>Network Analysis</PageTitle>
      <OceanWaves />
      
      <FormContainer>
        <FormTitle>Analyze Blockchain Network</FormTitle>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <label>Select Metrics to Analyze</label>
            <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
              <label>
                <input
                  type="checkbox"
                  checked={metrics.includes('hash_rate')}
                  onChange={() => handleMetricChange('hash_rate')}
                  style={{ marginRight: '0.5rem' }}
                />
                Hash Rate
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={metrics.includes('difficulty')}
                  onChange={() => handleMetricChange('difficulty')}
                  style={{ marginRight: '0.5rem' }}
                />
                Difficulty
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={metrics.includes('transaction_count')}
                  onChange={() => handleMetricChange('transaction_count')}
                  style={{ marginRight: '0.5rem' }}
                />
                Transaction Count
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={metrics.includes('active_addresses')}
                  onChange={() => handleMetricChange('active_addresses')}
                  style={{ marginRight: '0.5rem' }}
                />
                Active Addresses
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={metrics.includes('fee_rates')}
                  onChange={() => handleMetricChange('fee_rates')}
                  style={{ marginRight: '0.5rem' }}
                />
                Fee Rates
              </label>
            </div>
          </FormGroup>
          
          <FormGroup>
            <Input
              label="Question (Optional)"
              placeholder="Ask a specific question about network metrics..."
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
              {loading ? 'Analyzing...' : 'Analyze Network'}
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
            <LoadingIcon>🌊</LoadingIcon>
            <h3>Analyzing network metrics...</h3>
            <p>Charting the seas of blockchain data. This might take a minute.</p>
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

export default NetworkAnalysis; 