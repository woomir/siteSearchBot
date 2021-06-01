import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform
import daejeo
import samrak
import jinha


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
webdriver_options .add_argument('headless')

driver = webdriver.Chrome(pathChromedriver, options=webdriver_options)

# 오늘 날짜 확인
todayDay = datetime.datetime.now().day

# 검색할 캠핑장 선택
campsite = ['대저캠핑장',
            '삼락캠핑장', '진하캠핑장']
selectedCampsite = []
print('검색할 캠핑장을 선택하세요.(y나 n으로 대답하세요)')
for i in campsite:
    answerOk = False
    while answerOk == False:
        answer = input(i + '을 검색할까요? ')
        if 'y' in answer:
            selectedCampsite.append(i)
            answerOk = True
        elif 'n' in answer:
            print('ok')
            answerOk = True
        else:
            print('잘못 입력했어요. 다시 입력하세요')


for i in selectedCampsite:
    print(i + '\n=================================================')
    if i == '대저캠핑장':
        daejeo.connectWebsite(driver)
        daejeo.weekendSearch(driver)
        daejeo.thisMonth(todayDay)
        daejeo.nextMonth(driver)
        daejeo.repeatDayQuestion()
    elif i == '삼락캠핑장':
        samrak.connectWebsite(driver)
        samrak.weekendSearch(driver)
        samrak.thisMonth(todayDay)
        samrak.nextMonth(driver)
        samrak.repeatDayQuestion()
    elif i == '진하캠핑장':
        jinha.connectWebsite(driver)
        jinha.weekendSearch(driver, todayDay)
        jinha.repeatDayQuestion()

searchCount = 0
sendMessageCount = 0

while sendMessageCount == 0:
    sleepRandomTime = random.randrange(20, 40)

    if '대저캠핑장' in selectedCampsite:
        daejeo.thisAndNextMonthSearch(driver)

    if '삼락캠핑장' in selectedCampsite:
        samrak.thisAndNextMonthSearch(driver)

    if '진하캠핑장' in selectedCampsite:
        jinha.connectWebsite(driver)
        jinha.thisMonthSearch(driver)

    searchCount += 1
    print('Searching : ' + str(searchCount) + '번째')

    # 랜덤으로 대기 후 실행
    time.sleep(sleepRandomTime)
