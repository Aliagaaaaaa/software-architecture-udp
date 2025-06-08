FROM soa-base:latest

# Copy service-specific files
COPY prof_service.py .

# Expose the service port
EXPOSE 8008

# Run the service
CMD ["python", "prof_service.py"] 