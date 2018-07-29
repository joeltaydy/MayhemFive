import os
from telethon import TelegramClient, sync
from telethon.tl.functions import messages, contacts
from telethon.tl.types import InputPhoneContact
from telethon.errors import PhoneNumberUnoccupiedError, SessionPasswordNeededError
from Module_TeamManagement.models import Student, Instructor, Assigned_Team, Teaching_Assistant
from tele_config import API_ID, API_HASH, SESSION_FOLDER, ADMIN_SESSION, ADMIN_PHONE_NUMBER

#-----------------------------------------------------------------------------#
#-------------------------- Telegram Functions -------------------------------#
#-----------------------------------------------------------------------------#

# TO-DO:
# Get CLE BOT to send messages
def send_Message(username=None, message=None, group=None):
    session_name = ADMIN_SESSION
    phone_number = ADMIN_PHONE_NUMBER

    client = TelegramClient(os.path.join(SESSION_FOLDER,session_name), API_ID, API_HASH)
    client.connect()

    # If first time login, user will be prompted to give code, sent via telegram
    # For subsequent login, the system will look for admin_login.session file in telegram_sessions
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        try:
            user = client.sign_in(phone_number), input('Enter code: '))
        except PhoneNumberUnoccupiedError:
            user = client.sign_up(phone_number), input('Enter code: '))
        except SessionPasswordNeededError:
            client.sign_in(password=getpass.getpass())

    client(messages.SendMessageRequest(peer=group,message=message))


def initialize_Groups(username=None):
    session_name = ADMIN_SESSION
    phone_number = ADMIN_PHONE_NUMBER
    instructor = None

    if username != None:
        instructor = Instructor.objects.get(username=username)
        session_name = str(instructor.username) + '.session'
        phone_number = instructor.phone_number

    client = TelegramClient(os.path.join(SESSION_FOLDER,session_name), API_ID, API_HASH)
    client.connect()

    # If first time login, user will be prompted to give code, sent via telegram
    # For subsequent login, the system will look for admin_login.session file in telegram_sessions
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        try:
            user = client.sign_in(phone_number), input('Enter code: '))
        except PhoneNumberUnoccupiedError:
            user = client.sign_up(phone_number), input('Enter code: '))
        except SessionPasswordNeededError:
            client.sign_in(password=getpass.getpass())

    # IF instructor is the one initializing the groups
    if instrcutor != None:
        sections = instructor.section

        # Loop through every section that's in-charge by the instructor
        for section in sections:
            teams = Assigned_Team.objects.all().filter(section=section)
            assistants = Teaching_Assistant.objects.all().filter(section=section)
            assistant_contactList = [assistant.phone_number for assistant in assistants]
            student_contactList = []
            team_studentDict = {}

            # For all the team within that section, retrieve student's contact number and store is in a list
            # And categorize the students into their teams
            # Format of dictionary:
            # Team_Number
            # |- [phone_number_1]
            # |- [phone_number_2]
            # |- [phone_number_3]
            # |- ...
            #
            for team in teams:
                student = team.student
                student_contact = InputPhoneContact(
                                        client_id=0,
                                        phone=str(student.phone_number),
                                        first_name=student.firstname,
                                        last_name=student.lastname
                                    )
                student_contactList.append(student_contact)

                try:
                    team_studentDict[team.team_number].append(str(student.phone_number))
                except:
                    team_studentDict[team.team_number] = [str(student.phone_number)]

            # Add list of student's contacts into the contact list of client (in this case,it's the professors number)
            client(contacts.ImportContactsRequest(contactList))

            # For each team_number, retrieve list of student's number and add assistant's number into list
            # Subsequently, create telegram group with the list of numbers
            groupList = []
            for team_number,student_hps in team_studentDict.iteritems():
                groupName = "CLE " + section.section_number + team_number
                contactList = student_hps + assistant_contactList
                groupList.append(groupName)

                # Create group with list of contacts, with the associated groupName
                client(messages.CreateChatRequest(users=contactList,title=groupName))

                # TO-DO:
                # Add CLE bot into group

            # For each group created for that section, make the TA an admin
            dialogs = client.get_dialogs()
            for dialog in dialogs:
                if dialog.name in groupList:
                    for phone_number in assistant_contactList:
                        client(messages.EditChatAdminRequest(chat_id=dialog,user_id=phone_number,is_admin=True))

    # ELSE, will run admin commands
    else:
        # Program admin commands here
