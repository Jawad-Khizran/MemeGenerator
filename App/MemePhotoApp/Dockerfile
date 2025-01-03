# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app

# Install git and other necessary system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

# Copy the rest of the application code into the container
COPY . .

RUN chmod +x start_app.sh


CMD ["./start_app.sh"]