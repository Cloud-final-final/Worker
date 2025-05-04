# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt wordnet omw-1.4

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 80 available to the world outside this container (if needed, adjust if not a web service)
# EXPOSE 80 

# Define environment variable for Google Credentials (will be set in docker-compose)
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/key.json

# Set the command to run the application (adjust if needed)
# Assuming tasks.py needs to be run directly or via a task runner
# This CMD might need adjustment based on how the worker is actually invoked.
# For now, let's keep it simple. If it's meant to be run with arguments or via Celery, update accordingly.
CMD ["python", "tasks.py"]