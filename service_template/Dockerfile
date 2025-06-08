FROM soa-base:latest

# Copy service-specific files
COPY ${SERVICE_NAME}.py .

# Expose the service port
EXPOSE ${SERVICE_PORT}

# Run the service
CMD ["python", "${SERVICE_NAME}.py"] 