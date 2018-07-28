import os
from telethon import TelegramClient, sync
from telethon.tl.functions import messages
from telethon.errors import PhoneNumberUnoccupiedError, SessionPasswordNeededError

#-----------------------------------------------------------------------------#
#-------------------------- Telegram Functions -------------------------------#
#-----------------------------------------------------------------------------#

config_file = os.path.join(os.path.abspath('telegram_config'),'telegram_config.py')

# TO-DO: Automated group creation
# Get telethon to create a user bot to create the groups in telegram
# Concerns:
#   1. How to create group with students inside if we do not have their telegram username?
#
def create_Group(courseInfo):
    client = TelegramClient(config_file.ADMIN_LOGIN_SESSION, config_file.API_ID, config_file.API_HASH)
    client.connect()

    # If first time login, user will be prompted to give code, sent via telegram
    # For subsequent login, the system will look for admin_login.session file in telegram_sessions
    if not client.is_user_authorized():
        client.send_code_request(config_file.PHONE_NUMBER)
        try:
            user = client.sign_in(config_file.PHONE_NUMBER, input('Enter code: '))
        except PhoneNumberUnoccupiedError:
            user = client.sign_up(config_file.PHONE_NUMBER, input('Enter code: '))
        except SessionPasswordNeededError:
            client.sign_in(password=getpass.getpass())

    # IF USER_ADMIN is instructor in group, run this:
    #   client(messages.CreateChatRequest([student1,student2],GROUP_NAME))
    #
    # ELSE:
    #   client(messages.CreateChatRequest([instructor,student1,student2],GROUP_NAME))
    #   Get chat_id of group
    #   Add Instructor as admin
    #   client(messages.EditChatAdminRequest(chat_id=chat_id,user_id=instructo,is_admin=True))
    #   Remove self from group created
