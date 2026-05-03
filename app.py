import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from models import db, Admin
from auth_routes import auth_bp
from opp_routes import opp_bp

app = Flask(__name__, static_folder='sky/static')

# --- Configuration ---
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "fallback_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certifyme.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True, origins=["*"])

# --- Initialize Plugins ---
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized. Please log in."}), 401

# --- Register API Routes (IMPORTANT: Keep BEFORE frontend routes) ---
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(opp_bp, url_prefix='/opp')


# ==========================================
# FRONTEND SERVING
# ==========================================

FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sky')

@app.route('/')
def serve_ui():
    return send_from_directory(FRONTEND_FOLDER, 'admin.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(FRONTEND_FOLDER, 'static'), filename)



# ==========================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    