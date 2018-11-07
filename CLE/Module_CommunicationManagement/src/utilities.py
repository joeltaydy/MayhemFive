def getTelegramChatJSON(telegram_chatObj):
    telegram_chat = {}

    telegram_chat = {
        'name': telegram_chatObj.name,
        'link': telegram_chatObj.link,
        'type': telegram_chatObj.type,
        'members': telegram_chatObj.members.split('_') if telegram_chatObj.members != None else [],
        'members_count': len(telegram_chatObj.members.split('_')) if telegram_chatObj.members != None else 0,
    }

    return telegram_chat
