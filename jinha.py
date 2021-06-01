import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform

searchCount = 0
sendMessageCount = 0


def connectWebsite(driver):
    url = 'https://xn--om2bi2o9qdy7a48exzk3vf68fzzd.kr/'
    driver.get(url)
    time.sleep(0.5)
    html = driver.page_source
    if '/login?backURL=%2F' in html:
        # 로그인 화면으로 이동
        xpath = "//a[@href='/login?backURL=%2F']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(0.1)
        # 아이디 입력
        xpath = "//input[@id='m_id']"
        driver.find_element_by_xpath(xpath).send_keys('woomir@gmail.com')
        time.sleep(0.1)
        # 비번 입력
        xpath = "//input[@id='password']"
        driver.find_element_by_xpath(xpath).send_keys('$52Telecast')
        time.sleep(0.1)
        # 로그인 버튼 클릭
        xpath = "//button[@id='login_submit']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(0.1)

    # 예약사이트 접속
    xpath = "//a[@href='/room/camping.php']"
    driver.find_element_by_xpath(xpath).click()
    time.sleep(0.2)
    xpath = "//*[@id='wrap']/div[3]/div/ul/li[4]/a"
    driver.find_element_by_xpath(xpath).click()
    time.sleep(0.1)


def weekendSearch(driver, todayDay):
    # 토요일 날짜 추출
    html = driver.page_source
    global jinhaSoup
    jinhaSoup = BeautifulSoup(html, 'html.parser')
    satDay = jinhaSoup.find_all('span', {'class': 'sat'})
    global jinhaSatDayNumber
    jinhaSatDayNumber = []
    for text in satDay:
        if text.get_text() != '' and int(text.get_text()) > todayDay:
            jinhaSatDayNumber.append(text.get_text())

    # 몇월인지 확인
    global jinhaMonth
    jinhaMonth = jinhaSoup.find('div', {'class': 'month'})
    global jinhaMonthNumber
    jinhaMonthNumber = jinhaMonth.find('em').get_text()
    global jinhaThisMonth
    jinhaThisMonth = jinhaMonthNumber[5:7]


def repeatDayQuestion():
    # 반복 검색할 날짜 선택
    global jinhaSelectDay
    jinhaSelectDay = []
    print('검색할 날짜를 선택하세요.(y로 대답하세요)')
    for i in jinhaSatDayNumber:
        answer = input(jinhaThisMonth+'월 ' + i + '일을 검색할까요?')
        if 'y' in answer:
            jinhaSelectDay.append(i)
        elif 'n' in answer:
            print('ok')
        else:
            print('잘못 입력했어요.')


def thisMonthSearch(driver):
    # 선택한 날짜에서 예약 가능한 A구역 Site 개수 파악
    dataValList = ['a', 'b', 'c', 'd', 'e', 'f']
    for area in dataValList:
        xpath = "//button[@data-val='" + area + "']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(0.1)
        html = driver.page_source
        global jinhaSoup
        jinhaSoup = BeautifulSoup(html, 'html.parser')
        areaName = jinhaSoup.select_one("button.btn_active").get_text()
        siteFind = jinhaSoup.select('a.num')
        activeSiteCount = 0
        for selectSatDay in jinhaSelectDay:
            if len(selectSatDay) < 2:
                selectSatDay = '0'+selectSatDay
            searchDay = '2021-'+jinhaThisMonth+'-'+selectSatDay
            for active in siteFind:
                if searchDay in active['data-val']:
                    if '예약가능' in active.select_one('img')['alt']:
                        activeSiteCount += 1
            if activeSiteCount > 0:
                telegramSendMessage('이번달', selectSatDay,
                                    activeSiteCount, '진하캠핑장', areaName)
                print('진하캠핑장: ' + jinhaThisMonth + '월 ' + selectSatDay +
                      '일 ' + areaName + '에 ' + str(activeSiteCount) + '개 예약 가능')
                global sendMessageCount
                sendMessageCount += 1
            else:
                print('진하캠핑장: ' + jinhaThisMonth + '월 ' +
                      selectSatDay + '일 ' + areaName + '자리 없음.')

    return sendMessageCount


# 사용자 컴퓨터 OS 확인 후 설정값 반환
if __name__ == "__main__":
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

    driver = webdriver.Chrome(
        pathChromedriver, options=webdriver_options)

    # 오늘 날짜 확인
    todayDay = datetime.datetime.now().day

    connectWebsite(driver)
    weekendSearch(driver)
    repeatDayQuestion()

    while sendMessageCount == 0:
        sleepRandomTime = random.randrange(20, 40)

        thisMonthSearch(driver)

        # 찾은 횟수 카운트
        searchCount += 1
        print('Searching : ' + str(searchCount) + '번째')

        # 30~60초 랜덤 실행
        time.sleep(sleepRandomTime)
