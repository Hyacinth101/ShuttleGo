import os
import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'audit.log')


def log(action: str, user: str = 'anonymous', detail: str = '', status: str = 'OK'):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] [{status}] user={user} action={action} detail={detail}\n"
    with open(LOG_PATH, 'a') as f:
        f.write(line)
