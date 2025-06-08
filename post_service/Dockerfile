FROM soa-base:latest

# Copy service-specific files
COPY post_service.py .

# Expose the service port
EXPOSE 8004

# Run the service
CMD ["python", "post_service.py"] 