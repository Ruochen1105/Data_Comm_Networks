FROM python:3.11-slim

WORKDIR /app

# Install requirements
RUN pip install --no-cache-dir flask requests

# Copy the application code
COPY US.py .

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "US.py"]
