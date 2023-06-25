import os

from dotenv import load_dotenv

load_dotenv()

BASE_TARGET_APPS_DIR = os.environ.get('BASE_DIR', '/')
APPS_CONFIG_FILE = 'apps.yml'
