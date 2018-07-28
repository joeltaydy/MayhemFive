import os
from telethon import TelegramClient, sync
from telethon.tl.functions import messages
from telethon.errors import PhoneNumberUnoccupiedError, SessionPasswordNeededError
from Module_TeamManagement.models import Instructor

#-----------------------------------------------------------------------------#
#-------------------------- Telegram Functions -------------------------------#
#-----------------------------------------------------------------------------#

API_ID = '367454'
API_HASH = '1bf84fb9cec9b739bc9dc2a5fe97ee10'
SESSION_FOLDER = os.path.abspath('telegram_sessions')
ADMIN_SESSION = 'admin_login.session'

# TO-DO: Automated group creation
# Get telethon to create a user bot to create the groups in telegram
#
def initialize_Groups(instructor):
    session_name = ADMIN_SESSION

    if 

    client = TelegramClient(os.path.join(SESSION_FOLDER,session_name), API_ID, API_HASH)
    client.connect()

    # If first time login, user will be prompted to give code, sent via telegram
    # For subsequent login, the system will look for admin_login.session file in telegram_sessions
    if not client.is_user_authorized():
        client.send_code_request(<hp>,)
        try:
            user = client.sign_in(<hp>,, input('Enter code: '))
        except PhoneNumberUnoccupiedError:
            user = client.sign_up(<hp>, input('Enter code: '))
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
