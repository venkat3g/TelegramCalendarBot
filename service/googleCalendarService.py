import json
import logging
import os
import sys
from datetime import datetime

import flask
from requests_oauthlib import OAuth2Session
from support.properties import SCOPE, TOKEN_FILE, CLIENT_SECRET_FILE

LOG = logging.getLogger(__name__)
_GOING = "is going to this event"
_NOT = "is not going to this event"
_UNDECIDED = "is undecided about this event"

class GoogleCalendarService(object):
    def __init__(self, userEventStatusService):
        self._userEventStatusService = userEventStatusService
        self._secret = self._get_secret_from_file()
        self._google = self._get_creds()

    def getCalendarEvents(self, calendarId):
        response = self._google.get(
            "https://www.googleapis.com/calendar/v3/calendars/%s/events" % calendarId)
        if response.ok:
            content = json.loads(response.text)["items"]
            LOG.info("Events: %s" % content)
        else:
            content = json.loads(response.text)
            LOG.info("Response from Google: %s" % content)

        return content

    def getUpcomingEvents(self, calendarId):
        try:
            response = self._google.get(
                "https://www.googleapis.com/calendar/v3/calendars/%s/events" % calendarId, 
                params={
                    "singleEvents" : True,
                    "orderBy" : "startTime",
                    "timeMin" : datetime.today().strftime("%Y-%m-%dT%H:%M:%S%zZ")
                    })
            if response.ok:
                content = json.loads(response.text)["items"]
                LOG.info("Upcoming events: %s" % content)
            else:
                content = json.loads(response.text)
                LOG.info("Response from Google: %s" % content)
        except Exception as e:
            LOG.info(e)
            content = []

        return content

    def _get_secret_from_file(self):
        with open(CLIENT_SECRET_FILE) as json_file:
            secret = json.load(json_file)
        return secret["web"]

    def _get_token_from_file(self):
        token = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE) as json_file:
                token = json.load(json_file)
        return token

    def _get_creds(self):
        secret = self._secret
        token = self._get_token_from_file()
        extra = {
            "client_id": secret["client_id"],
            'client_secret': secret["client_secret"]
        }
        google = OAuth2Session(secret["client_id"],
                               scope=SCOPE,
                               auto_refresh_url=secret["token_uri"],
                               auto_refresh_kwargs=extra,
                               token_updater=self.saveToken,
                               redirect_uri=secret['redirect_uris'][0],
                               token=token)

        return google

    def getCurrentEvent(self, calendarId, eventId):
        event = None
        res = self._google.get("https://www.googleapis.com/calendar/v3/calendars/%s/events/%s" % (calendarId, eventId))
        if res.ok:
            event = json.loads(res.text)
        return event

    def setGoingToEvent(self, calendarId, eventId, usersName):
        event = self.getCurrentEvent(calendarId, eventId)
        existingDescription = event["description"] if "description" in event else ""

        updatedDescription = self._userEventStatusService.getUpdatedDescToUpdateUserStatus(existingDescription, usersName, _GOING)

        res = self._google.patch(
            "https://www.googleapis.com/calendar/v3/calendars/%s/events/%s" % (calendarId, eventId),
            json={"description": updatedDescription},
            params={
                "sendUpdates": "none"
            }
            )
        LOG.info("Response after updating status to going: %s" % res.text)

    def setNotGoingToEvent(self, calendarId, eventId, usersName):
        event = self.getCurrentEvent(calendarId, eventId)
        existingDescription = event["description"] if "description" in event else ""

        updatedDescription = self._userEventStatusService.getUpdatedDescToUpdateUserStatus(existingDescription, usersName, _NOT)

        res = self._google.patch(
            "https://www.googleapis.com/calendar/v3/calendars/%s/events/%s" % (calendarId, eventId),
            json={"description": updatedDescription},
            params={
                "sendUpdates": "none"
            }
            )
        LOG.info("Response after updating status to not going: %s" % res.text)


    def setUndecidedAboutEvent(self, calendarId, eventId, usersName):
        event = self.getCurrentEvent(calendarId, eventId)
        existingDescription = event["description"] if "description" in event else ""

        updatedDescription = self._userEventStatusService.getUpdatedDescToUpdateUserStatus(existingDescription, usersName, _UNDECIDED)

        res = self._google.patch(
            "https://www.googleapis.com/calendar/v3/calendars/%s/events/%s" % (calendarId, eventId),
            json={"description": updatedDescription},
            params={
                "sendUpdates": "none"
            }
            )
        LOG.info("Response after updating status to undecided: %s" % res.text)

    def quickCreateEvent(self, calendarId, quickCreateString):
        result = {}
        res = self._google.post(
            "https://www.googleapis.com/calendar/v3/calendars/%s/events/quickAdd" % calendarId,
            params={
                "text": quickCreateString
            })
        if res.ok:
            LOG.info("Response after quick creating event: %s" % res.text)
            createdEvent = json.loads(res.text)
            result["summary"] = createdEvent["summary"]
            result["htmlLink"] = createdEvent["htmlLink"]
        else:
            errorMessage = "Could not quick create event %s"
            result["error"] = errorMessage % "contact developer"
            LOG.info(errorMessage % res.text)
        return result

    def authorize(self):
        secret = self._secret
        # Redirect user to Google for authorization
        authorization_url, state = self._google.authorization_url(
            secret['auth_uri'],
            access_type="offline",
            include_granted_scopes='true',
            prompt='consent'
        )

        self._state = state

        return authorization_url

    def setAccessToken(self, redirect_response):
        secret = self._secret
        state = self._state
        # Fetch the access token
        token = self._google.fetch_token(secret["token_uri"], client_secret=secret["client_secret"],
                                         authorization_response=redirect_response)

        with open(TOKEN_FILE, "w+") as token_file:
            json.dump(token, token_file)
    
    def saveToken(self, token):
        with open(TOKEN_FILE, "w+") as token_file:
            json.dump(token, token_file)