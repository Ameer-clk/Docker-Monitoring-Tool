# Use an official Python runtime as the base image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required packages from the requirements.txt file
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Copy the port to access the Applicatin
EXPOSE 5000

# Set the entry point for the container
ENTRYPOINT ["python", "docker_monitor.py"]`