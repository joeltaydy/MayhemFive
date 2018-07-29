import os
from telethon import TelegramClient, sync, errors
from telethon.tl.functions import messages, contacts
from telethon.tl.types import InputPhoneContact
from Module_TeamManagement.models import Student, Instructor, Assigned_Team, Teaching_Assistant
from tele_config import API_ID, API_HASH, SESSION_FOLDER, ADMIN_SESSION, ADMIN_PHONE_NUMBER, BOT_TOKEN, ADMIN_GROUP
import telebot_util as telebot

#-----------------------------------------------------------------------------#
#-------------------------- Telegram Functions -------------------------------#
#-----------------------------------------------------------------------------#

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
        except errors.PhoneNumberUnoccupiedError:
            user = client.sign_up(phone_number), input('Enter code: '))
        except errors.SessionPasswordNeededError:
            client.sign_in(password=getpass.getpass())

    # IF instructor is the one initializing the groups
    if instrcutor != None:
        sections = instructor.section

        try:
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
                # Subsequently, create telegram group, with the given list of numbers
                groupList = []
                for team_number,student_hps in team_studentDict.iteritems():
                    groupName = "CLE " + section.section_number + team_number
                    contactList = student_hps + assistant_contactList
                    groupList.append(groupName)

                    # Create group with list of contacts, with the associated groupName
                    client(messages.CreateChatRequest(users=contactList,title=groupName))

                # For each group created for that section, make the TA an admin
                # And add @SMUCLEBot into group
                dialogs = client.get_dialogs()
                for dialog in dialogs:
                    if dialog.name in groupList:
                        client(messages.AddChatUserRequest(chat_id=dialog.entity.id,user_id='@SMUCLEBot',fwd_limit=10))

                        for phone_number in assistant_contactList:
                            client(messages.EditChatAdminRequest(chat_id=dialog.entity.id,user_id=phone_number,is_admin=True))

        # Catching errors for CreateChatRequest method
        except errors.UserRestrictedError:
            message = 'ALERT, initialize_Groups function of tele_util.py threw an error. \
                        It seems that the user was reported as spam. He or she is unable to create chats or channels. \
                        Please refer to telethon api for more information: https://lonamiwebs.github.io/Telethon/methods/messages/create_chat.html'
            telebot.send_Message(message=message,group_name=ADMIN_GROUP)

        # Catching errors for CreateChatRequest method
        except errors.UsersTooFewError:
            message = 'ALERT, initialize_Groups function of tele_util.py threw an error. \
                        It seems that there are not enough users to create a telegram group chat. \
                        Please refer to telethon api for more information: https://lonamiwebs.github.io/Telethon/methods/messages/create_chat.html'
            telebot.send_Message(message=message,group_name=ADMIN_GROUP)

        # Catching errors for AddChatUserRequest method
        except errors.ChatAdminRequiredError:
            message = 'ALERT, initialize_Groups function of tele_util.py threw an error. \
                        It seems that chat admin privileges are required to do that in the specified chat. \
                        Please refer to telethon api for more information: https://lonamiwebs.github.io/Telethon/methods/messages/add_chat_user.html'
            telebot.send_Message(message=message,group_name=ADMIN_GROUP)

        # Catching errors for AddChatUserRequest and EditChatAdminRequest method
        except errors.ChatIdInvalidError:
            message = 'ALERT, initialize_Groups function of tele_util.py threw an error. \
                        It seems that the wrong chat id was parse. \
                        Please refer to telethon api for more information: https://lonamiwebs.github.io/Telethon/methods/messages.html'
            telebot.send_Message(message=message,group_name=ADMIN_GROUP)

    # ELSE, will run admin commands
    else:
        message = 'ALERT, your CLE web application has encountered an error. \
                    It seems that initialize_Groups function was called but a valid username was not specified. \
                    Sepcifically, an instructor\'s username.'
        telebot.send_Message(message=message,group_name=ADMIN_GROUP)

    client.disconnect()
