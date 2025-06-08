FROM soa-base:latest

# Copy service-specific files
COPY prof_service.py .

# Expose the service port
EXPOSE 8002

# Run the service with explicit port
CMD ["python", "-c", "import prof_service; prof_service.ProfileService(port=8002).start_service()"] 