import os
import hashlib
from flask import Flask, render_template
from flask_socketio import SocketIO
import docker

app = Flask(__name__)
app.config['SECRET_KEY'] = hashlib.sha256(os.urandom(32)).hexdigest()
socketio = SocketIO(app, port=80)

client = docker.from_env()
containers = client.containers.list()

@app.route('/')
def index():
    containers_info = [{'id': c.id, 'name': c.name, 'status': c.status} for c in containers]
    return render_template('index.html', containers=containers_info)

@socketio.on('connect')
def connect():
    print('Client connected')
    for container in containers:
        socketio.emit('container_status', {'id': container.id, 'name': container.name, 'status': container.status}, room=container.id)
    check_container_status()

def check_container_status():
    global containers
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

    containers = new_containers
    socketio.sleep(5)
    check_container_status()

def show_alert(icon, message):
    """Show an alert using SweetAlert2."""
    socketio.emit('alert', {'icon': icon, 'message': message})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=80)
