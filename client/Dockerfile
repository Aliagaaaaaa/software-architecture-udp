FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy client files
COPY soa_client.py .
COPY soa_protocol.py .
COPY services_config.py .

# Run the client
CMD ["python", "soa_client.py"] 