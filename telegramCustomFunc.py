import telegram


def telegramSendMessage(chatId: int, campName: str, date: str, areaName="none", term='none'):
    bot_token = "1730964681:AAFQ96aa9ARQajzKCpTZ3CfeiN_AmlheSMg"
    bot = telegram.Bot(token=bot_token)
    if areaName == "none" and term == "none":
        telegramMessageText = campName + ': ' + date + ' ' + ' 예약 가능'
    elif areaName == "none" and term != "none":
        telegramMessageText = campName + ': ' + date + ' ' + term + '박 예약 가능'
    elif areaName != "none" and term == "none":
        telegramMessageText = campName + ': ' + date + ' ' + areaName + '구역 예약 가능'
    bot.sendMessage(chat_id=str(chatId), text=telegramMessageText)
