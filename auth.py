from flask import Blueprint, request, session, jsonify, redirect, url_for
from werkzeug.security import check_password_hash
from app.database import get_db
from app.audit import log
import functools

auth_bp = Blueprint('auth', __name__)


# ── decorators ────────────────────────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        if session.get('role') != 'admin':
            log('UNAUTHORIZED_ACCESS', session.get('username', '?'), f.__name__, 'DENIED')
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ── routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect('/')          # served by static login.html via main blueprint


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Missing parameters'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    db.close()

    if not user or not check_password_hash(user['password'], password):
        log('LOGIN_FAIL', username, 'bad credentials', 'FAIL')
        return jsonify({'error': 'Invalid credentials'}), 401

    session.permanent = True
    session['user_id']  = user['user_id']
    session['username'] = user['username']
    session['role']     = user['role']

    log('LOGIN', username, f"role={user['role']}", 'OK')
    return jsonify({'message': 'Login successful', 'role': user['role']}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    user = session.get('username', 'unknown')
    session.clear()
    log('LOGOUT', user)
    return jsonify({'message': 'Logged out'}), 200


@auth_bp.route('/isAuth', methods=['GET'])
def is_auth():
    if 'user_id' not in session:
        return jsonify({'error': 'No session found'}), 401
    return jsonify({
        'message':  'User is authenticated',
        'username': session['username'],
        'role':     session['role']
    }), 200
