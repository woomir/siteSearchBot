import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from boto3.dynamodb.conditions import Key
import jinha
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform

campName = ['울주해양레포츠센터', '대저캠핑장', '삼락캠핑장']
jinhaDb = []
jinhaDate = []
jinhaTerm = []
jinhaChatId = []

daejeoDb = []
daejeoDate = []
daejeoTerm = []
daejeoChatId = []

samrakDb = []
samrakDate = []
samrakTerm = []
samrakChatId = []

session = boto3.session.Session(profile_name='siteSearch')


def dbScan(dynamodb=None):
    dynamodb = session.resource('dynamodb')  # bucket 목록
    table = dynamodb.Table('siteSearchBot_campInfo')

    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Items']


if __name__ == '__main__':
    campDb = dbScan()
    if campDb:
        print("Get campDb succeeded:")
        print(campDb)
        # 진하캠핑장 구독 데이터 추출
        for db in campDb:
            if db['campName'] == campName[0]:
                if 'selectedDate' in db:
                    for date in db['selectedDate']:
                        jinhaDate.append(date['startDate'])
                        jinhaTerm.append(date['term'])
                        jinhaChatId.append(db['chat_id'])
            elif db['campName'] == campName[1]:
                if 'selectedDate' in db:
                    for date in db['selectedDate']:
                        daejeoDate.append(date['startDate'])
                        daejeoTerm.append(date['term'])
                        daejeoChatId.append(db['chat_id'])
            elif db['campName'] == campName[2]:
                if 'selectedDate' in db:
                    for date in db['selectedDate']:
                        samrakDate.append(date['startDate'])
                        samrakTerm.append(date['term'])
                        samrakChatId.append(db['chat_id'])

        print('jinhaDate: ', jinhaDate)
        print('jinhaTerm: ', jinhaTerm)
        print('jinhaChatId: ', jinhaChatId)
        print('daejeoDate: ', daejeoDate)
        print('daejeoTerm: ', daejeoTerm)
        print('daejeoChatId: ', daejeoChatId)
        print('samrakDate: ', samrakDate)
        print('samrakTerm: ', samrakTerm)
        print('samrakChatId: ', samrakChatId)


# 사용자 컴퓨터 OS 확인 후 설정값 반환
systemOS = platform.system()
pathChromedriver = ''

if systemOS == "Darwin":
    pathChromedriver = '/Users/WMHY/Downloads/chromedriver'
elif systemOS == "Windows":
    pathChromedriver = ''
elif systemOS == "Linux":
    pathChromedriver = '/home/ubuntu/chromedriver'

webdriver_options = webdriver.ChromeOptions()
# webdriver_options .add_argument('headless')

driver = webdriver.Chrome(pathChromedriver, options=webdriver_options)

# # 오늘 날짜 확인
today = datetime.date.today()
print(today)

# # 진하캠핑장 검색
jinha.connectWebsite(driver)
index = 0
jinhaThisMonth = 0
jinhaModDate = []
for date in jinhaDate:
    startDateYear = date[0:2]
    startDateMonth = date[2:4]
    startDateDay = date[4:]
    jinhaModDate.append('20'+startDateYear+'-'+startDateMonth+'-'+startDateDay)

# term = jinhaTerm[index]
# chatId = jinhaChatId[index]
# index = index + 1
# if int(startDateMonth) == today.month:
#     print('ok')
# else:
#     print('no')
# # 검색할 캠핑장 선택
# selectedCampsite = []
# sendMessageCount = 0

# while sendMessageCount == 0:
#     sleepRandomTime = random.randrange(20, 40)

#     # if '대저캠핑장' in selectedCampsite:
#     #     daejeo.thisAndNextMonthSearch(driver)

#     # if '삼락캠핑장' in selectedCampsite:
#     #     samrak.thisAndNextMonthSearch(driver)

#     if '진하캠핑장' in selectedCampsite:
#         jinha.connectWebsite(driver)
#         jinha.thisMonthSearch(driver)

#     searchCount += 1
#     print('Searching : ' + str(searchCount) + '번째')

#     # 랜덤으로 대기 후 실행
#     time.sleep(sleepRandomTime)
