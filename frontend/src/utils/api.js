import axios from 'axios';

// Set up axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds timeout for LLM queries which can take time
});

// API methods
export const analyzeWallet = async (address, question, provider = 'claude') => {
  try {
    const response = await api.post('/wallet', {
      address,
      question,
      provider,
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing wallet:', error);
    throw error;
  }
};

export const analyzeTransaction = async (txId, question, provider = 'claude') => {
  try {
    const response = await api.post('/transaction', {
      tx_id: txId,
      question,
      provider,
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing transaction:', error);
    throw error;
  }
};

export const analyzeNetwork = async (metrics, question, provider = 'claude') => {
  try {
    const response = await api.post('/network', {
      metrics,
      question,
      provider,
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing network:', error);
    throw error;
  }
};

export const performForensicAnalysis = async (address, depth = 2, question, provider = 'claude') => {
  try {
    const response = await api.post('/forensic', {
      address,
      depth,
      question,
      provider,
    });
    return response.data;
  } catch (error) {
    console.error('Error performing forensic analysis:', error);
    throw error;
  }
}; 