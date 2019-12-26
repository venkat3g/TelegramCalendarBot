import telegram.ext
from datetime import datetime

class CalendarBotHandler(telegram.ext.CommandHandler):
    
    def __init__(self, calanderService, calenderId, userEventStatusService):
        self._commands = ['upcoming', 'going', 'not', 'undecided', 'details', 'help', 'create']
        self._calendarService = calanderService
        self._calendar_id = calenderId
        self._userEventStatusService = userEventStatusService
        self._time = lambda event, key: datetime.strptime(event[key]['dateTime'], "%Y-%m-%dT%H:%M:%S%z")
        self._startTime = lambda event: self._time(event, 'start')
        self._endTime = lambda event: self._time(event, 'end')
        self._eventLink = lambda event: event['htmlLink']
        self._eventSummary = lambda event: event["summary"]
        self._eventSummaryWLinkTelegram = lambda event: "[%s](%s)" % (self._eventSummary(event), self._eventLink(event))
        self._eventFormattedDate = lambda event: self._startTime(event).strftime("%m/%d/%Y")
        self._eventFormattedStartTime = lambda event: self._startTime(event).strftime("%I:%M:%S%p")
        self._eventFormattedEndTime = lambda event: self._endTime(event).strftime("%I:%M:%S%p")
        super().__init__(self._commands, self._callback)

    def _is_command(self, message, botName, command):
        return message.startswith("/%s" % command) \
            or message.startswith("/%s%s" % (command, botName))
    
    def _is_command_upcoming(self, message, botName):
        return self._is_command(message, botName, "upcoming")
    
    def _is_command_going_to_event(self, message, botName):
        return self._is_command(message, botName, "going")
    
    def _is_command_not_going_to_event(self, message, botName):
        return self._is_command(message, botName, "not")

    def _is_command_undecided_about_event(self, message, botName):
        return self._is_command(message, botName, "undecided")

    def _is_command_get_event_details(self, message, botName):
        return self._is_command(message, botName, "details")

    def _is_command_help(self, message, botName):
        return self._is_command(message, botName, "help")
    
    def _is_command_create_event(self, message, botName):
        return self._is_command(message, botName, "create")

    def _callback(self, update, context):
        try:
            chatId = update.effective_chat.id
            message = update.effective_message.text
            botName = context.bot.name
            if self._is_command_upcoming(message, botName):
                self._send_events(context, chatId, update)

            elif self._is_command_going_to_event(message, botName):
                eventNumber = int(context.args[0]) if len(context.args) > 0 else 0
                self._going_to_event(context, chatId, update, eventNumber)

            elif self._is_command_not_going_to_event(message, botName):
                eventNumber = int(context.args[0]) if len(context.args) > 0 else 0
                self._not_going_to_event(context, chatId, update, eventNumber)

            elif self._is_command_undecided_about_event(message, botName):
                eventNumber = int(context.args[0]) if len(context.args) > 0 else 0
                self._undecided_about_event(context, chatId, update, eventNumber)

            elif self._is_command_get_event_details(message, botName):
                eventToSee = int(context.args[0]) if len(context.args) > 0 else 0
                self._see_event_details(context, chatId, eventToSee)

            elif self._is_command_create_event(message, botName):
                quickCreateString = self._get_quick_create_string(message, botName)
                self._quick_create_event(context, chatId, update, quickCreateString)

            elif self._is_command_help(message, botName):
                self._send_help_message(context, chatId)

            else:
                self.unsupportedCommand(context, chatId, message)
        except Exception as e:
            context.bot.send_message(chatId, "An exception occurred while processing command, contact developer(s)")
            print(e)

    def _get_quick_create_string(self, message, botName):
        command = "/create"
        quickCreateString = ""
        if message.find(botName) != -1:
            chrToSkip = len(command) + len(botName) + 1 # including space at the end
            quickCreateString = message[chrToSkip:]
        else:
            chrToSkip = len(command)
            quickCreateString = message[chrToSkip:]

        return quickCreateString

    def _get_upcoming_events(self):
        return self._calendarService.getUpcomingEvents(self._calendar_id)

    def _send_events(self, context, chatId, update):
        events = self._get_upcoming_events()

        # one index events since this has more meaning in a message form
        formattedEvent = lambda index, event: str(index + 1) + ". " + self._eventSummaryWLinkTelegram(event) + " - " + self._eventFormattedDate(event) \
                + "\n\t\t\t\t\t\t\t" + self._eventFormattedStartTime(event) + " - " + self._eventFormattedEndTime(event)

        eventsString = "\n".join([formattedEvent(index, e) for index, e in enumerate(events)])

        context.bot.send_message(chatId, "Events coming up:\n%s" % eventsString, telegram.ParseMode.MARKDOWN)

    def _get_user_name(self, update):
        return update.effective_user.full_name

    def _going_callback(self, userName, event):
        eventId = event["id"]
        self._calendarService.setGoingToEvent(self._calendar_id, eventId, userName)
        return "%s is going to %s" % (userName, self._eventSummaryWLinkTelegram(event))

    def _going_to_event(self, context, chatId, update, eventNumber):        
        self._update_event_on_google_cal(context, chatId, update, eventNumber, self._going_callback)

    def _not_going_callback(self, userName, event):
        eventId = event["id"]
        self._calendarService.setNotGoingToEvent(self._calendar_id,eventId, userName)
        return "%s is not going to %s" % (userName, self._eventSummaryWLinkTelegram(event))

    def _not_going_to_event(self, context, chatId, update, eventNumber):
        self._update_event_on_google_cal(context, chatId, update, eventNumber, self._not_going_callback)

    def _undecided_callback(self, userName, event):
        eventId = event["id"]
        self._calendarService.setUndecidedAboutEvent(self._calendar_id, eventId, userName)
        return "%s is undecided about %s" % (userName, self._eventSummaryWLinkTelegram(event))

    def _undecided_about_event(self, context, chatId, update, eventNumber):
        self._update_event_on_google_cal(context, chatId, update, eventNumber, self._undecided_callback)


    def _update_event_on_google_cal(self, context, chatId, update, eventNumber, calendarServiceCallback):
        index = eventNumber - 1
        message = "Invalid Event Number see /upcoming for event numbers"
        if index >= 0:
            userName = self._get_user_name(update)
            events = self._get_upcoming_events()
            if index < len(events):
                try:
                    message = calendarServiceCallback(userName, events[index])
                except Exception as e:
                    print(e)
                    message = "Unable to update the Google Calendar, please try again later."
        
        context.bot.send_message(chatId, message, telegram.ParseMode.MARKDOWN)

    def _see_event_details(self, context, chatId, eventToSee):
        events = self._get_upcoming_events()
        index = eventToSee - 1
        message = "Valid Event Number Required \n\t\t For Example: `/details 1`"
        if index >= 0 and index < len(events):
            description = lambda event: (event["description"] if "description" in event else "")
            dayAsStringEvent = lambda event: self._startTime(event).strftime("%a. %b %d, %Y")

            # one index events since this has more meaning in a message form
            formattedEventDescription = description(events[index])
            eventDesc = ""
            attendeeStatusString = None
            if len(formattedEventDescription) > 0:
                eventDesc = self._userEventStatusService.getDescriptionFromFormattedDescription(formattedEventDescription)
                attendeeStatusString = self._userEventStatusService.getAttendeeStatusString(formattedEventDescription)
            
            formattedEvent = lambda index, event: str(index + 1) + ". " + self._eventSummaryWLinkTelegram(event) \
                    + "\n`" + dayAsStringEvent(event) \
                    + "\nFrom " + self._eventFormattedStartTime(event) \
                        + " - " + self._eventFormattedEndTime(event) + '`' \
                    + (
                        "\nDescription:\n" + "%s" % eventDesc \
                        if len(eventDesc) > 0 else ""
                        ) \
                    + (
                        "\n\nAttendee Information:\n" + "%s" % attendeeStatusString \
                            if attendeeStatusString != None else ""
                    )
            message = formattedEvent(index, events[index])

        context.bot.send_message(chatId, "%s" % message, telegram.ParseMode.MARKDOWN)
    
    def _quick_create_event(self, context, chatId, update, quickCreateString):
        userName = self._get_user_name(update)
        result = self._calendarService.quickCreateEvent(self._calendar_id, quickCreateString)
        if "error" in result:
            context.bot.send_message(chatId, "%s" % (result["error"]))
        else:
            context.bot.send_message(chatId, "%s created %s" % (userName, self._eventSummaryWLinkTelegram(result)), telegram.ParseMode.MARKDOWN)
    
    def _send_help_message(self, context, chatId):
        helpMessage = "I currently support the following commands" \
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
        context.bot.send_message(chatId, helpMessage)

    def unsupportedCommand(self, context, chatId, command):
        context.bot.send_message(chatId, "I do not support the command %s yet" % command)

