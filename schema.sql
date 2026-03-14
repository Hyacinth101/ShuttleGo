-- ============================================================
-- SYSTEM TABLES (auth, roles) - separate from project tables
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,  -- bcrypt hash
    role        TEXT    NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
    member_id   INTEGER,           -- FK to Member (optional link)
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PROJECT TABLES (from Assignment 1 ER Diagram)
-- ============================================================

CREATE TABLE IF NOT EXISTS Member (
    MemberID         INTEGER PRIMARY KEY AUTOINCREMENT,
    Name             TEXT    NOT NULL,
    Image            TEXT,
    Age              INTEGER,
    Gender           TEXT,
    Email            TEXT    UNIQUE NOT NULL,
    ContactNumber    TEXT,
    MemberType       TEXT,
    RegistrationDate DATE    DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS Driver (
    DriverID           INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID           INTEGER UNIQUE NOT NULL REFERENCES Member(MemberID),
    LicenseNumber      TEXT    UNIQUE NOT NULL,
    LicenseExpiryDate  DATE,
    ExperienceYears    INTEGER,
    CurrentStatus      TEXT    DEFAULT 'available',
    Rating             REAL    DEFAULT 0.0,
    Status             TEXT    DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS Passenger (
    PassengerID           INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID              INTEGER UNIQUE NOT NULL REFERENCES Member(MemberID),
    EmergencyContact      TEXT,
    PreferredPaymentMethod TEXT,
    SpecialAssistance     TEXT,
    NotificationPreference TEXT,
    Status                TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS Vehicle (
    VehicleID        INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleNumber    TEXT    UNIQUE NOT NULL,
    Model            TEXT,
    Capacity         INTEGER,
    CurrentStatus    TEXT    DEFAULT 'available',
    GPSDeviceID      TEXT,
    RegistrationDate DATE
);

CREATE TABLE IF NOT EXISTS Route (
    RouteID             INTEGER PRIMARY KEY AUTOINCREMENT,
    RouteName           TEXT    NOT NULL,
    Source              TEXT,
    Destination         TEXT,
    IntermediateStops   TEXT,
    EstimatedDuration   INTEGER,
    DistanceKM          REAL,
    BaseFare            REAL,
    Status              TEXT    DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS Trip (
    TripID                  INTEGER PRIMARY KEY AUTOINCREMENT,
    RouteID                 INTEGER REFERENCES Route(RouteID),
    VehicleID               INTEGER REFERENCES Vehicle(VehicleID),
    DriverID                INTEGER REFERENCES Driver(DriverID),
    TripDate                DATE    NOT NULL,
    ScheduledDepartureTime  TIME,
    ScheduledArrivalTime    TIME,
    ActualDepartureTime     TIME,
    ActualArrivalTime       TIME,
    Status                  TEXT    DEFAULT 'scheduled',
    TotalSeats              INTEGER,
    AvailableSeats          INTEGER
);

CREATE TABLE IF NOT EXISTS Booking (
    BookingID          INTEGER PRIMARY KEY AUTOINCREMENT,
    PassengerID        INTEGER REFERENCES Passenger(PassengerID),
    TripID             INTEGER REFERENCES Trip(TripID),
    SeatNumber         INTEGER,
    BookingTime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    BookingStatus      TEXT    DEFAULT 'confirmed',
    FareAmount         REAL,
    QRCode             TEXT    UNIQUE,
    QRCodeURL          TEXT,
    VerificationStatus TEXT    DEFAULT 'pending',
    VerifiedAt         TIMESTAMP,
    VerifiedBy         INTEGER
);

CREATE TABLE IF NOT EXISTS PaymentTransaction (
    TransactionID    INTEGER PRIMARY KEY AUTOINCREMENT,
    BookingID        INTEGER REFERENCES Booking(BookingID),
    TransactionType  TEXT,
    Amount           REAL,
    TransactionDate  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod    TEXT,
    PaymentStatus    TEXT    DEFAULT 'pending',
    GatewayReference TEXT
);

CREATE TABLE IF NOT EXISTS VehicleMaintenance (
    MaintenanceID  INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID      INTEGER REFERENCES Vehicle(VehicleID),
    ServiceDate    DATE,
    ServiceType    TEXT,
    Cost           REAL,
    NextServiceDue DATE,
    Status         TEXT DEFAULT 'scheduled'
);

CREATE TABLE IF NOT EXISTS BookingCancellation (
    CancellationID     INTEGER PRIMARY KEY AUTOINCREMENT,
    BookingID          INTEGER REFERENCES Booking(BookingID),
    CancellationTime   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CancellationReason TEXT,
    RefundAmount       REAL,
    PenaltyAmount      REAL,
    ProcessedAt        TIMESTAMP,
    Status             TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS NoShowPenalty (
    PenaltyID      INTEGER PRIMARY KEY AUTOINCREMENT,
    BookingID      INTEGER REFERENCES Booking(BookingID),
    DetectionTime  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PenaltyAmount  REAL,
    Reason         TEXT,
    AutoGenerated  INTEGER DEFAULT 1,
    PaymentStatus  TEXT DEFAULT 'unpaid',
    WaivedBy       INTEGER
);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Default admin user (password: admin123)
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('admin', 'scrypt:32768:8:1$placeholder$hash_will_be_set_by_init', 'admin');

-- Sample regular user (password: user123)
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('anand', 'scrypt:32768:8:1$placeholder$hash_will_be_set_by_init', 'user');

-- Sample Members
INSERT OR IGNORE INTO Member (MemberID, Name, Age, Gender, Email, ContactNumber, MemberType) VALUES
(1, 'Ravi Kumar',    28, 'Male',   'ravi@shuttlego.in',   '9876543210', 'Passenger'),
(2, 'Priya Sharma',  34, 'Female', 'priya@shuttlego.in',  '9876543211', 'Driver'),
(3, 'Arjun Mehta',   25, 'Male',   'arjun@shuttlego.in',  '9876543212', 'Passenger'),
(4, 'Sneha Patel',   30, 'Female', 'sneha@shuttlego.in',  '9876543213', 'Passenger'),
(5, 'Dev Nair',      40, 'Male',   'dev@shuttlego.in',    '9876543214', 'Driver');

-- Sample Routes
INSERT OR IGNORE INTO Route (RouteID, RouteName, Source, Destination, DistanceKM, BaseFare, Status) VALUES
(1, 'Campus Express',   'IITGN Gate',    'Ahmedabad Railway Station', 35.5, 80.00,  'active'),
(2, 'City Shuttle',     'Palaj',         'Gandhinagar Sector 1',      12.0, 30.00,  'active'),
(3, 'Airport Connect',  'IITGN Gate',    'Ahmedabad Airport',         42.0, 120.00, 'active');

-- Sample Vehicles
INSERT OR IGNORE INTO Vehicle (VehicleID, VehicleNumber, Model, Capacity, CurrentStatus) VALUES
(1, 'GJ-01-AB-1234', 'Tata Winger',   12, 'available'),
(2, 'GJ-01-CD-5678', 'Force Traveller', 17, 'available'),
(3, 'GJ-01-EF-9012', 'Toyota Innova',  6, 'maintenance');

-- Sample Drivers
INSERT OR IGNORE INTO Driver (DriverID, MemberID, LicenseNumber, ExperienceYears, Rating, Status) VALUES
(1, 2, 'DL-GJ-2020-001', 8, 4.5, 'active'),
(2, 5, 'DL-GJ-2018-002', 12, 4.8, 'active');

-- Sample Passengers
INSERT OR IGNORE INTO Passenger (PassengerID, MemberID, PreferredPaymentMethod, Status) VALUES
(1, 1, 'UPI',   'active'),
(2, 3, 'Card',  'active'),
(3, 4, 'Cash',  'active');

-- Sample Trips
INSERT OR IGNORE INTO Trip (TripID, RouteID, VehicleID, DriverID, TripDate, ScheduledDepartureTime, TotalSeats, AvailableSeats, Status) VALUES
(1, 1, 1, 1, date('now'), '08:00', 12, 8, 'scheduled'),
(2, 2, 2, 2, date('now'), '09:30', 17, 15, 'scheduled'),
(3, 3, 1, 1, date('now'), '14:00', 12, 12, 'scheduled');

-- Sample Bookings
INSERT OR IGNORE INTO Booking (BookingID, PassengerID, TripID, SeatNumber, FareAmount, BookingStatus, QRCode) VALUES
(1, 1, 1, 3, 80.00,  'confirmed', 'QR-001-2024'),
(2, 2, 1, 5, 80.00,  'confirmed', 'QR-002-2024'),
(3, 3, 2, 2, 30.00,  'confirmed', 'QR-003-2024');
