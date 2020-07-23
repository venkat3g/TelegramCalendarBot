from service.calendarBotHandler import CalendarBotHandler
from service.userEventStatusService import UserEventStatusService, _HIDDEN_CHAR, _START_OF_ATTENDEE_INFO
from service.googleCalendarService import _GOING, _NOT, _UNDECIDED
import unittest
from unittest import mock
import telegram
import json

botName = "@botName"

class CalendarBotHandlerTest(unittest.TestCase):
    calendarBotHandler = None

    @mock.patch("service.googleCalendarService.GoogleCalendarService")
    def setUp(self, mockGoogleCalendarService):
        self.mockGoogleCalendarService = mockGoogleCalendarService
        userEventStatusService = UserEventStatusService()
        self.calendarBotHandler = CalendarBotHandler(mockGoogleCalendarService, "calendarId", userEventStatusService)

    def createMockResourcesForTests(self):
        chatId = "chatId"
        update = mock.MagicMock()
        context = mock.MagicMock()
        update.effective_chat.id = chatId
        context.bot.name = botName
        return update, context, chatId

        
    def mockUpcomingEvents(self):
        with open("./service/eventResponseTest.json") as eventResponseText:
            self.mockGoogleCalendarService.getUpcomingEvents.return_value = json.load(eventResponseText)["items"]

    def test_callback_invalid_command(self):
        update, context, chatId = self.createMockResourcesForTests()
        command = "/invalid"
        update.effective_message.text = command
        
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, "I do not support the command %s yet" % command)

    def test_no_upcoming_events(self):
        update, context, chatId = self.createMockResourcesForTests()
        command = "/upcoming"
        update.effective_message.text = command
        self.mockGoogleCalendarService.getUpcomingEvents.return_value = []
        
        expectedFormattedEvents = ""
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, "Events coming up:\n%s" % expectedFormattedEvents, telegram.ParseMode.MARKDOWN)
    
    def test_two_upcoming_events(self):
        update, context, chatId = self.createMockResourcesForTests()
        command = "/upcoming"
        update.effective_message.text = command
        self.mockUpcomingEvents()
        
        expectedFormattedEvents = "1. [Star Wars: The Rise of Skywalker (2019)](starWarsHtmlLink) - 12/20/2019" \
            + "\n\t\t\t\t\t\t\t11:15:00PM - 02:10:00AM" \
            + "\n2. [Game Night](gameNightHtmlLink) - 12/28/2019" \
            + "\n\t\t\t\t\t\t\t05:00:00PM - 11:30:00PM"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, "Events coming up:\n%s" % expectedFormattedEvents, telegram.ParseMode.MARKDOWN)

    def test_going_to_event(self):
        update, context, chatId = self.createMockResourcesForTests()
        fullName = "full name"
        command = "/going 1"
        context.args = ['1']
        update.effective_user.full_name = fullName
        update.effective_message.text = command
        self.mockUpcomingEvents()
        
        formattedEventSummary = "[Star Wars: The Rise of Skywalker (2019)](starWarsHtmlLink)"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, "%s is going to %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

        command = "/going"
        context.args = []
        update.effective_message.text = command
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is going to %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

        command = "/going 2"
        context.args = ['2']
        update.effective_message.text = command
        formattedEventSummary = "[Game Night](gameNightHtmlLink)"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is going to %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

    def test_not_going_to_event(self):
        update, context, chatId = self.createMockResourcesForTests()
        fullName = "full name"
        command = "/not 1"
        context.args = ['1']
        update.effective_user.full_name = fullName
        update.effective_message.text = command
        self.mockUpcomingEvents()
        
        formattedEventSummary = "[Star Wars: The Rise of Skywalker (2019)](starWarsHtmlLink)"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, "%s is not going to %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

        command = "/not"
        context.args = []
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is not going to %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

        command = "/not 2"
        context.args = ['2']
        update.effective_message.text = command
        formattedEventSummary = "[Game Night](gameNightHtmlLink)"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is not going to %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

    def test_undecided_about_event(self):
        update, context, chatId = self.createMockResourcesForTests()
        fullName = "full name"
        command = "/undecided 1"
        context.args = ['1']
        update.effective_user.full_name = fullName
        update.effective_message.text = command
        self.mockUpcomingEvents()
        
        formattedEventSummary = "[Star Wars: The Rise of Skywalker (2019)](starWarsHtmlLink)"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is undecided about %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

        command = "/undecided"
        context.args = []
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is undecided about %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

        command = "/undecided 2"
        context.args = ['2']
        update.effective_message.text = command
        formattedEventSummary = "[Game Night](gameNightHtmlLink)"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, "%s is undecided about %s" % (fullName, formattedEventSummary), telegram.ParseMode.MARKDOWN)

    def test_invalid_number_for_going_not_undecided(self):
        update, context, chatId = self.createMockResourcesForTests()
        self.mockUpcomingEvents()
        update.effective_message.text = "/going 11"
        context.args = ['11']
        self.calendarBotHandler._callback(update, context)

        update.effective_message.text = "/not 123"
        context.args = ['123']
        self.calendarBotHandler._callback(update, context)

        update.effective_message.text = "/undecided 3"
        context.args = ['3']
        self.calendarBotHandler._callback(update, context)

        context.bot.send_message.assert_called_with(chatId, "Invalid Event Number see /upcoming for event numbers \n\t\t (or leave out number for first event)", telegram.ParseMode.MARKDOWN)
        self.assertEqual(context.bot.send_message.call_count, 3)
        self.assertEqual(context.bot.send_message.args[0], context.bot.send_message.args[1])
        self.assertEqual(context.bot.send_message.args[0], context.bot.send_message.args[2])

        update.effective_message.text = "/details 321"
        context.args = ['321']
        self.calendarBotHandler._callback(update, context)

        context.bot.send_message.assert_called_with(chatId, "Valid Event Number Required \n\t\t For Example: `/details 1` \n\t\t (or `/details` for first event)", telegram.ParseMode.MARKDOWN)

    def test_details_for_event(self):
        update, context, chatId = self.createMockResourcesForTests()
        fullName = "full name"
        command = "/details 1"
        context.args = ['1']
        update.effective_user.full_name = fullName
        update.effective_message.text = command
        self.mockUpcomingEvents()
        
        formattedEventDetails = "1. [Star Wars: The Rise of Skywalker (2019)](starWarsHtmlLink)"\
            +"\n`Fri. Dec 20, 2019\nFrom 11:15:00PM - 02:10:00AM`\nDescription:\ndescription."
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, formattedEventDetails, telegram.ParseMode.MARKDOWN)

        command = "/details"
        context.args = []
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, formattedEventDetails, telegram.ParseMode.MARKDOWN)

        command = "/details 2"
        context.args = ['2']
        update.effective_message.text = command
        formattedEventDetails = "2. [Game Night](gameNightHtmlLink)\n`Sat. Dec 28, 2019\nFrom 05:00:00PM - 11:30:00PM`"
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, formattedEventDetails, telegram.ParseMode.MARKDOWN)
    
    def test_details_for_event_w_user_status(self):
        update, context, chatId = self.createMockResourcesForTests()
        fullName = "full name"
        command = "/details 1"
        context.args = ['1']
        update.effective_user.full_name = fullName
        update.effective_message.text = command
        self.mockUpcomingEvents()

        events = self.mockGoogleCalendarService.getUpcomingEvents()
        events[0]["description"] = events[0]["description"] + "%s" % _START_OF_ATTENDEE_INFO + "%s%c%s" % (fullName, _HIDDEN_CHAR, _GOING)
        events[1]["description"] = "%s" % _START_OF_ATTENDEE_INFO + "%s%c%s" % (fullName, _HIDDEN_CHAR, _NOT)
        
        formattedEventDetails = "1. [Star Wars: The Rise of Skywalker (2019)](starWarsHtmlLink)"\
            + "\n`Fri. Dec 20, 2019\nFrom 11:15:00PM - 02:10:00AM`\nDescription:\ndescription." \
            + "\n\nAttendee Information:" \
            + "\n%s%c%s" % (fullName, _HIDDEN_CHAR, _GOING)
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, formattedEventDetails, telegram.ParseMode.MARKDOWN)

        command = "/details 2"
        context.args = ['2']
        update.effective_message.text = command
        formattedEventDetails = "2. [Game Night](gameNightHtmlLink)\n`Sat. Dec 28, 2019\nFrom 05:00:00PM - 11:30:00PM`"\
            + "\n\nAttendee Information:" \
            + "\n%s%c%s" % (fullName, _HIDDEN_CHAR, _NOT)
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_with(chatId, formattedEventDetails, telegram.ParseMode.MARKDOWN)

    def test_help_command(self):
        update, context, chatId = self.createMockResourcesForTests()
        expectedMessage = "I currently support the following commands" \
            + "\n/create - Quickly create an event" \
            + "\n/upcoming - See upcoming events" \
            + "\n/going <number> - Going to event" \
            + "\n\t\t Ex: /going 1" \
            + "\n/not <number> - Not going to specified event" \
            + "\n\t\t Ex: /not 1" \
            + "\n/undecided <number> - Undecided about specified event" \
            + "\n\t\t Ex: /undecided 1" \
            + "\n/details <number> - See additional information about specified event" \
            + "\n\t\t Ex: /details 1"
        command = "/help"
        update.effective_message.text = command
        self.calendarBotHandler._callback(update, context)
        context.bot.send_message.assert_called_once_with(chatId, expectedMessage)

    def test_quick_create_events_wo_bot_name(self):
        self.quick_create_events_w_command("/create")

    def test_quick_create_events_w_bot_name(self):
        self.quick_create_events_w_command("/create%s" % botName)

    def quick_create_events_w_command(self, command):
        update, context, chatId = self.createMockResourcesForTests()
        quickCreateString = "Event"
        htmlLink = "htmlLink"
        command = "%s %s" % (command, quickCreateString)
        fullName = "full name"
        update.effective_message.text = command
        update.effective_user.full_name = fullName

        self.mockGoogleCalendarService.quickCreateEvent.return_value = {
                    "htmlLink": "%s" % htmlLink,
                    "summary": "%s" % quickCreateString
                }

        self.calendarBotHandler._callback(update, context)

        expectedMessage = "%s created [%s](%s)" % (fullName, quickCreateString, htmlLink)
        context.bot.send_message.assert_called_once_with(chatId, expectedMessage, telegram.ParseMode.MARKDOWN)

    def test_error_creating_event(self):
        update, context, chatId = self.createMockResourcesForTests()
        error = "Could not create event"
        command = "/create event"
        fullName = "full name"
        update.effective_message.text = command
        update.effective_user.full_name = fullName

        self.mockGoogleCalendarService.quickCreateEvent.return_value = {
                    "error": error
                }

        self.calendarBotHandler._callback(update, context)

        expectedMessage = "%s" % error
        context.bot.send_message.assert_called_once_with(chatId, expectedMessage)

        command = '/create'
        update.effective_message.text = command
        self.calendarBotHandler._callback(update, context)

        expectedMessage = "You did not enter anything so an event will not be created.\n" \
            + "An example of this command: `/create Some Event on Tuesday 1-2pm`\n" \
            + "Or... `/create Some Event on July 30th 11-4pm`"

        context.bot.send_message.assert_called_with(chatId, expectedMessage, telegram.ParseMode.MARKDOWN)