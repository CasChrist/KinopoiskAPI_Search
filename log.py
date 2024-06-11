from datetime import datetime
import os

LOG_DIR = './logs'

def log(user_id, message):
    os.makedirs(LOG_DIR, exist_ok=True)
    filename = os.path.join(LOG_DIR, f'{user_id}.log')
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f'{datetime.now()} — {message}\n')
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'{datetime.now()} — {message}\n')