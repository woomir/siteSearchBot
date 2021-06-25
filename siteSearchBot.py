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
    # webdriver_options .add_argument('--headless')
    webdriver_options.add_argument('lang=ko_KR')
    webdriver_options.add_argument('headless')
    webdriver_options.add_argument('window-size=1920x1080')
    webdriver_options.add_argument('disable-gpu')

    # webdriver_options.add_argument('start-maximized')
    webdriver_options.add_argument('disable-infobars')
    webdriver_options.add_argument('--disable-extensions')
    webdriver_options.add_argument('--ignore-certificate-errors')
    webdriver_options.add_argument('--ignore-certificate-errors-spki-list')
    webdriver_options.add_argument('--ignore-ssl-errors')
    webdriver_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    webdriver_options.add_experimental_option('useAutomationExtension', False)
    webdriver_options.add_arguments("--disable-dev-shm-usage")
    # webdriver_options.add_argument('--start-maximized')

    webdriver_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

    driver = webdriver.Chrome(pathChromedriver, options=webdriver_options)
    # driver.maximize_window()
    # driver.set_window_size(1920, 1080)

    # TEST_URL = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'
    driver.get('about:blank')
    driver.execute_script(
        "Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script(
        "Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    # driver.get(TEST_URL)
    # user_agent = driver.find_element_by_css_selector('#user-agent').text
    # plugins_length = driver.find_element_by_css_selector(
    #     '#plugins-length').text
    # languages = driver.find_element_by_css_selector('#languages').text
    # print('User-Agent: ', user_agent)
    # print('Plugin length: ', plugins_length)
    # print('languages: ', languages)

    while roofCheck < 1:
        # 오늘 날짜 확인
        today = datetime.date.today()
        sleepRandomTime = random.randrange(10, 20)

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
                # print("Get campDb succeeded:")
                # print(campDb)
                # 진하캠핑장 구독 데이터 추출
                for db in campDb:
                    if db['campName'] == campName[0]:
                        if 'selectedDate' in db:
                            for date in db['selectedDate']:
                                jinhaDate.append(date['startDate'])
                                jinhaTerm.append(date['term'])
                                jinhaChatId.append(db['chat_id'])
                    elif db['campName'] == campName[2]:
                        if 'selectedDate' in db:
                            for date in db['selectedDate']:
                                hwarangDate.append(date['startDate'])
                                hwarangTerm.append(date['term'])
                                hwarangChatId.append(db['chat_id'])
                    elif db['campName'] == campName[1]:
                        if 'selectedDate' in db:
                            for date in db['selectedDate']:
                                samrakDate.append(date['startDate'])
                                samrakTerm.append(date['term'])
                                samrakChatId.append(db['chat_id'])

                    elif db['campName'] == campName[3]:
                        if 'selectedDate' in db:
                            for date in db['selectedDate']:
                                sinbulDate.append(date['startDate'])
                                sinbulTerm.append(date['term'])
                                sinbulChatId.append(db['chat_id'])

        # # 진하캠핑장 검색
        # index = 0
        # for date in jinhaDate:
        #     startDateYear = date[0:2]
        #     startDateMonth = date[2:4]
        #     startDateDay = date[4:]
        #     jinhaModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
        #     jinhaDateType = datetime.date(
        #         int('20'+startDateYear), int(startDateMonth), int(startDateDay))
        #     if (today <= jinhaDateType):
        #         term = jinhaTerm[index]
        #         chatId = jinhaChatId[index]
        #         jinha.connectWebsite(driver, jinhaModDate)
        #         jinha.thisMonthSearch(
        #             driver, campName[0], chatId, jinhaModDate, term)
        #     index += 1

        # # 삼락캠핑장 검색
        # index = 0
        # for date in samrakDate:
        #     startDateYear = date[0:2]
        #     startDateMonth = date[2:4]
        #     startDateDay = date[4:]
        #     samrakModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
        #     samrakDateType = datetime.date(
        #         int('20'+startDateYear), int(startDateMonth), int(startDateDay))
        #     oneMonthAfterDate = today + datetime.timedelta(days=30)
        #     if (today <= samrakDateType and oneMonthAfterDate >= samrakDateType):
        #         term = samrakTerm[index]
        #         chatId = samrakChatId[index]
        #         samrak.connectWebsite(driver, samrakModDate, term)
        #         samrak.siteSearch(
        #             driver, campName[1], chatId, samrakModDate, term)
        #     index += 1

        # # 화랑마을(육부촌) 검색
        # index = 0
        # for date in hwarangDate:
        #     startDateYear = date[0:2]
        #     startDateMonth = date[2:4]
        #     startDateDay = date[4:]
        #     hwarangModDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
        #     hwarangDateType = datetime.date(
        #         int('20'+startDateYear), int(startDateMonth), int(startDateDay))
        #     if (today <= hwarangDateType):
        #         term = hwarangTerm[index]
        #         chatId = hwarangChatId[index]
        #         hwarang.connectWebsite(
        #             driver, startDateYear, startDateMonth, startDateDay)
        #         hwarang.siteSearch(
        #             driver, campName[2], chatId, hwarangModDate, term)
        #     index += 1

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
                # print("신불 접속")
                sinbul.siteSearch(
                    driver, chatId, sinbulModDate)
            index += 1

        # 랜덤으로 대기 후 실행
        time.sleep(sleepRandomTime)

except Exception as e:
    teleFunc.telegramSimpleMessage('1003456250', '프로그램 정지')
    logger.error('Failed: ' + str(e))
