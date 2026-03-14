from flask import Flask
from app.database import init_db
import datetime
import os

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = 'shuttlego-super-secret-key-change-in-prod'
    app.permanent_session_lifetime = datetime.timedelta(hours=8)

    from app.auth import auth_bp
    from app.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Init DB on first run
    db_path = os.path.join(os.path.dirname(__file__), '..', 'shuttlego.db')
    if not os.path.exists(db_path):
        with app.app_context():
            init_db()

    return app
