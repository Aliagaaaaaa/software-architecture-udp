FROM soa-base:latest

# Copy service-specific files
COPY forum_service.py .

# Expose the service port
EXPOSE 8003

# Run the service
CMD ["python", "forum_service.py"] 