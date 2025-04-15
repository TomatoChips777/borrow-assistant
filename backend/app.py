from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import smtplib
from email.message import EmailMessage
from routes.users import users_blueprint
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

# Serve static files from /uploads
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)

# Email route
@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    to = data.get('to')
    subject = data.get('subject')
    message = data.get('message')

    try:
        email = EmailMessage()
        email['From'] = 'goldenpaper777@gmail.com'
        email['To'] = to
        email['Subject'] = subject
        email.set_content(message)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('goldenpaper777@gmail.com', 'zqyw sufs jjdu euno')
            smtp.send_message(email)

        return jsonify({'message': 'Email sent successfully!'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Email failed to send.'}), 500

# Register user routes
app.register_blueprint(users_blueprint, url_prefix='/api/users')

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('User connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('User disconnected')

if __name__ == '__main__':
    socketio.run(app, port=5000)
