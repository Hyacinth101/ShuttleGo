from app import create_app
from app.database import init_db

app = create_app()

if __name__ == '__main__':
    init_db()   # safe to call multiple times (uses IF NOT EXISTS)
    app.run(debug=True, port=5000)
