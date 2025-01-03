# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files from the `GeminiApiApp` directory
COPY . /app

# Install git and other necessary system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask app port
EXPOSE 5000

# Make the start script executable
RUN chmod +x start_app.sh

# Set the default command to run the app
CMD ["./start_app.sh"]
