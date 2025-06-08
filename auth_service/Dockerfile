FROM soa-base:latest

# Copy service-specific files
COPY auth_service.py .

# Expose the service port
EXPOSE 8001

# Run the service with explicit port
CMD ["python", "-c", "import auth_service; auth_service.AuthService(port=8001).start_service()"] 