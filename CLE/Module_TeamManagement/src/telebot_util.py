import telegram
from tele_config import BOT_TOKEN

#-----------------------------------------------------------------------------#
#------------------------ Telegram Bot Functions -----------------------------#
#-----------------------------------------------------------------------------#

def send_Message(message=None, group_name=None):
    bot = telegram.Bot(token=BOT_TOKEN)
    chat_id = None

    # Raise exception if no group_name is found
    if group_name == None:
        raise Exception("Please specify group name.")

    # Raise exception is no message was specified
    if message == None:
        raise Exception("Please specify a message.")

    # IF bot is added into a group, it will get an 'update'
    # This 'update' stores all the information about the group/supergroup,
    # thus, it can be use to identify said group/supergroup by their 'id' and 'title'
    for update in bot.getUpdates():
        if update.message.chat.type == 'group' and update.message.chat.title == group_name:
            chat_id = update.message.chat.id

    # Raise exception if group is specified but not found
    if chat_id == None:
        raise Exception("No such group. Please specify valid group name.")

    # Once group is identified as existing, send message
    bot.sendMessage(chat_id=chat_id, text=message)
