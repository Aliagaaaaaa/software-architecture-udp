FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common files
COPY soa_service_base.py .
COPY soa_protocol.py .
COPY database_client.py .
COPY services_config.py .

# Copy service-specific files
COPY comment_service.py .

# Expose the service port
EXPOSE 8006

# Run the service
CMD ["python", "comment_service.py"] 