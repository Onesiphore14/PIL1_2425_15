from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/ifri_comotorage'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)
CORS(app)

# Import des routes
from routes.messaging import messaging_bp
app.register_blueprint(messaging_bp, url_prefix='/api/messaging')

# Import des événements Socket.IO
# from utils.socket_events import *

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)