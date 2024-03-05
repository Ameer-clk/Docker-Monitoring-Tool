import time
import docker
from flask_socketio import SocketIO

# Initialize the SocketIO object
socketio = SocketIO()

def check_container_status():
    client = docker.from_env()
    container = client.containers.get('my_container') # replace with your container name or ID
    while True:
        time.sleep(60) # check every minute
        if container.status != 'running':
            user = User.query.filter_by(id=1).first() # replace with the user ID that should receive notifications
            socketio.emit('container_status', {'status': 'down'}, room=user.id)

# Initialize the Flask application and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
socketio.init_app(app)

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
    return socketio.serve_forever()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    # Start the container status monitoring thread
    thread = Thread(target=check_container_status)
    thread.start()

    # Start the Flask application and SocketIO
    app.run(debug=True, host='0
