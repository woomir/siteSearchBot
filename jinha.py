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

def filterDbDate (aadbList):
    dateList = []
    for bb in aadbList:
        for aa in bb['date']:
            if aa not in dateList:
                dateList.append(aa)
    return dateList

def siteSearch(calDate, driver, dbDateList):
    avalList = []
    dataValList = ['a', 'b', 'c', 'd', 'e', 'f']
    url = 'https://xn--om2bi2o9qdy7a48exzk3vf68fzzd.kr/reserve/month?day=' + str(calDate) + '&cate_no=a'
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
                    if active['data-val'].replace('-','')[2:] in dbDateList:
                        avalList.append({'date': active['data-val'], 'siteNum': active.text})
    return avalList

def siteMatching(avalMonth, searchDateRealList, dbList):
    for avalDay in avalMonth:
        if avalDay['date'] in searchDateRealList:
            for dbListElement in dbList:
                for c in dbListElement['date']:
                    if avalDay['date'][2:].replace('-','') == c:
                        telegramSendMessage(dbListElement['id'],'울주해양레포츠센터',avalDay['date'], avalDay['siteNum'])

def mainSearch(driver, searchDateRealList, dbList):
    avalThisMonth = []
    avalNextMonth = []
    dbDateList = filterDbDate(dbList)
    
    # 이번달 찾기
    avalThisMonth = siteSearch(today, driver, dbDateList)
    # 다음달 찾기
    avalNextMonth = siteSearch(nextMonth, driver, dbDateList)

    # 자리 있는 날짜와 검색 날짜 매칭
    siteMatching(avalThisMonth, searchDateRealList, dbList)
    siteMatching(avalNextMonth, searchDateRealList, dbList)

