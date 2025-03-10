FROM python:3.11-slim

WORKDIR /app

# Copy the application code
COPY AS.py .

# Expose the port for UDP communication
EXPOSE 53533/udp

# Run the application
CMD ["python", "AS.py"]
