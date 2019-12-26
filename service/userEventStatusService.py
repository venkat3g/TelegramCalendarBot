_START_OF_ATTENDEE_INFO = "\n\nTELEGRAM_BOT_INFO_BELOW_DO_NOT_MODIFY\n"
_HIDDEN_CHAR = chr(0x2800)

class UserEventStatusService(object):
    def _get_attendees_info(self, existingAttendeesStr):
        return existingAttendeesStr.splitlines()

    def _update_user_for_event(self, usersName, attendeeLines, updatedStatus):
        updatedAttendeeLines = []
        userFound = False
        for attendeeLine in attendeeLines:
            if attendeeLine.split(_HIDDEN_CHAR)[0] == usersName:
                updatedAttendeeLines.append("%s%c%s" % (usersName, _HIDDEN_CHAR, updatedStatus))
                userFound = True
            else:
                updatedAttendeeLines.append(attendeeLine)

        if not userFound:
            updatedAttendeeLines.append("%s%c%s" % (usersName, _HIDDEN_CHAR, updatedStatus))

        return updatedAttendeeLines
        
    def getUpdatedDescToUpdateUserStatus(self, formattedExistingDesc, usersName, updatedStatus):
        attendeeLines = []
        startAttendeeInfo = formattedExistingDesc.find(_START_OF_ATTENDEE_INFO)
        if startAttendeeInfo != -1:
            attendeeLines = self._get_attendees_info(formattedExistingDesc[startAttendeeInfo+len(_START_OF_ATTENDEE_INFO):])

        updatedAttendeeLines = self._update_user_for_event(usersName, attendeeLines, updatedStatus)

        description = self.getDescriptionFromFormattedDescription(formattedExistingDesc, startAttendeeInfo=startAttendeeInfo) \
             if startAttendeeInfo != -1 else formattedExistingDesc
        return description + _START_OF_ATTENDEE_INFO \
            + "\n".join(updatedAttendeeLines)

    def getAttendeeStatusString(self, formattedExistingDesc):
        startAttendeeInfo = formattedExistingDesc.find(_START_OF_ATTENDEE_INFO)
        return formattedExistingDesc[startAttendeeInfo+len(_START_OF_ATTENDEE_INFO):] if startAttendeeInfo != -1 else None

    def getDescriptionFromFormattedDescription(self, formattedExistingDesc, startAttendeeInfo=None):
        if startAttendeeInfo == None:
            startAttendeeInfo = formattedExistingDesc.find(_START_OF_ATTENDEE_INFO)
        return formattedExistingDesc[0:startAttendeeInfo] if startAttendeeInfo != -1 else formattedExistingDesc
