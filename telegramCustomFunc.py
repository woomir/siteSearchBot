import telegram


def telegramSendMessage(month: str, day: str, siteNumber: int, camping: str, areaName="none"):
    chat_token = "1752254532:AAHM8-RftUAr3V5KRJ2SzaBp41G8JTTeHIE"
    bot = telegram.Bot(token=chat_token)
    if areaName == "none":
        telegramMessageText = camping + ': ' + month + ' ' + day + \
            '일 ' + str(siteNumber) + '개 예약 가능'
    else:
        telegramMessageText = camping + ': ' + month + ' ' + day + \
            '일 ' + areaName + '에 ' + str(siteNumber) + '개의 사이트가 있습니다.'
    bot.sendMessage(chat_id="-564369831", text=telegramMessageText)  # Official
    # bot.sendMessage(chat_id="1003456250", text=telegramMessageText)  # Test
