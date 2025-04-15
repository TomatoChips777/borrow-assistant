from flask import Blueprint, request, jsonify
import mysql.connector
import os
import requests
from datetime import datetime

users_blueprint = Blueprint('users', __name__)
UPLOAD_FOLDER = 'uploads/profile'

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='lc-ticketing-db-2'
    
)
cursor = db.cursor(dictionary=True)

def download_image(url):
    response = requests.get(url)
    ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
    filename = f"{int(datetime.now().timestamp())}{ext}"
    full_path = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with open(full_path, 'wb') as f:
        f.write(response.content)
    return f"profile/{filename}"

@users_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    picture = data.get('picture')
    token = data.get('token')

    if not all([email, name, picture, token]):
        return jsonify({'error': 'Missing required fields'}), 400

    cursor.execute("SELECT * FROM tbl_users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        updates = []
        params = []
        if not user['name']:
            updates.append("name = %s")
            params.append(name)
        if not user['image_url']:
            try:
                image_path = download_image(picture)
                updates.append("image_url = %s")
                params.append(image_path)
            except Exception as e:
                return jsonify({'error': 'Failed to download profile picture'}), 500
        if not user['token']:
            updates.append("token = %s")
            params.append(token)
        if updates:
            update_query = f"UPDATE tbl_users SET {', '.join(updates)} WHERE email = %s"
            params.append(email)
            cursor.execute(update_query, tuple(params))
            db.commit()

        cursor.execute("SELECT * FROM tbl_users WHERE email = %s", (email,))
        return jsonify(cursor.fetchone())
    else:
        try:
            image_path = download_image(picture)
            insert_query = "INSERT INTO tbl_users (name, email, role, image_url, token, status) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (name, email, 'student', image_path, token, 1))
            db.commit()
            cursor.execute("SELECT * FROM tbl_users WHERE email = %s", (email,))
            return jsonify(cursor.fetchone())
        except Exception as e:
            return jsonify({'error': 'Error inserting user'}), 500

@users_blueprint.route('/get-current-user', methods=['POST'])
def get_current_user():
    data = request.json
    user_id = data.get('id')
    email = data.get('email')

    if not user_id and not email:
        return jsonify({'error': 'ID or email is required'}), 400

    query = "SELECT * FROM tbl_users WHERE " + ("id = %s" if user_id else "email = %s")
    param = (user_id or email,)
    cursor.execute(query, param)
    result = cursor.fetchone()
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'User not found'}), 404

@users_blueprint.route('/get-all-users', methods=['GET'])
def get_all_users():
    cursor.execute("SELECT * FROM tbl_users")
    return jsonify(cursor.fetchall())

@users_blueprint.route('/update-user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name, email, role = data.get('name'), data.get('email'), data.get('role')
    cursor.execute("UPDATE tbl_users SET name=%s, email=%s, role=%s WHERE id=%s", (name, email, role, user_id))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'message': 'User updated successfully'})

@users_blueprint.route('/activate-deactivate-user/<int:user_id>', methods=['PUT'])
def toggle_user_status(user_id):
    status = request.json.get('status')
    if status not in [0, 1]:
        return jsonify({'success': False, 'message': 'Invalid status value. Use 1 or 0.'}), 400
    cursor.execute("UPDATE tbl_users SET status=%s WHERE id=%s", (status, user_id))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'message': f'User status updated to {"active" if status else "inactive"}'})

@users_blueprint.route('/add-user', methods=['POST'])
def add_user():
    data = request.json
    name, email, role = data.get('name'), data.get('email'), data.get('role')

    if not all([name, email, role]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    cursor.execute("SELECT id FROM tbl_users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({'success': False, 'message': 'User already exists'}), 409

    cursor.execute("INSERT INTO tbl_users (name, email, role) VALUES (%s, %s, %s)", (name, email, role))
    db.commit()
    return jsonify({'success': True, 'message': 'User created successfully'})
