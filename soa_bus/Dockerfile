FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bus files
COPY soa_server.py .
COPY soa_protocol.py .
COPY services_config.py .

# Expose the bus port
EXPOSE 8000

# Run the bus
CMD ["python", "soa_server.py"] 