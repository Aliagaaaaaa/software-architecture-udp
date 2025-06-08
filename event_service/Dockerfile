FROM soa-base:latest

# Copy service-specific files
COPY event_service.py .

# Expose the service port
EXPOSE 8007

# Run the service
CMD ["python", "event_service.py"] 