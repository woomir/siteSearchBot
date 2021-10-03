from bs4 import BeautifulSoup
import time
from telegramCustomFunc import telegramSendMessage
import datetime
from dateutil.relativedelta import relativedelta


today = datetime.date.today()
nextMonth = today + relativedelta(months=1)

def changeDateType(date):
    startDateYear = date[0:2]
    startDateMonth = date[2:4]
    startDateDay = date[4:]
    modDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
    dateType = datetime.date(
    int('20'+startDateYear), int(startDateMonth), int(startDateDay))
    return {'modDate': modDate, 'dateType':dateType, 'startDateYear': startDateYear, 'startDateMonth': startDateMonth, 'startDateDay': startDateDay}

def thisMonthSearch(driver, searchDateRealList, dbList):
    avalThisMonth = []
    avalNextMonth = []
    dataValList = ['a', 'b', 'c', 'd', 'e', 'f']
    
    # 이번달 찾기
    url = 'https://xn--om2bi2o9qdy7a48exzk3vf68fzzd.kr/reserve/month?day=' + str(today) + '&cate_no=a'
    driver.get(url)
    time.sleep(0.1)
    for area in dataValList:
        xpath = "//button[@data-val='" + area + "']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(0.1)
        html = driver.page_source
        jinhaSoup = BeautifulSoup(html, 'html.parser')
        siteFind = jinhaSoup.select('a.num')
        for active in siteFind:
            if '예약가능' in active.select_one('img')['alt']:
                avalThisMonth.append({'date': active['data-val'], 'siteNum': active.text})
    
    # 다음달 찾기
    url = 'https://xn--om2bi2o9qdy7a48exzk3vf68fzzd.kr/reserve/month?day=' + str(nextMonth) + '&cate_no=a'
    driver.get(url)
    time.sleep(0.1)
    html = driver.page_source
    jinhaSoup = BeautifulSoup(html, 'html.parser')
    siteFind = jinhaSoup.select('a.num')
    if siteFind:
        for area in dataValList:
            xpath = "//button[@data-val='" + area + "']"
            driver.find_element_by_xpath(xpath).click()
            time.sleep(0.1)
            html = driver.page_source
            jinhaSoup = BeautifulSoup(html, 'html.parser')
            siteFind = jinhaSoup.select('a.num')
            for active in siteFind:
                if '예약가능' in active.select_one('img')['alt']:
                    avalNextMonth.append({'date': active['data-val'], 'siteNum': active.text})
    
    # 자리 있는 날짜와 검색 날짜 매칭
    for avalThisDay in avalThisMonth:
        if avalThisDay['date'] in searchDateRealList:
            for dbListElement in dbList:
                    for c in dbListElement['date']:
                        if avalThisDay['date'][2:].replace('-','') == c:
                            telegramSendMessage(dbListElement['id'],'울주해양레포츠센터',avalThisDay['date'], avalThisDay['siteNum'])
                        
    for avalNextDay in avalNextMonth:
        if avalNextDay['date'] in searchDateRealList:
            for dbListElement in dbList:
                    for c in dbListElement['date']:
                        if avalNextDay['date'][2:].replace('-','') == c:
                            telegramSendMessage(dbListElement['id'],'울주해양레포츠센터',avalNextDay['date'], avalNextDay['siteNum'])
