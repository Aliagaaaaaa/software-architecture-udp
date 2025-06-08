FROM soa-base:latest

# Copy service-specific files
COPY comment_service.py .

# Expose the service port
EXPOSE 8006

# Run the service
CMD ["python", "comment_service.py"] 