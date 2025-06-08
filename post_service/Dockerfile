FROM soa-base:latest

# Copy service-specific files
COPY post_service.py .

# Expose the service port
EXPOSE 8005

# Run the service
CMD ["python", "post_service.py"] 