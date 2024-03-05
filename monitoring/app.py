import os
import hashlib
import docker
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = hashlib.sha256(os.urandom(32)).hexdigest()
socketio = SocketIO(app)

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
RECIPIENT_EMAILS = ['recipient1@gmail.com', 'recipient2@gmail.com']

client = docker.from_env()
containers = client.containers.list()

@app.route('/')
def index():
    containers_info = [{'id': c.id, 'name': c.name, 'status': c.status} for c in containers]
    return render_template('index.html', containers=containers_info)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    subject = data.get('subject')
    body = data.get('body')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = ', '.join(RECIPIENT_EMAILS)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, RECIPIENT_EMAILS, msg.as_string())

    return jsonify({'status': 'success'})

@socketio.on('connect')
def connect():
    print('Client connected')
    for container in containers:
        socketio.emit('container_status', {'id': container.id, 'name': container.name, 'status': container.status}, room=container.id)
    check_container_status()

def check_container_status():
    global containers
    while True:
        new_containers = client.containers.list()
        added_containers = [c for c in new_containers if c not in containers]
        removed_containers = [c for c in containers if c not in new_containers]

        for container in added_containers:
            socketio.emit('container_status', {'id': container.id, 'name': container.name, 'status': container.status}, room=container.id)

        for container in removed_containers:
            socketio.emit('container_status', {'id': container.id, 'name': container.name, 'status': 'removed'}, room=container.id)

        for container in new_containers:
            if container.status == 'exited':
                socketio.emit('container_stopped', {'id': container.id, 'name': container.name}, room=container.id)
                show_alert('danger', f"Container {container.name} has stopped!")
                send_email_notification(f"Container {container.name} has stopped!", f"Container {container.name} has
