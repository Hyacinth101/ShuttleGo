# ShuttleGo
Databases (CS: 432) Project Work

Assigment 2, Web UI 

##  Project Structure

```
shuttlego/
├── run.py                  ← entry point
├── requirements.txt
├── sql/
│   └── schema.sql          ← all tables + seed data
├── logs/                   ← audit.log goes here
└── app/
    ├── __init__.py         ← Flask factory
    ├── database.py         ← SQLite connection
    ├── auth.py             ← login/logout/session + decorators
    ├── audit.py            ← audit logger
    ├── routes.py           ← all API + page routes
    └── templates/
        ├── login.html      ← bold transport-themed login
        ├── base.html       ← shared sidebar layout
        ├── dashboard.html  ← stats + today's trips
        ├── members.html    ← member portfolio
        ├── trips.html      ← trips table
        └── bookings.html   ← bookings table
```
##  How to Run

1. Download and extract the ZIP file  
2. Open a terminal in the project folder  
3. Run the following commands:

```
cd shuttlego
pip install flask werkzeug
python run.py
```

4. Open your browser and go to:

```
http://localhost:5000
```
