from flask import Blueprint, render_template, session, jsonify, request, abort
from app.database import get_db
from app.auth import login_required, admin_required
from app.audit import log

main_bp = Blueprint('main', __name__)


# ── Pages ──────────────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    return render_template('login.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
                           username=session['username'],
                           role=session['role'])


@main_bp.route('/members')
@login_required
def members_page():
    return render_template('members.html',
                           username=session['username'],
                           role=session['role'])


@main_bp.route('/trips')
@login_required
def trips_page():
    return render_template('trips.html',
                           username=session['username'],
                           role=session['role'])


@main_bp.route('/bookings')
@login_required
def bookings_page():
    return render_template('bookings.html',
                           username=session['username'],
                           role=session['role'])


# ── API: Members ───────────────────────────────────────────────────────────────

@main_bp.route('/api/members', methods=['GET'])
@login_required
def api_members():
    db = get_db()
    if session['role'] == 'admin':
        rows = db.execute('''
            SELECT m.*, 
                   CASE WHEN d.DriverID IS NOT NULL THEN 'Driver'
                        WHEN p.PassengerID IS NOT NULL THEN 'Passenger'
                        ELSE m.MemberType END as ResolvedType
            FROM Member m
            LEFT JOIN Driver d ON m.MemberID = d.MemberID
            LEFT JOIN Passenger p ON m.MemberID = p.MemberID
        ''').fetchall()
    else:
        # Regular users can only see their own member profile
        member_id = db.execute(
            'SELECT member_id FROM users WHERE user_id=?', (session['user_id'],)
        ).fetchone()
        if not member_id or not member_id['member_id']:
            db.close()
            return jsonify([])
        rows = db.execute('SELECT * FROM Member WHERE MemberID=?',
                          (member_id['member_id'],)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@main_bp.route('/api/members', methods=['POST'])
@login_required
def api_add_member():
    if session['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    data = request.get_json()
    db = get_db()
    db.execute('''INSERT INTO Member (Name, Age, Gender, Email, ContactNumber, MemberType)
                  VALUES (?,?,?,?,?,?)''',
               (data['name'], data.get('age'), data.get('gender'),
                data['email'], data.get('contact'), data.get('type', 'Passenger')))
    db.commit()
    db.close()
    log('ADD_MEMBER', session['username'], f"email={data['email']}")
    return jsonify({'message': 'Member added'}), 201


@main_bp.route('/api/members/<int:mid>', methods=['DELETE'])
@login_required
def api_delete_member(mid):
    if session['role'] != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    db = get_db()
    db.execute('DELETE FROM Member WHERE MemberID=?', (mid,))
    db.commit()
    db.close()
    log('DELETE_MEMBER', session['username'], f"MemberID={mid}")
    return jsonify({'message': 'Deleted'}), 200


# ── API: Trips ─────────────────────────────────────────────────────────────────

@main_bp.route('/api/trips', methods=['GET'])
@login_required
def api_trips():
    db = get_db()
    rows = db.execute('''
        SELECT t.*, r.RouteName, r.Source, r.Destination,
               v.VehicleNumber, v.Model,
               m.Name as DriverName
        FROM Trip t
        LEFT JOIN Route r ON t.RouteID = r.RouteID
        LEFT JOIN Vehicle v ON t.VehicleID = v.VehicleID
        LEFT JOIN Driver d ON t.DriverID = d.DriverID
        LEFT JOIN Member m ON d.MemberID = m.MemberID
        ORDER BY t.TripDate DESC, t.ScheduledDepartureTime
    ''').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ── API: Bookings ──────────────────────────────────────────────────────────────

@main_bp.route('/api/bookings', methods=['GET'])
@login_required
def api_bookings():
    db = get_db()
    if session['role'] == 'admin':
        rows = db.execute('''
            SELECT b.*, m.Name as PassengerName,
                   r.RouteName, t.TripDate, t.ScheduledDepartureTime
            FROM Booking b
            LEFT JOIN Passenger p ON b.PassengerID = p.PassengerID
            LEFT JOIN Member m ON p.MemberID = m.MemberID
            LEFT JOIN Trip t ON b.TripID = t.TripID
            LEFT JOIN Route r ON t.RouteID = r.RouteID
            ORDER BY b.BookingTime DESC
        ''').fetchall()
    else:
        # Users see only their bookings
        uid = session['user_id']
        rows = db.execute('''
            SELECT b.*, r.RouteName, t.TripDate, t.ScheduledDepartureTime
            FROM Booking b
            LEFT JOIN Passenger p ON b.PassengerID = p.PassengerID
            LEFT JOIN Member m ON p.MemberID = m.MemberID
            LEFT JOIN users u ON u.member_id = m.MemberID
            LEFT JOIN Trip t ON b.TripID = t.TripID
            LEFT JOIN Route r ON t.RouteID = r.RouteID
            WHERE u.user_id = ?
            ORDER BY b.BookingTime DESC
        ''', (uid,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ── API: Stats for dashboard ───────────────────────────────────────────────────

@main_bp.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    db = get_db()
    stats = {
        'members':  db.execute('SELECT COUNT(*) FROM Member').fetchone()[0],
        'trips':    db.execute("SELECT COUNT(*) FROM Trip WHERE TripDate=date('now')").fetchone()[0],
        'bookings': db.execute('SELECT COUNT(*) FROM Booking').fetchone()[0],
        'vehicles': db.execute("SELECT COUNT(*) FROM Vehicle WHERE CurrentStatus='available'").fetchone()[0],
    }
    db.close()
    return jsonify(stats)
