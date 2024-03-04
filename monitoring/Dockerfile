FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask
RUN pip install flask-socketio

COPY . .

CMD ["python", "app.py"]
