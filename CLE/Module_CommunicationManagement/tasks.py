from datetime import datetime
from background_task import background
from Module_CommunicationManagement.src import tele_util

@background(schedule=0)
def test_tasks(message):
    print(message)

@background(schedule=0)
def sendMessage(username,chat_type,chat_name,message):
    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Running background event: Sending Telegram Message')

    client = tele_util.getClient(username)

    if chat_type == 'Group':
        tele_util.sendGroupMessage(client,chat_name,message)
    elif chat_type == 'Channel':
        tele_util.sendChannelMessage(client,chat_name,message)

    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Sent message to ('+ chat_type +'): ' + chat_name)
    tele_util.disconnectClient(client)

    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Ending background event: Sending Telegram Message')
