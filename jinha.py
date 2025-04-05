from bs4 import BeautifulSoup
import time
from telegramCustomFunc import telegramSendMessage
import datetime
from dateutil.relativedelta import relativedelta
import asyncio
from selenium.webdriver.common.by import By
import logging


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
    try:
        driver.get(url)
        time.sleep(0.2)
        html = driver.page_source
        jinhaSoup = BeautifulSoup(html, 'html.parser')
        page_title_element = jinhaSoup.select_one('title')
        if not page_title_element or "달력" not in page_title_element.string:
             logging.warning(f"Jinha: Page title not as expected for {calDate}. Title: {page_title_element.string if page_title_element else 'Not Found'}")
             return []

        siteFind = jinhaSoup.select('a.num')
        if siteFind:
            for area in dataValList:
                xpath = "//button[@data-val='" + area + "']"
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.2)
                    html = driver.page_source
                    jinhaSoup = BeautifulSoup(html, 'html.parser')
                    siteFind_area = jinhaSoup.select('a.num')
                    for active in siteFind_area:
                        img_tag = active.select_one('img')
                        if img_tag and '예약가능' in img_tag.get('alt', ''):
                            date_val = active.get('data-val')
                            site_text = active.text
                            if date_val and site_text and date_val.replace('-','')[2:] in dbDateList:
                                avalList.append({'date': date_val, 'siteNum': site_text})
                except Exception as e:
                    logging.error(f"Jinha: Error clicking area {area} or processing results: {e}")
        else:
            logging.info(f"Jinha: No 'a.num' elements found initially for {calDate}")

    except Exception as e:
        logging.error(f"Jinha: Error in siteSearch for date {calDate}: {e}")
    return avalList

async def siteMatching(avalMonth, searchDateRealList, dbList):
    for avalDay in avalMonth:
        try:
            if 'siteNum' not in avalDay or not avalDay['siteNum']:
                logging.warning(f"Jinha: Skipping avalDay due to missing 'siteNum': {avalDay}")
                continue
            siteNumSelect = avalDay['siteNum'][1]

            if 'date' not in avalDay or avalDay['date'] not in searchDateRealList:
                continue

            for dbListElement in dbList:
                if 'date' not in dbListElement or 'onlyAsite' not in dbListElement or 'id' not in dbListElement:
                    logging.warning(f"Jinha: Skipping dbListElement due to missing keys: {dbListElement}")
                    continue

                count = 0
                for c in dbListElement['date']:
                    if count >= len(dbListElement['onlyAsite']):
                        logging.warning(f"Jinha: Index 'count' out of bounds for 'onlyAsite' in dbListElement: {dbListElement}")
                        break

                    if avalDay['date'][2:].replace('-','') == c:
                        if dbListElement['onlyAsite'][count] == 'y':
                            if siteNumSelect == 'A':
                                logging.info(f"Jinha: Sending Telegram msg (A site): {dbListElement['id']}, {avalDay['date']}, {avalDay['siteNum']}")
                                await telegramSendMessage(dbListElement['id'],'울주해양레포츠센터',avalDay['date'], avalDay['siteNum'])
                        else:
                            logging.info(f"Jinha: Sending Telegram msg (any site): {dbListElement['id']}, {avalDay['date']}, {avalDay['siteNum']}")
                            await telegramSendMessage(dbListElement['id'],'울주해양레포츠센터',avalDay['date'], avalDay['siteNum'])
                    count += 1
        except IndexError as e:
             logging.error(f"Jinha: IndexError in siteMatching for day {avalDay}. Is 'siteNum' populated correctly? Error: {e}")
        except Exception as e:
            logging.error(f"Jinha: General Error in siteMatching for day {avalDay}: {e}")

async def mainSearch(driver, searchDateRealList, dbList):
    avalThisMonth = []
    avalNextMonth = []
    dbDateList = []
    try:
        dbDateList = filterDbDate(dbList)
    except Exception as e:
        logging.error(f"Jinha: Error in filterDbDate: {e}")
        return

    try:
        logging.info("Jinha: Searching current month")
        avalThisMonth = siteSearch(today, driver, dbDateList)
        logging.info("Jinha: Searching next month")
        avalNextMonth = siteSearch(nextMonth, driver, dbDateList)

        logging.info(f"Jinha: Matching sites for current month ({len(avalThisMonth)} found)")
        await siteMatching(avalThisMonth, searchDateRealList, dbList)
        logging.info(f"Jinha: Matching sites for next month ({len(avalNextMonth)} found)")
        await siteMatching(avalNextMonth, searchDateRealList, dbList)
    except Exception as e:
        logging.error(f"Jinha: Error in mainSearch execution: {e}")

