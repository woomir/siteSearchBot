import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from boto3.dynamodb.conditions import Key, Attr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import jinha
import samrak
import hwarang
import sinbul
import time
import datetime
import telegramCustomFunc as teleFunc
import platform
import asyncio
import logging
import sys
from typing import Optional

# 로깅 설정 (기존 basicConfig 제거)
logger = logging.getLogger() # 루트 로거 가져오기
logger.setLevel(logging.INFO) # 로거의 기본 레벨은 INFO로 설정 (콘솔 출력을 위해)

# 포매터 설정
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 콘솔 핸들러 설정 (WARNING 레벨 이상으로 변경)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.WARNING) # INFO -> WARNING 변경
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 파일 핸들러 설정 (ERROR 레벨 이상 - 유지)
file_handler = logging.FileHandler('siteSearchBot.log')
file_handler.setLevel(logging.ERROR) # 파일에는 ERROR 레벨 이상만 기록
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def setup_webdriver() -> Optional[webdriver.Chrome]:
    try:
        options = Options()
        options.add_argument('--headless') # 주석 제거하여 헤드리스 모드 활성화
        options.add_argument('lang=ko_KR')
        options.add_argument('window-size=1920x1080')
        options.add_argument('disable-gpu')
        options.add_argument('--incognito')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-save-password-bubble')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-web-security')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        )

        # Using webdriver-manager is preferred if installed
        try:
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            logger.info("WebDriver initialized using webdriver-manager.")
        except (ImportError, Exception) as e_wdm:
            logger.warning(f"webdriver-manager failed ({e_wdm}), falling back to default path...")
            # Fallback if webdriver-manager is not installed or fails
            driver = webdriver.Chrome(options=options) 
            logger.info("WebDriver initialized using default method.")
            
        driver.set_page_load_timeout(45) # Increase timeout slightly
        driver.set_script_timeout(45) # Increase timeout slightly
        return driver
    except WebDriverException as e:
         # More specific exception handling
        logger.error(f"WebDriverException during setup: {str(e)}")
        if "net::ERR_CONNECTION_REFUSED" in str(e):
            logger.error("Connection refused - is ChromeDriver running or accessible?")
        elif "session not created" in str(e):
            logger.error("Session not created - ChromeDriver/Chrome version mismatch or other setup issue?")
        return None
    except Exception as e:
        logger.error(f"Generic exception during webdriver setup: {str(e)}", exc_info=True)
        return None

def initialize_aws_session():
    try:
        session = boto3.session.Session(profile_name='siteSearch')
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('siteSearchBot_campInfo')
        return table
    except Exception as e:
        logger.error(f"Failed to initialize AWS session: {str(e)}")
        return None

def dbScan(table, campName):
    try:
        response = table.scan(
            FilterExpression=Attr('campName').eq(campName)
        )
        return response['Items']
    except ClientError as e:
        logger.error(f"Database scan error for {campName}: {str(e)}")
        return []

def dateExtract(data):
    try:
        date = []
        for element in data:
            if element.get('selectedDate'):
                for date_info in element['selectedDate']:
                    b = date_info['startDate']
                    if b not in date:
                        date.append(b)
        return date
    except Exception as e:
        logger.error(f"Error extracting dates: {str(e)}")
        return []

def listSearch(db):
    try:
        group = []
        for a in db:
            dateT = []
            onlyAsite = a.get('onlyAsite', '')
            onlyAsiteOne = []
            if a.get('selectedDate'):
                for i in range(len(a['selectedDate'])):
                    dateT.append(a['selectedDate'][i]['startDate'])
                    onlyAsiteOne.append(onlyAsite[i])
                group.append({'id': a['chat_id'], 'date': dateT, 'onlyAsite': onlyAsite})
        return sorted(group, key=lambda item: item['id'])
    except Exception as e:
        logger.error(f"Error in listSearch: {str(e)}")
        return []

def sinbullistSearch(db):
    try:
        group = []
        for a in db:
            dateT = []
            if a.get('selectedDate'):
                for i in range(len(a['selectedDate'])):
                    dateT.append(a['selectedDate'][i]['startDate'])
                group.append({'id': a['chat_id'], 'date': dateT})
        return sorted(group, key=lambda item: item['id'])
    except Exception as e:
        logger.error(f"Error in sinbullistSearch: {str(e)}")
        return []

def changeDateType(date):
    try:
        startDateYear = date[0:2]
        startDateMonth = date[2:4]
        startDateDay = date[4:]
        modDate = '20'+startDateYear+'-'+startDateMonth+'-'+startDateDay
        dateType = datetime.date(
            int('20'+startDateYear), int(startDateMonth), int(startDateDay))
        return {
            'modDate': modDate,
            'dateType': dateType,
            'startDateYear': startDateYear,
            'startDateMonth': startDateMonth,
            'startDateDay': startDateDay
        }
    except Exception as e:
        logger.error(f"Error in changeDateType: {str(e)}")
        return None

async def run_search_cycle(driver: webdriver.Chrome, table):
    """Fetches data and runs the search for all campsites for one cycle."""
    try:
        today = datetime.date.today()
        campName = ['울주해양레포츠센터', '삼락캠핑장', '화랑마을(육부촌)', '신불산(작천정, 등억, 달빛)']
        logger.info(f"--- Starting search cycle for {today} ---")

        # Get data from DynamoDB
        logger.info("Fetching data from DynamoDB...")
        # Add try-except around DB operations as they can fail
        try:
            jinhaDb = sorted(dbScan(table, '울주해양레포츠센터'), key=lambda item: item.get('chat_id', ''))
            hwarangDb = sorted(dbScan(table, '화랑마을(육부촌)'), key=lambda item: item.get('chat_id', ''))
            samrakDb = sorted(dbScan(table, '삼락캠핑장'), key=lambda item: item.get('chat_id', ''))
            sinbulDb = sorted(dbScan(table, '신불산(작천정, 등억, 달빛)'), key=lambda item: item.get('chat_id', ''))
            logger.info(f"DynamoDB data fetched: Jinha({len(jinhaDb)}), Hwarang({len(hwarangDb)}), Samrak({len(samrakDb)}), Sinbul({len(sinbulDb)})")
        except Exception as db_e:
            logger.error(f"Error fetching data from DynamoDB: {db_e}")
            return # Cannot proceed without data

        # Extract dates and create lists
        # Add try-except around list processing
        try:
            jinhaDate = dateExtract(jinhaDb)
            hwarangDate = dateExtract(hwarangDb)
            samrakDate = dateExtract(samrakDb)
            sinbulDate = dateExtract(sinbulDb)

            jinhaList = listSearch(jinhaDb)
            hwarangList = listSearch(hwarangDb)
            samrakList = listSearch(samrakDb)
            sinbulList = sinbullistSearch(sinbulDb)
        except Exception as list_e:
            logger.error(f"Error processing lists from DB data: {list_e}")
            return # Cannot proceed
            
        # --- Process Jinha --- 
        logger.info("Processing Jinha...")
        jinhaSearchDateRealList = []
        for date in jinhaDate:
            searchDate = changeDateType(date)
            if searchDate and today <= searchDate['dateType']:
                jinhaSearchDateRealList.append(searchDate['modDate'])
        
        if jinhaSearchDateRealList:
            logger.info(f"Jinha dates to search: {jinhaSearchDateRealList}")
            # Add try-except around individual site searches
            try:
                await jinha.mainSearch(driver, jinhaSearchDateRealList, jinhaList)
            except Exception as site_e:
                logger.error(f"Error during Jinha processing: {site_e}", exc_info=True)
                # Decide if driver needs refresh/restart after error
                # driver.refresh() # Example
        else:
            logger.info("No valid future dates found for Jinha.")

        # --- Process Samrak --- 
        logger.info("Processing Samrak...")
        oneMonthAfterDate = today + datetime.timedelta(days=30)
        for user_info in samrakList:
            chatId = user_info.get('id')
            dateList = user_info.get('date', [])
            if not chatId:
                 logger.warning("Samrak: Skipping user_info due to missing 'id'.")
                 continue
            
            for date in dateList:
                searchDate = changeDateType(date)
                if searchDate and today <= searchDate['dateType'] and oneMonthAfterDate >= searchDate['dateType']:
                    term = '1' 
                    try:
                        logger.info(f"Samrak: Connecting & Searching for {chatId} - {searchDate['modDate']}")
                        samrak.connectWebsite(driver, searchDate['modDate'], term)
                        await samrak.siteSearch(driver, campName[1], chatId, searchDate['modDate'], term) 
                    except Exception as e:
                        logger.error(f"Samrak: Error during processing for {chatId} - {searchDate['modDate']}: {e}", exc_info=True)
                        # driver.refresh()

        # --- Process Hwarang --- 
        logger.info("Processing Hwarang...")
        for user_info in hwarangList:
            chatId = user_info.get('id')
            dateList = user_info.get('date', [])
            if not chatId:
                 logger.warning("Hwarang: Skipping user_info due to missing 'id'.")
                 continue

            for date in dateList:
                searchDate = changeDateType(date)
                if searchDate and today <= searchDate['dateType']:
                    term = 1 
                    try:
                        logger.info(f"Hwarang: Connecting & Searching for {chatId} - {searchDate['modDate']}")
                        hwarang.connectWebsite(
                            driver, searchDate['startDateYear'], searchDate['startDateMonth'], searchDate['startDateDay'])
                        await hwarang.siteSearch(driver, campName[2], chatId, searchDate['modDate'], term) 
                    except Exception as e:
                        logger.error(f"Hwarang: Error during processing for {chatId} - {searchDate['modDate']}: {e}", exc_info=True)
                        # driver.refresh()

        # --- Process Sinbul --- 
        logger.info("Processing Sinbul...")
        for user_info in sinbulList:
            mainID = user_info.get('id')
            dateList = user_info.get('date', [])
            if not mainID:
                 logger.warning("Sinbul: Skipping user_info due to missing 'id'.")
                 continue
                 
            for date in dateList:
                searchDate = changeDateType(date)
                if searchDate and today <= searchDate['dateType']:
                    try:
                        logger.info(f"Sinbul: Connecting & Searching for {mainID} - {searchDate['modDate']}")
                        sinbul.connectWebsite(driver) 
                        await sinbul.siteSearch(driver, mainID, searchDate['modDate'], searchDate['dateType'].month, today) 
                    except Exception as e:
                         logger.error(f"Sinbul: Error during processing for {mainID} - {searchDate['modDate']}: {e}", exc_info=True)
                         # driver.refresh()

        logger.info(f"--- Finished search cycle --- ")

    except WebDriverException as driver_e:
        logger.error(f"WebDriverException during search cycle: {driver_e}", exc_info=True)
        # Re-raise the exception so the main loop can handle driver restart
        raise
    except Exception as e:
        # Catch any other unexpected errors within the cycle
        logger.error(f"Unexpected error during search cycle: {e}", exc_info=True)
        # Optionally send a Telegram message here as well
        # await teleFunc.telegramSimpleMessage('1003456250', f'[ERROR] Unexpected cycle error: {str(e)}')

# --- Main Execution Block --- 
if __name__ == '__main__':
    logger.info("Script starting...")
    driver = None
    table = None
    retries = 3 # Number of retries for initial setup

    # --- Initial Setup --- 
    for i in range(retries):
        logger.info(f"Attempting initial setup ({i+1}/{retries})...")
        driver = setup_webdriver()
        if driver:
            logger.info("WebDriver setup successful.")
            table = initialize_aws_session()
            if table:
                logger.info("AWS session initialized successfully.")
                break # Exit loop if both succeed
            else:
                logger.error("Failed to initialize AWS session. Quitting driver.")
                try:
                    driver.quit()
                except Exception: pass
                driver = None # Reset driver
        else:
            logger.error("Failed to setup WebDriver.")
        
        if i < retries - 1:
            logger.info("Retrying setup in 30 seconds...")
            time.sleep(30)
    
    if not driver or not table:
        logger.critical("Initial setup failed after multiple retries. Exiting script.")
        # Optionally send a critical failure message via Telegram if possible (sync)
        # Note: Cannot use await here
        sys.exit(1) # Exit if setup fails completely

    # --- Main Loop --- 
    try:
        while True:
            try:
                logger.info("Starting new search cycle execution...")
                # Check if driver is still usable before running cycle
                try:
                    # Simple check: get current URL. If this fails, driver is likely dead.
                    driver.current_url 
                except WebDriverException as wd_check_e:
                    logger.error(f"WebDriver seems unresponsive before cycle: {wd_check_e}. Attempting restart...")
                    try: driver.quit() 
                    except Exception: pass
                    driver = setup_webdriver()
                    if not driver:
                        logger.error("Failed to restart WebDriver. Waiting before next attempt...")
                        time.sleep(120) # Wait longer if restart fails
                        continue # Skip this cycle
                    logger.info("WebDriver restarted successfully.")
                
                # Run the actual search cycle
                asyncio.run(run_search_cycle(driver, table))
                
                logger.info(f"Search cycle finished. Sleeping for 3 seconds...")
                time.sleep(3)
                
            except WebDriverException as loop_wd_e:
                logger.error(f"WebDriverException caught in main loop: {loop_wd_e}. Attempting to restart WebDriver...")
                try: driver.quit() 
                except Exception: pass
                driver = None # Ensure old driver is cleared
                # Try to restart the driver immediately
                driver = setup_webdriver()
                if not driver:
                    logger.error("Failed to restart WebDriver after error. Waiting 120s...")
                    time.sleep(120) # Wait longer if restart fails within loop
                else:
                    logger.info("WebDriver restarted successfully after error. Continuing loop.")
                    time.sleep(5) # Short pause after successful restart
                    
            except Exception as loop_e:
                # Handle other unexpected errors in the loop
                logger.error(f"Unexpected error in main loop: {loop_e}", exc_info=True)
                logger.info("Sleeping for 60 seconds before continuing...")
                time.sleep(60)
                # Consider if driver needs restart here too depending on the error

    except KeyboardInterrupt:
        logger.info("Script interrupted by user. Cleaning up...")
    finally:
        # --- Cleanup --- 
        if driver:
            try:
                logger.info("Closing final WebDriver instance...")
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing final WebDriver: {str(e)}")
        logger.info("Script finished.")