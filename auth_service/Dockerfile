FROM soa-base:latest

# Copy service-specific files
COPY auth_service.py .

# Expose the service port
EXPOSE 8001

# Run the service
CMD ["python", "auth_service.py"] 