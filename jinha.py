from bs4 import BeautifulSoup
import time
from telegramCustomFunc import telegramSendMessage
import datetime
from dateutil.relativedelta import relativedelta
import asyncio
from selenium.webdriver.common.by import By
import logging
import sys


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
    logging.info(f"Jinha: Accessing URL: {url}")
    try:
        driver.get(url)
        time.sleep(0.5)
        html = driver.page_source
        jinhaSoup = BeautifulSoup(html, 'html.parser')
        page_title_element = jinhaSoup.select_one('title')
        expected_title = "울주해양레포츠센터"
        if not page_title_element or expected_title not in page_title_element.string:
             logging.warning(f"Jinha: Page title mismatch for {calDate}. Expected '{expected_title}' in title, but got: '{page_title_element.string if page_title_element else 'Not Found'}'")
             return []

        siteFind = jinhaSoup.select('a.num')
        logging.info(f"Jinha: Initial reservation cells found on page for {calDate}: {len(siteFind) if siteFind else 0}")
        
        if siteFind:
            for area in dataValList:
                xpath = "//button[@data-val='" + area + "']"
                logging.info(f"Jinha: Attempting to click area button: {area}")
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)
                    html = driver.page_source
                    jinhaSoup = BeautifulSoup(html, 'html.parser')
                    siteFind_area = jinhaSoup.select('a.num')
                    logging.info(f"Jinha: Found {len(siteFind_area)} cells after clicking area {area}")
                    for active in siteFind_area:
                        img_tag = active.select_one('img')
                        alt_text = img_tag.get('alt', '') if img_tag else ''
                        date_val = active.get('data-val')
                        site_text = active.text.strip()
                        
                        logging.debug(f"Jinha: Cell found - Date: {date_val}, Site: {site_text}, Alt: {alt_text}")

                        if img_tag and '예약가능' in alt_text:
                            if date_val and site_text and '-' in date_val and len(date_val.split('-')) == 3: 
                                date_key = date_val.replace('-','')[2:]
                                if date_key in dbDateList:
                                    logging.info(f"Jinha: Found AVAILABLE site - Date: {date_val}, SiteNum: {site_text}, DateKey: {date_key}")
                                    avalList.append({'date': date_val, 'siteNum': site_text})
                                else:
                                    logging.debug(f"Jinha: Available site {date_val} date key {date_key} not in user's requested dbDateList: {dbDateList}")
                            else:
                                 logging.warning(f"Jinha: Skipping available cell due to unexpected data format - Date: {date_val}, Site: {site_text}")
                                 
                except Exception as e:
                    logging.error(f"Jinha: Error processing area {area} for date {calDate}: {e}", exc_info=True) 
        else:
            logging.info(f"Jinha: No 'a.num' elements (reservation cells) found initially for {calDate}")

    except Exception as e:
        logging.error(f"Jinha: General error in siteSearch for date {calDate}: {e}", exc_info=True)
    
    logging.info(f"Jinha: siteSearch for {calDate} finished. Found available/relevant sites: {len(avalList)}")
    logging.debug(f"Jinha: siteSearch returning avalList: {avalList}")
    return avalList

async def siteMatching(avalMonth, searchDateRealList, dbList):
    logging.info(f"Jinha: Starting siteMatching. Found sites: {len(avalMonth)}, User requests: {len(dbList)}, Target dates: {searchDateRealList}")
    for avalDay in avalMonth:
        try:
            logging.debug(f"Jinha: Processing available day: {avalDay}")
            if 'siteNum' not in avalDay or not avalDay['siteNum']:
                logging.warning(f"Jinha: Skipping avalDay due to missing or empty 'siteNum': {avalDay}")
                continue
                
            if len(avalDay['siteNum']) < 2:
                logging.warning(f"Jinha: Skipping avalDay due to unexpected 'siteNum' format (too short): {avalDay}")
                continue
            siteNumSelect = avalDay['siteNum'][0]

            if 'date' not in avalDay:
                 logging.warning(f"Jinha: Skipping avalDay due to missing 'date': {avalDay}")
                 continue
                 
            avalDate = avalDay['date']
            if avalDate not in searchDateRealList:
                logging.debug(f"Jinha: Skipping available date {avalDate} as it's not in user's target dates {searchDateRealList}")
                continue

            avalDateKey = avalDate.replace('-', '')[2:] 
            logging.debug(f"Jinha: Prepared avalDateKey: {avalDateKey}")

            for dbListElement in dbList:
                logging.debug(f"Jinha: Comparing with user request: {dbListElement}")
                if 'date' not in dbListElement or 'onlyAsite' not in dbListElement or 'id' not in dbListElement:
                    logging.warning(f"Jinha: Skipping dbListElement due to missing keys: {dbListElement}")
                    continue

                chatId = dbListElement['id']
                userDates = dbListElement['date']
                onlyAsiteFlags = dbListElement['onlyAsite']

                for index, requestedDateKey in enumerate(userDates):
                    logging.debug(f"Jinha: Checking against requestedDateKey: {requestedDateKey} at index {index}")
                    if avalDateKey == requestedDateKey:
                        logging.info(f"Jinha: Date match found! Available: {avalDateKey}, Requested: {requestedDateKey}")
                        if index >= len(onlyAsiteFlags):
                            logging.warning(f"Jinha: Index {index} out of bounds for onlyAsiteFlags (len {len(onlyAsiteFlags)}) for user {chatId}. Assuming 'n'.")
                            wantsOnlyASite = 'n'
                        else:
                            wantsOnlyASite = onlyAsiteFlags[index]
                        
                        logging.info(f"Jinha: Matching Details - WantsOnlyA: {wantsOnlyASite}, FoundSiteType: {siteNumSelect}")
                        
                        shouldSend = False
                        if wantsOnlyASite == 'y':
                            if siteNumSelect == 'A':
                                logging.info("Jinha: Condition met (Wants only A, Found A)")
                                shouldSend = True
                            else:
                                logging.info("Jinha: Condition NOT met (Wants only A, Found {siteNumSelect})")
                        else:
                            logging.info("Jinha: Condition met (Wants any site)")
                            shouldSend = True
                            
                        if shouldSend:
                            logging.info(f"Jinha: Preparing to send Telegram message to {chatId} for site {avalDay['siteNum']} on {avalDate}")
                            try:
                                await telegramSendMessage(chatId, '울주해양레포츠센터', avalDate, avalDay['siteNum'])
                                logging.info(f"Jinha: Telegram message apparently sent successfully to {chatId}.")
                            except Exception as telegram_e:
                                logging.error(f"Jinha: Error calling telegramSendMessage for {chatId}: {telegram_e}", exc_info=True)
                                
        except IndexError as e:
             logging.error(f"Jinha: IndexError in siteMatching for day {avalDay}. Is 'siteNum' ({avalDay.get('siteNum')}) populated correctly? Error: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Jinha: General Error in siteMatching processing {avalDay}: {e}", exc_info=True)

    logging.info(f"Jinha: Finished siteMatching.")

async def mainSearch(driver, searchDateRealList, dbList):
    avalThisMonth = []
    avalNextMonth = []
    dbDateList = []
    try:
        dbDateList = filterDbDate(dbList)
        logging.info(f"Jinha: Extracted unique DB date keys for siteSearch: {dbDateList}")
    except Exception as e:
        logging.error(f"Jinha: Error in filterDbDate: {e}", exc_info=True)
        return

    try:
        logging.info("Jinha: Searching current month")
        avalThisMonth = siteSearch(today, driver, dbDateList)
        logging.info("Jinha: Searching next month")
        avalNextMonth = siteSearch(nextMonth, driver, dbDateList)

        allAvalSites = avalThisMonth + avalNextMonth
        logging.info(f"Jinha: Total available sites found across months: {len(allAvalSites)}")

        await siteMatching(allAvalSites, searchDateRealList, dbList)
        
    except Exception as e:
        logging.error(f"Jinha: Error in mainSearch execution: {e}", exc_info=True)

