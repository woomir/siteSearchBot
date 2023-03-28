import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from boto3.dynamodb.conditions import Key, Attr
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
import asyncio


try:
    roofCheck = 0
    # 사용자 컴퓨터 OS 확인 후 설정값 반환
    systemOS = platform.system()
    pathChromedriver = ''

    if systemOS == "Darwin":
        # pathChromedriver = '/Users/WMHY/Downloads/chromedriver'
        pathChromedriver = '/Users/home/coding/chromedriver' 
        # 맥북에서 테스트 할 때 사용
    elif systemOS == "Windows":
        pathChromedriver = ''
    elif systemOS == "Linux":
        pathChromedriver = '/home/ubuntu/chromedriver'

    webdriver_options = webdriver.ChromeOptions()
    webdriver_options .add_argument('--headless')
    webdriver_options.add_argument('lang=ko_KR')
    webdriver_options.add_argument('window-size=1920x1080')
    webdriver_options.add_argument('disable-gpu')
    webdriver_options.add_argument('--incognito')
    webdriver_options.add_argument('--no-sandbox')
    webdriver_options.add_argument('--disable-setuid-sandbox')
    webdriver_options.add_argument('--disable-dev-shm-usage')



    webdriver_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

    driver = webdriver.Chrome(pathChromedriver, options=webdriver_options)

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

    def listSearch(db):
        group = []
        for a in db:
            dateT = []
            if a.get('selectedDate'):
                for i in range(0,len(a['selectedDate'])):
                    dateT.append(a['selectedDate'][i]['startDate'])
                group.append({'id':a['chat_id'],'date':dateT})
        return sorted(group, key = lambda item: item['id'])

    def changeDateType(date):
        startDateYear = date[0:2]
        startDateMonth = date[2:4]
        startDateDay = date[4:]
        modDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
        dateType = datetime.date(
        int('20'+startDateYear), int(startDateMonth), int(startDateDay))
        return {'modDate': modDate, 'dateType':dateType, 'startDateYear': startDateYear, 'startDateMonth': startDateMonth, 'startDateDay': startDateDay}


    while roofCheck < 1:
        # 오늘 날짜 확인
        today = datetime.date.today()
        startTime = time.time()

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

        jinhaList = []
        hwarangList = []
        samrakList = []
        sinbulList = []

        session = boto3.session.Session(profile_name='siteSearch')

        dynamodb = session.resource('dynamodb')  # bucket 목록
        table = dynamodb.Table('siteSearchBot_campInfo')

        
        if __name__ == '__main__':
            jinhaDb = sorted(dbScan('울주해양레포츠센터'), key=lambda item:item['chat_id'])
            hwarangDb = sorted(dbScan('화랑마을(육부촌)'), key=lambda item:item['chat_id'])
            samrakDb = sorted(dbScan('삼락캠핑장'), key=lambda item:item['chat_id'])
            sinbulDb = sorted(dbScan('신불산(작천정, 등억, 달빛)'), key=lambda item:item['chat_id'])

            jinhaDate = dateExtract(jinhaDb)
            hwarangDate = dateExtract(hwarangDb)
            samrakDate = dateExtract(samrakDb)
            sinbulDate = dateExtract(sinbulDb)

            jinhaList = listSearch(jinhaDb)
            hwarangList = listSearch(hwarangDb)
            samrakList = listSearch(samrakDb)
            sinbulList = listSearch(sinbulDb)

        # 진하캠핑장 검색
        jinhaSearchDateRealList = []
        for date in jinhaDate:
            # 검색할 날짜를 list로 변환
            searchDate = changeDateType(date)
            if (today <= searchDate['dateType']):
                jinhaSearchDateRealList.append(searchDate['modDate'])
        jinha.mainSearch(driver, jinhaSearchDateRealList, jinhaList)

        # 삼락캠핑장 검색
        index = 0
        for date in samrakDate:
            searchDate = changeDateType(date)
            oneMonthAfterDate = today + datetime.timedelta(days=30)
            if (today <= searchDate['dateType'] and oneMonthAfterDate >= searchDate['dateType']):
                # term = samrakTerm[index]
                term = 1
                chatId = samrakChatId[index]
                samrak.connectWebsite(driver, searchDate['modDate'], term)
                samrak.siteSearch(
                    driver, campName[1], chatId, searchDate['modDate'], term)
            index += 1

        # 화랑마을(육부촌) 검색
        index = 0
        for date in hwarangDate:
            searchDate = changeDateType(date)
            if (today <= searchDate['dateType']):
                # term = hwarangTerm[index]
                term = 1
                chatId = hwarangChatId[index]
                hwarang.connectWebsite(
                    driver, searchDate['startDateYear'], searchDate['startDateMonth'], searchDate['startDateDay'])
                hwarang.siteSearch(
                    driver, campName[2], chatId, searchDate['modDate'], term)
            index += 1

        # 신불산 검색
        for index in range(len(sinbulList)):
            dateList = sinbulList[index]['date']
            for date in dateList:
                mainID = sinbulList[index]['id']
                searchDate = changeDateType(date)
                if (today <= searchDate['dateType']):
                    sinbul.connectWebsite(driver)
                    sinbul.siteSearch(driver, mainID, searchDate['modDate'])

        # endTime = time.time()
        # measureTime = endTime - startTime

        # 시간 측정
        # print("시간")
        # print(measureTime)

except Exception as e:
    asyncio.run(teleFunc.telegramSimpleMessage('1003456250', '정지'))
    print(datetime.datetime.now(),"===================================")
    print(e)