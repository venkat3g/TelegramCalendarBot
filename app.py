import json
import os
import sys
import re
import logging
from multiprocessing import current_process, process

import pprint
import telegram
import telegram.ext
from flask import Flask, escape, redirect, request

from service.userEventStatusService import UserEventStatusService
from service import calendarBotHandler as cbh
from service import googleCalendarService as gcs
from support.properties import BOT_TOKEN, CALENDER_ID, LOG_LEVEL, LOG_DATE_FORMAT, LOG_FORMAT, ENABLE_FLASK_SERVER

app = Flask(__name__)
app.secret_key = "secretToken"

def startBot():
    updater = telegram.ext.Updater(token=BOT_TOKEN, use_context=True)
    updater.start_polling(poll_interval=1)
    updater.dispatcher.add_handler(cbh.CalendarBotHandler(calendarService, CALENDER_ID, userEventStatusService))

@app.route("/test")
def test():
    return pprint.pformat(calendarService.getCalendarEvents(CALENDER_ID))

@app.route('/auth')
def authorize():
    return redirect(calendarService.authorize())
    
@app.route('/oauth2callback')
def oauth2callback():
    try:
        calendarService.setAccessToken(request.url)
        msg = "Success"
    except:
        msg = "Failure"
    return msg

def configureLogger():
    formatter = LOG_FORMAT
    dateFormat = LOG_DATE_FORMAT
    logging.basicConfig(
        format=formatter,
        datefmt=dateFormat,
        stream=sys.stdout,
        level=logging.INFO
        )

if __name__ == '__main__':
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    if current_process().name == "MainProcess":
        userEventStatusService = UserEventStatusService()
        calendarService = gcs.GoogleCalendarService(userEventStatusService)
        if not ENABLE_FLASK_SERVER:
            startBot()

    configureLogger()
    LOG = logging.getLogger(__name__)
    LOG.info("Started")
    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    if ENABLE_FLASK_SERVER:
        app.run('0.0.0.0', 8080, debug=True)
