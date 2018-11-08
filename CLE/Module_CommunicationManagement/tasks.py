from datetime import datetime
from background_task import background
from Module_CommunicationManagement.src import tele_util

@background(schedule=0)
def test_tasks(message):
    print(message)

@background(schedule=0)
def sendMessage(username,chat_name,message):
    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Running background event: Sending Telegram Message')

    client = tele_util.getClient(username)

    if telegram_chat_type == 'Group':
        tele_util.sendGroupMessage(client,chat_name,message)
    elif telegram_chat_type == 'Channel':
        tele_util.sendChannelMessage(client,chat_name,message)

    tele_util.disconnectClient(client)

    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Ending background event: Sending Telegram Message')
