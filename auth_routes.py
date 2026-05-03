from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Auth route working"}), 200

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    required_fields = ["full_name", "email", "password", "confirm_password"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "All fields are required"}), 400
        
    if data['password'] != data['confirm_password']:
        return jsonify({"error": "Passwords do not match"}), 400
        
    if len(data['password']) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Account with this email already exists"}), 409

    hashed_pw = generate_password_hash(data['password'], method='scrypt')
    new_admin = Admin(full_name=data['full_name'], email=data['email'], password_hash=hashed_pw)
    
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({"message": "Account created successfully"}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember_me', False)

    admin = Admin.query.filter_by(email=email).first()

    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(admin, remember=remember)
    return jsonify({"message": "Logged in successfully", "admin_name": admin.full_name}), 200

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    admin = Admin.query.filter_by(email=email).first()
    if admin:
        reset_token = str(uuid.uuid4())
        print(f"INTERNAL LOG: Reset link generated: http://localhost:3000/reset?token={reset_token}")
        
    return jsonify({"message": "If that email is in our system, we have sent a reset link."}), 200