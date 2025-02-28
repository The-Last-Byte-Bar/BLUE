# BLUE - Blockchain Analysis Tool

BLUE is a blockchain analysis platform that combines the power of LLM-driven analytics with a charming Wind Waker-inspired user interface. This tool enables blockchain researchers, analysts, and enthusiasts to explore blockchain data through natural language queries and receive AI-powered insights about wallets, transactions, network metrics, and transaction flows.

![BLUE Screenshot](./docs/blue-screenshot.png)

## What is BLUE?

BLUE leverages large language models (Claude or local Ollama models) to analyze blockchain data and present insights in a user-friendly manner. The Wind Waker-inspired UI creates an engaging experience as you navigate through the ocean of blockchain data.

### Key Features

- **Wallet Analysis**: Investigate blockchain addresses, balances, transaction history, asset holdings, and patterns of activity. Ask natural language questions about wallets to get detailed insights about their behavior and purpose.

- **Transaction Analysis**: Decode complex blockchain transactions, understand token transfers, smart contract interactions, and purpose of transactions. Input any transaction ID and get a comprehensive breakdown of what happened and why.

- **Network Analysis**: Explore blockchain-wide metrics like transaction volume, active addresses, fees, mining/staking statistics, and trends. Understand the health and activity of the blockchain ecosystem over time.

- **Forensic Analysis**: Track funds across multiple transaction hops, visualize money flow patterns, identify suspicious activities, and establish connections between addresses. Specify how many transaction hops to analyze for deeper investigations.

## Tech Stack

- **Backend**: Python with FastAPI, with LLM integration (Claude/Ollama)
- **Frontend**: React with Wind Waker-inspired UI components and styling
- **Deployment**: Docker Compose for easy setup and containerization

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Anthropic API Key](https://www.anthropic.com/) for Claude integration (optional if using Ollama)
- Ergo Explorer API key (optional, for higher rate limits)

### Quick Start with Helper Scripts

BLUE comes with several helper scripts to make setup and usage easier:

1. **Setup Script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   This script checks dependencies, creates environment files, builds and starts the containers.

2. **Build Script**:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```
   Builds Docker images without starting containers.

3. **Development Script**:
   ```bash
   chmod +x dev.sh
   ./dev.sh
   ```
   Runs both frontend and backend in development mode with hot-reloading.

4. **Test Script**:
   ```bash
   chmod +x test.sh
   ./test.sh
   ```
   Runs tests for both frontend and backend.

5. **Cleanup Script**:
   ```bash
   chmod +x cleanup.sh
   ./cleanup.sh
   ```
   Removes containers, images, and cleans up development artifacts.

### Manual Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd BLUE
   ```

2. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   EXPLORER_API_URL=https://api.ergoplatform.com
   EXPLORER_API_KEY=your_explorer_api_key_if_needed
   ```

3. **Build and start the containers**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**:
   - Frontend UI: http://localhost:3030
   - Backend API: http://localhost:8008

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Usage Guide

### Analyzing a Wallet

1. Navigate to the Wallet Analysis page
2. Enter a blockchain wallet address (e.g., `9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN`)
3. Optionally enter a specific question about the wallet
4. Select your preferred LLM provider (Claude or Ollama)
5. Click "Analyze Wallet" and wait for the results

### Analyzing a Transaction

1. Navigate to the Transaction Analysis page
2. Enter a transaction ID/hash (e.g., `f5eb96783f8c492c533b7a898b52b75b4c0f8a703c4e70d833a5f1167a408fc8`)
3. Optionally enter a specific question about the transaction
4. Select your preferred LLM provider
5. Click "Analyze Transaction" and wait for the results

### Analyzing Network Metrics

1. Navigate to the Network Analysis page
2. Select the metrics you're interested in
3. Optionally enter a specific question about network performance
4. Select your preferred LLM provider
5. Click "Analyze Network" and wait for the results

### Performing Forensic Analysis

1. Navigate to the Forensic Analysis page
2. Enter a starting wallet address
3. Select the trace depth (how many transaction hops to analyze)
4. Optionally enter specific questions for your investigation
5. Select your preferred LLM provider
6. Click "Perform Forensic Analysis" and wait for the results

## API Endpoints

BLUE exposes the following API endpoints:

- `GET /`: Root endpoint with API information
- `POST /api/wallet`: Wallet analysis endpoint
- `POST /api/transaction`: Transaction analysis endpoint
- `POST /api/network`: Network analysis endpoint
- `POST /api/forensic`: Forensic analysis endpoint

## Development

### Running Backend Locally

```bash
cd api
python -m pip install -r ../requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8008
```

### Running Frontend Locally

```bash
cd frontend
npm install
PORT=3030 npm start
```

## Project Structure

- `api/`: FastAPI backend code
- `frontend/`: React frontend application
- `docker/`: Docker configuration files
  - `backend.Dockerfile`: Backend container configuration
  - `frontend.Dockerfile`: Frontend container configuration
  - `nginx/`: Nginx configuration for serving the React app
- `llm/`: LLM integration modules
- `blockchain/`: Blockchain analysis modules
- `tests/`: Test suite for the application
- Helper scripts:
  - `setup.sh`: Setup script
  - `cleanup.sh`: Cleanup script
  - `dev.sh`: Development script
  - `test.sh`: Test script
  - `build.sh`: Build script

## License

[LICENSE](./LICENSE)
