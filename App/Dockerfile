# Use the Alpine image as the base image
FROM alpine:latest

# Install Python, pip, and build dependencies
RUN apk add --no-cache python3 py3-pip python3-dev gcc musl-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip

# Set the virtual environment to be used by default
ENV PATH="/venv/bin:$PATH"

# Set the PYTHONPATH to include the /app directory
ENV PYTHONPATH=/App

# Set the working directory
WORKDIR /App

# Copy requirements.txt and install dependencies
COPY requirements.txt /App/
RUN pip install -r requirements.txt

# Copy project files
COPY . /App/

# Expose the Flask app port
EXPOSE 5000

# Set the entrypoint and default command
ENTRYPOINT ["python3"]
CMD ["app.py"]