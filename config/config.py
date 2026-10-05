
import os
import platform

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'network_traffic.db')

MODEL_DIR = os.path.join(BASE_DIR, 'ml')
MODEL_PATH = os.path.join(MODEL_DIR, 'trained_ids.pkl')

INCIDENTS_DIR = os.path.join(BASE_DIR, 'incidents')

CURRENT_OS = platform.system()

NETWORK_INTERFACE = None 

TIME_WINDOW = 2.0

ALERT_THRESHOLD = 0.85
