FROM soa-base:latest

# Copy service-specific files
COPY message_service.py .

# Expose the service port
EXPOSE 8002

# Run the service
CMD ["python", "message_service.py"] 