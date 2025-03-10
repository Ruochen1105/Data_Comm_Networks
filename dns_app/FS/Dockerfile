FROM python:3.11-slim

WORKDIR /app

# Install requirements
RUN pip install --no-cache-dir flask

# Copy the application code
COPY FS.py .

# Expose the port
EXPOSE 9090

# Run the application
CMD ["python", "FS.py"]
