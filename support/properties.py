from logging import INFO
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CALENDER_ID = os.environ.get('CALENDAR_ID')
SCOPE = 'https://www.googleapis.com/auth/calendar.events'
TOKEN_FILE = 'token.json'
CLIENT_SECRET_FILE = 'client_secret.json'
LOG_LEVEL=INFO
LOG_DATE_FORMAT='%m-%d-%y %H:%M:%S'
LOG_FORMAT='[%(asctime)s] p%(process)s:%(thread)d {%(filename)s::%(funcName)s:%(lineno)d} %(levelname)s - %(message)s'
