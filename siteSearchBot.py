import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from boto3.dynamodb.conditions import Key
import jinha
import samrak
import hwarang
import sinbul
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
import telegramCustomFunc as teleFunc
import platform


try:
    roofCheck = 0

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
    webdriver_options .add_argument('--headless')
    webdriver_options.add_argument('lang=ko_KR')
    webdriver_options.add_argument('window-size=1920x1080')
    webdriver_options.add_argument('disable-gpu')

    webdriver_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

    driver = webdriver.Chrome(pathChromedriver, options=webdriver_options)

    while roofCheck < 1:
        # 오늘 날짜 확인
        today = datetime.date.today()
        sleepRandomTime = random.randrange(1, 3)

        campName = ['울주해양레포츠센터', '삼락캠핑장', '화랑마을(육부촌)', '신불산(작천정, 등억, 달빛)']
        jinhaDate = []
        jinhaTerm = []
        jinhaChatId = []

        hwarangDate = []
        hwarangTerm = []
        hwarangChatId = []

        samrakDate = []
        samrakTerm = []
        samrakChatId = []

        sinbulDate = []
        sinbulTerm = []
        sinbulChatId = []

        session = boto3.session.Session(profile_name='siteSearch')
        dynamodb = session.resource('dynamodb')  # bucket 목록
        table = dynamodb.Table('siteSearchBot_campInfo')

        def dbScan(campName, dynamodb=None):
            try:
                response = table.scan(
                    FilterExpression = Attr('campName').eq(campName)
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
            else:
                return response['Items']

        def dateExtract(data):
            date = []
            for i in range(0, len(data)):
                element = data[i]
                if element.get('selectedDate') != None:
                    for j in range(0,len(element['selectedDate'])):
                        b = element['selectedDate'][j]['startDate']
                        if b not in date:
                            date.append(b)
            return date

        if __name__ == '__main__':
            jinhaDb = dbScan('울주해양레포츠센터')
            hwarangDb = dbScan('화랑마을(육부촌)')
            samrakDb = dbScan('삼락캠핑장')
            sinbulDb = dbScan('신불산(작천정, 등억, 달빛)')

            jinhaDate = dateExtract(jinhaDb)
            hwarangDate = dateExtract(hwarangDb)
            samrakDate = dateExtract(samrakDb)
            sinbulDate = dateExtract(sinbulDb)

        # 진하캠핑장 검색
        index = 0
        for date in jinhaDate:
            startDateYear = date[0:2]
            startDateMonth = date[2:4]
            startDateDay = date[4:]
            jinhaModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
            jinhaDateType = datetime.date(
                int('20'+startDateYear), int(startDateMonth), int(startDateDay))
            if (today <= jinhaDateType):
                chatId = jinhaChatId[index]
                jinha.connectWebsite(driver, jinhaModDate)
                jinha.thisMonthSearch(
                    driver, campName[0], chatId, jinhaModDate, 1)
            index += 1

        # 삼락캠핑장 검색
        index = 0
        for date in samrakDate:
            startDateYear = date[0:2]
            startDateMonth = date[2:4]
            startDateDay = date[4:]
            samrakModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
            samrakDateType = datetime.date(
                int('20'+startDateYear), int(startDateMonth), int(startDateDay))
            oneMonthAfterDate = today + datetime.timedelta(days=30)
            if (today <= samrakDateType and oneMonthAfterDate >= samrakDateType):
                term = samrakTerm[index]
                chatId = samrakChatId[index]
                samrak.connectWebsite(driver, samrakModDate, term)
                samrak.siteSearch(
                    driver, campName[1], chatId, samrakModDate, term)
            index += 1

        # 화랑마을(육부촌) 검색
        index = 0
        for date in hwarangDate:
            startDateYear = date[0:2]
            startDateMonth = date[2:4]
            startDateDay = date[4:]
            hwarangModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
            hwarangDateType = datetime.date(
                int('20'+startDateYear), int(startDateMonth), int(startDateDay))
            if (today <= hwarangDateType):
                term = hwarangTerm[index]
                chatId = hwarangChatId[index]
                hwarang.connectWebsite(
                    driver, startDateYear, startDateMonth, startDateDay)
                hwarang.siteSearch(
                    driver, campName[2], chatId, hwarangModDate, term)
            index += 1

        # 신불산 검색
        index = 0
        for date in sinbulDate:
            startDateYear = date[0:2]
            startDateMonth = date[2:4]
            startDateDay = date[4:]
            sinbulModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
            sinbulDateType = datetime.date(
                int('20'+startDateYear), int(startDateMonth), int(startDateDay))
            if (today <= sinbulDateType):
                term = sinbulTerm[index]
                chatId = sinbulChatId[index]
                sinbul.connectWebsite(driver)
                sinbul.siteSearch(
                    driver, chatId, sinbulModDate)
            index += 1

        # 랜덤으로 대기 후 실행
        time.sleep(sleepRandomTime)

except Exception as e:
    teleFunc.telegramSimpleMessage('1003456250', '프로그램 정지')
    # logger.error('Failed: ' + str(e))