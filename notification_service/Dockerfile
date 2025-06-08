FROM soa-base:latest

# Copy service-specific files
COPY notification_service.py .

# Expose the service port
EXPOSE 8010

# Run the service
CMD ["python", "notification_service.py"] 