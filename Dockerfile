# Dockerfile

# Start from an official, lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
# This way, dependencies are only re-installed if requirements.txt change
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expost port 8000 to allow communication with the app inside the container
EXPOSE 8000  
# (this is for documentation and local use, Cloud Run ignores it)

# Define the command to run the application when the container starts
# We use "--host 0.0.0.0" to make the server accessible from outside the container
# Use the "shell form" to allow environment variable substitution.
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT