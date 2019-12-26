from service.googleCalendarService import GoogleCalendarService
from service.userEventStatusService import _START_OF_ATTENDEE_INFO, _HIDDEN_CHAR, UserEventStatusService
import unittest
import mock
import datetime
import json

class GoogleCalendarServiceTest(unittest.TestCase):
    googleCalendarService = None

    @mock.patch("service.googleCalendarService.OAuth2Session")
    def setUp(self, mockOAuth2Session):
        mockOAuth2Session.return_value = mockOAuth2Session
        self.calendarId = "calendarId"
        self.mockOAuth2Session = mockOAuth2Session
        userEventStatusService = UserEventStatusService()
        self.googleCalendarService = GoogleCalendarService(userEventStatusService)

    def test_get_calendar_events(self):
        with open("./service/eventResponseTest.json") as eventResponseText:
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = eventResponseText.read()
        events = self.googleCalendarService.getCalendarEvents(self.calendarId)
        self.assertEqual(len(events), 2)
        self.mockOAuth2Session.get.assert_called_once_with('https://www.googleapis.com/calendar/v3/calendars/%s/events' % self.calendarId)

    def test_get_upcoming_events(self):
        with open("./service/eventResponseTest.json") as eventResponseText:
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = eventResponseText.read()
        events = self.googleCalendarService.getUpcomingEvents("calendarId")
        self.assertEqual(len(events), 2)
        self.assertEqual(self.mockOAuth2Session.get.call_args.args[0], 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % self.calendarId)
        self.assertIn("params", self.mockOAuth2Session.get.call_args.kwargs)
        self.assertIn("singleEvents", self.mockOAuth2Session.get.call_args.kwargs['params'])
        self.assertIn("orderBy", self.mockOAuth2Session.get.call_args.kwargs['params'])
        self.assertIn("timeMin", self.mockOAuth2Session.get.call_args.kwargs['params'])

    def test_set_going_to_event_no_existing_attendees(self):
        with open("./service/eventResponseTest.json") as eventResponseText:
            events = json.load(eventResponseText)["items"]
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = json.dumps(events[0])

        eventId = events[0]["id"]
        userName = "userName"
        expectedDescription = events[0]["description"] + _START_OF_ATTENDEE_INFO \
            + "%s%cis going to this event" % (userName, _HIDDEN_CHAR)
        self.googleCalendarService.setGoingToEvent(self.calendarId, eventId, userName)
        self.verifyUpdatedUserStatusForEvent(eventId, expectedDescription)

    def test_set_going_to_event_with_existing_attendees(self):
        userName = "userName"
        with open("./service/eventResponseTest.json") as eventResponseText:
            events = json.load(eventResponseText)["items"]
            expectedDescription = events[0]["description"] + _START_OF_ATTENDEE_INFO \
                + "%s%cis going to this event" % (userName, _HIDDEN_CHAR)

            # update description to act like a user is currently not going    
            events[0]["description"] = events[0]["description"] + _START_OF_ATTENDEE_INFO \
                + "%s%cis not going to this event" % (userName, _HIDDEN_CHAR)
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = json.dumps(events[0])

        eventId = events[0]["id"]
        self.googleCalendarService.setGoingToEvent(self.calendarId, eventId, userName)
        self.verifyUpdatedUserStatusForEvent(eventId, expectedDescription)

    def test_set_not_going_to_event_no_existing_attendees(self):
        with open("./service/eventResponseTest.json") as eventResponseText:
            events = json.load(eventResponseText)["items"]
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = json.dumps(events[0])

        eventId = events[0]["id"]
        userName = "userName"
        expectedDescription = events[0]["description"] + _START_OF_ATTENDEE_INFO \
            + "%s%cis not going to this event" % (userName, _HIDDEN_CHAR)
        self.googleCalendarService.setNotGoingToEvent(self.calendarId, eventId, userName)
        self.verifyUpdatedUserStatusForEvent(eventId, expectedDescription)

    def test_set_not_going_to_event_with_existing_attendees(self):
        userName = "userName"
        with open("./service/eventResponseTest.json") as eventResponseText:
            events = json.load(eventResponseText)["items"]
            expectedDescription = events[0]["description"] + _START_OF_ATTENDEE_INFO \
                + "%s%cis not going to this event" % (userName, _HIDDEN_CHAR)

            # update description to act like a user is currently going    
            events[0]["description"] = events[0]["description"] + _START_OF_ATTENDEE_INFO \
                + "%s%cis going to this event" % (userName, _HIDDEN_CHAR)
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = json.dumps(events[0])

        eventId = events[0]["id"]
        self.googleCalendarService.setNotGoingToEvent(self.calendarId, eventId, userName)
        self.verifyUpdatedUserStatusForEvent(eventId, expectedDescription)

    def test_set_undecided_about_event_no_existing_attendees(self):
        with open("./service/eventResponseTest.json") as eventResponseText:
            events = json.load(eventResponseText)["items"]
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = json.dumps(events[0])

        eventId = events[0]["id"]
        userName = "userName"
        expectedDescription = events[0]["description"] + _START_OF_ATTENDEE_INFO \
            + "%s%cis undecided about this event" % (userName, _HIDDEN_CHAR)
        self.googleCalendarService.setUndecidedAboutEvent(self.calendarId, eventId, userName)
        self.verifyUpdatedUserStatusForEvent(eventId, expectedDescription)

    def test_set_undecided_about_event_with_existing_attendees(self):
        userName = "userName"
        with open("./service/eventResponseTest.json") as eventResponseText:
            events = json.load(eventResponseText)["items"]
            expectedDescription = events[0]["description"] + _START_OF_ATTENDEE_INFO \
                + "%s%cis undecided about this event" % (userName, _HIDDEN_CHAR)

            # update description to act like a user is currently going    
            events[0]["description"] = events[0]["description"] + _START_OF_ATTENDEE_INFO \
                + "%s%cis going to this event" % (userName, _HIDDEN_CHAR)
            (self.mockOAuth2Session.get.return_value).ok = True
            (self.mockOAuth2Session.get.return_value).text = json.dumps(events[0])

        eventId = events[0]["id"]
        self.googleCalendarService.setUndecidedAboutEvent(self.calendarId, eventId, userName)
        self.verifyUpdatedUserStatusForEvent(eventId, expectedDescription)

    def verifyUpdatedUserStatusForEvent(self, eventId, expectedDescription):
        self.mockOAuth2Session.get.assert_called_once_with('https://www.googleapis.com/calendar/v3/calendars/%s/events/%s' % (self.calendarId, eventId))
        self.assertEqual(self.mockOAuth2Session.patch.call_args.args[0], 'https://www.googleapis.com/calendar/v3/calendars/%s/events/%s' % (self.calendarId, eventId))
        self.assertIn("params", self.mockOAuth2Session.patch.call_args.kwargs)
        data = self.mockOAuth2Session.patch.call_args.kwargs["json"]
        params = self.mockOAuth2Session.patch.call_args.kwargs["params"]

        self.assertIn("sendUpdates", params)
        self.assertEqual("none", params["sendUpdates"])

        self.assertIn("description", data)

        self.assertEqual(expectedDescription, data["description"])

    def test_quick_create_params(self):
        htmlLink = "htmlLink"
        quickCreateString = "Event"
        (self.mockOAuth2Session.post.return_value).ok = True
        (self.mockOAuth2Session.post.return_value).text = json.dumps({
                    "status": "confirmed",
                    "htmlLink": "%s" % htmlLink,
                    "summary": "%s" % quickCreateString
                })

        result = self.googleCalendarService.quickCreateEvent(self.calendarId, quickCreateString)
        self.assertEqual(self.mockOAuth2Session.post.call_args.args[0], 'https://www.googleapis.com/calendar/v3/calendars/%s/events/quickAdd' % self.calendarId)
        params = self.mockOAuth2Session.post.call_args.kwargs["params"]

        self.assertIn("text", params)
        self.assertEqual(quickCreateString, params["text"])
        
        self.assertEqual(result["summary"], quickCreateString)
        self.assertEqual(result["htmlLink"], htmlLink)
