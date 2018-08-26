import os
import datetime
import traceback
from telethon import TelegramClient, sync, errors
from telethon.tl.functions import messages, channels
from telethon.tl.types import ChannelAdminRights, ChatInviteExported, Channel, Chat

#-----------------------------------------------------------------------------#
#-------------------------- Telegram Functions -------------------------------#
#-----------------------------------------------------------------------------#

# Return telegram client object.
# Default username = admin_login
def getClient(username=None):
    if username == None:
        raise Exception('Please specify a username.')

    session_file = username + '.session'
    return TelegramClient(os.path.join(SESSION_FOLDER,session_file), API_ID, API_HASH)


# Return True if name already exists within telegram. Else False
def dialogExists(client,dialog_name,type):
    dialogs = client.get_dialogs()
    for dialog in dialogs:
        if dialog.name == dialog_name and isinstance(dialog.entity,type):
            return True

    return False


# Return dialog object if name exists within telegram. Else None
def getDialog(client,dialog_name,type):
    if dialogExists(client,dialog_name,type):
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            if dialog.name == dialog_name and isinstance(dialog.entity,type):
                return dialog

    return None


# Return entity object if name exists within telegram. Else None
def getEntity(client,dialog_name,type):
    dialog = getDialog(client,dialog_name,type)
    if dialog != None:
        return dialog.entity

    return None


# Return a string of the current financial year
def getFinancialYear():
    year = int(datetime.datetime.now().strftime("%y"))
    month = int(datetime.datetime.now().strftime("%m"))

    if month >= 4:
        fin_year = 'AY' + str(year) + '/' + str(year+1)
    else:
        fin_year = 'AY' + str(year-1) + '/' + str(year)

    return fin_year


# Return True if channel is succesfully create, ELSE False
# Valid for:
# 1. Course Channel
# 2. Section Channel
#
# Returns dict:
# - status
# - message
# - channel_name
# - channel_link
def initialize_Channel(client=None,course_title='',section_number=''):
    results = {}

    if client == None:
        raise Exception('Client is invalid. Please connect to telegram client first.')

    if course_title == '':
        raise Exception('Please specify a course title at least; section number is optional.')

    fin_year = getFinancialYear()
    title = (fin_year + ' ' + course_title + ' ' + section_number).strip()

    # Create channel for specified user
    if dialogExists(client,title,Channel):
        results['status'] = False
        results['message'] = title + ' channel already exists within Telegram.'
    else:
        client(channels.CreateChannelRequest(title=title,about='This channel is for students in ' + title))

        channel_entity = getEntity(client,title,Channel)
        admin_rights = ChannelAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            invite_link=True,
            pin_messages=True,
            add_admins=True,
        )

        client(channels.EditAdminRequest(channel=channel_entity.id,user_id='@SMUCLEBot',admin_rights=admin_rights))
        results['status'] = True
        results['message'] = title + ' channel create.'

    invite_link = client(channels.ExportInviteRequest(getEntity(client,title,Channel).id))
    results['channel_name'] = title
    results['channel_link'] = invite_link.link

    return results


# Return True if groups are succesfully create, ELSE False
# Valid for:
# 1. Section Groups
# 2. Team Groups
#
# Returns dict:
# - status
# - message
# - group_name
# - group_link
def initialize_Group(client=None,course_title='',section_number='',team_number=''):
    results = {}

    if client == None:
        raise Exception('Client is invalid. Please connect to telegram client first.')

    if course_title == '' or section_number == '':
        raise Exception('Please specify a course title and a section number at least; team number is optional.')

    fin_year = getFinancialYear()
    title = (fin_year + ' ' + course_title + ' ' + section_number + team_number).strip()

    # Create groups for specified user
    if dialogExists(client,title,Chat):
        results['status'] = False
        results['message'] = title + ' group already exists within Telegram.'
    else:
        users = ['@rizzzy','@SMUCLEBot']
        client(messages.CreateChatRequest(users=users,title=title))

        results['status'] = True
        results['message'] = title + ' group create.'

    invite_link = client(messages.ExportChatInviteRequest(getEntity(client,title,Chat).id))
    results['group_name'] = title
    results['group_link'] = invite_link.link

    return results


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


if __name__ == "__main__":
    from tele_config import *
    try:
        client = getClient(ADMIN_USERNAME)
        client.connect()

        if not client.is_user_authorized():
            client.send_code_request(ADMIN_PHONE_NUMBER)
            try:
                client.sign_in(ADMIN_PHONE_NUMBER, input("Enter Code: "))
            except PhoneNumberUnoccupiedError:
                client.sign_up(ADMIN_PHONE_NUMBER, input("Enter Code: "))

        # RUN test methods here
        results = initialize_Group(client,'IS480','G4','T1')

        print(results)

        client.disconnect()

    except Exception as e:
        traceback.print_exc()
else:
    from Module_TeamManagement.src.tele_config import *
