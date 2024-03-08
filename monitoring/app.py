import time
import docker
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO

# Initialize the SocketIO object
socketio = SocketIO()

# Initialize the Flask application and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
socketio.init_app(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Define the User and Notification models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Define the routes for the application
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('notifications'))

        flash('Login unsuccessful. Please check your username and password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/add_notification', methods=['POST'])
@login_required
def add_notification():
    name = request.form['name']
    description = request.form['description']

    new_notification = Notification(name=name, description=description, user_id=current_user.id)
    db.session.add(new_notification)
    db.session.commit()

    return redirect(url_for('notifications'))

@app.route('/socket.io/<path:path>')
def handle_socketio(path):
    socketio.emit('container_status', {'status': 'running'}, room=current_user.id)
    return socketio.handle_request()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Start the container status monitoring thread
def check_container_status():
    client = docker.from_env()
    container = client.containers.get('my_container') # replace with your container name or ID
    while True:
        time.sleep(60) # check every minute
        if container
