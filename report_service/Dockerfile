FROM soa-base:latest

# Copy service-specific files
COPY report_service.py .

# Expose the service port
EXPOSE 8007

# Run the service
CMD ["python", "report_service.py"] 