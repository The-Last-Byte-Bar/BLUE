FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn

# Copy project files
COPY . .

# Run the FastAPI server
# Note: This port (8000) is internal to the container and is mapped to 8008 externally
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"] 