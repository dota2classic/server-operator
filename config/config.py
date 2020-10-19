from dotenv import load_dotenv
load_dotenv()
import os

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT'))
