from datetime import datetime

class EventFormatter:
    def isAllDayEvent(self, event):
        raise NotImplementedError()

    def isStartAndEndOnSameDate(self, event):
        raise NotImplementedError()

    def getTime(self, event, key):
        raise NotImplementedError()

    def getStartTime(self, event):
        raise NotImplementedError()

    def getEndTime(self, event):
        raise NotImplementedError()

    def getEventLink(self, event):
        raise NotImplementedError()

    def getEventSummary(self, event):
        raise NotImplementedError()

    def getSummaryWLinkTelegram(self, event):
        raise NotImplementedError()

    def getFormattedStartTime(self, event):
        raise NotImplementedError()

    def getFormattedEndTime(self, event):
        raise NotImplementedError()

    def getFormattedDateOrDatesForEvent(self, event):
        raise NotImplementedError()

    def getDayOrDaysAsFormattedDates(self, event):
        raise NotImplementedError()

class GoogleEventFormatter(EventFormatter):

    def isAllDayEvent(self, event):
        return 'date' in event['start']

    def isStartAndEndOnSameDate(self, event):
        return self.getFormattedStartDate(event) == self.getFormattedEndDate(event)

    def getTime(self, event, key):
        time = None
        if 'dateTime' in event[key]:
            time = datetime.strptime(event[key]['dateTime'], "%Y-%m-%dT%H:%M:%S%z")
        elif 'date' in event[key]:
            time = datetime.strptime(event[key]['date'], "%Y-%m-%d")
        return time

    def getStartTime(self, event):
        return self.getTime(event, 'start')

    def getEndTime(self, event):
        return self.getTime(event, 'end')

    def getEventLink(self, event):
        return event['htmlLink']

    def getEventSummary(self, event):
        return event['summary']

    def getSummaryWLinkTelegram(self, event):
        return "[%s](%s)" % (self.getEventSummary(event), self.getEventLink(event))

    def getFormattedStartDate(self, event):
        return self.getStartTime(event).strftime("%m/%d/%Y")

    def getFormattedEndDate(self, event):
        return self.getEndTime(event).strftime("%m/%d/%Y")

    def getFormattedStartTime(self, event):
        return self.getStartTime(event).strftime("%I:%M:%S%p")

    def getFormattedEndTime(self, event):
        return self.getEndTime(event).strftime("%I:%M:%S%p")

    def getFormattedDateOrDatesForEvent(self, index, event):
        # one index events since this has more meaning in a message form
        eventFormatted = str(index + 1) + ". " + self.getSummaryWLinkTelegram(event) + " - " + self.getFormattedStartDate(event)
        if not self.isStartAndEndOnSameDate(event):
            eventFormatted += " to " + self.getFormattedEndDate(event)

        if not self.isAllDayEvent(event):
            eventFormatted += "\n\t\t\t\t\t\t\t" + self.getFormattedStartTime(event) + " - " + self.getFormattedEndTime(event)

        return eventFormatted

    def getDayOrDaysAsFormattedDates(self, event):
        dayOrDaysAsFormattedDateOrDates = self.getStartTime(event).strftime("%a. %b %d, %Y")
        if not self.isStartAndEndOnSameDate(event):
            dayOrDaysAsFormattedDateOrDates += " to " + self.getEndTime(event).strftime("%a. %b %d, %Y")

        return dayOrDaysAsFormattedDateOrDates