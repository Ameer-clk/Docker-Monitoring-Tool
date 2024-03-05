FROM python:3.9-slim-buster

# Set environment variables
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libffi-dev \
        libpq-dev \
        python3-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Copy the app code
COPY . /app/

# Expose the Flask app port
EXPOSE 5000

# Start the Flask app
CMD ["flask", "run", "--debug"]
