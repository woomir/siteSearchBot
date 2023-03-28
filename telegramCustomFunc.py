import telegram
import asyncio

with open("./token.txt") as f:
    lines = f.readlines()
    token = lines[0].strip()


async def telegramSendMessage(chatId: str, campName: str, date: str, areaName="none", term='none'):
    bot = telegram.Bot(token=token)
    if areaName == "none" and term == "none":
        telegramMessageText = campName + ': ' + date + ' ' + ' 예약 가능'
    elif areaName == "none" and term != "none":
        telegramMessageText = campName + ': ' + date + ' ' + term + '박 예약 가능'
    elif areaName != "none" and term == "none":
        telegramMessageText = campName + ': ' + date + ' ' + areaName + ' 예약 가능'
    await bot.sendMessage(chat_id=str(chatId), text=telegramMessageText)


async def telegramSimpleMessage(chatId: str, text: str):
    bot = telegram.Bot(token=token)
    await bot.sendMessage(chat_id=chatId, text=text)
