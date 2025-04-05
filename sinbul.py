from bs4 import BeautifulSoup
from selenium import webdriver
import time
from telegramCustomFunc import telegramSendMessage
from selenium.common.exceptions import WebDriverException, NoSuchElementException, NoAlertPresentException
from selenium.webdriver.common.alert import Alert
import asyncio
from selenium.webdriver.common.by import By
import logging # Add logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def connectWebsite(driver):
    url = 'https://camping.ulju.ulsan.kr/Pmreservation.do'
    try:
        driver.get(url)
        time.sleep(1.2) # Increase sleep slightly
    except Exception as e:
        logging.error(f"Sinbul: Error connecting to website: {e}")
        raise # Re-raise exception

async def siteSearch(driver, chatId, date, numDate, today):
    # Make this function async
    errorCheck = 0
    site_found = False # Flag to track if any site was found and message sent

    try:
        # --- Navigate to the correct month and day --- 
        current_month_xpath = "//*[@id='calendar']/div[1]/div[1]" # Adjust XPath if needed
        # Get the displayed month text (assuming format like 'YYYY년 MM월')
        displayed_month_text = driver.find_element(By.XPATH, current_month_xpath).text
        displayed_month = int(displayed_month_text.split(' ')[1].replace('월', ''))

        # Click next month if necessary
        if displayed_month != numDate:
             # Make sure this logic correctly handles year changes if applicable
            next_month_button_xpath = "//*[@id='calendar']/div[1]/div[2]" # Adjust XPath if needed
            driver.find_element(By.XPATH, next_month_button_xpath).click()
            time.sleep(0.5)

        # Click on the target date
        date_element_xpath = f"//td[@data-date='{date}']"
        driver.find_element(By.XPATH, date_element_xpath).click()
        time.sleep(1) # Wait for potential loading/scripts

    except NoSuchElementException:
        logging.warning(f"Sinbul: Date element {date} not found or not clickable.")
        return False # Date not available or navigation failed
    except Exception as e:
        logging.error(f"Sinbul: Error navigating calendar to date {date}: {e}")
        return False

    # --- Handle potential alert --- 
    try:
        # Check for alert and accept if present
        alert = Alert(driver)
        alert_text = alert.text # Optional: log alert text
        logging.info(f"Sinbul: Accepting alert: {alert_text}")
        alert.accept()
        # If alert was present, it often means no sites available, maybe return early?
        # logging.info(f"Sinbul: Alert indicates no sites for {date}")
        # return False # Decide if accepting alert means failure
        errorCheck = 0 # Alert was handled
    except NoAlertPresentException:
        errorCheck = 1 # No alert means we proceed to check sites
    except Exception as e:
        logging.error(f"Sinbul: Error handling alert for date {date}: {e}")
        return False # Uncertain state, treat as failure

    time.sleep(1)

    # --- Check available sites if no blocking alert appeared --- 
    if errorCheck == 1:
        try:
            # Check if the area selection / site table is present
            try:
                 # Use a more reliable element to check if site info is loaded
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='divAjaxTable']//label"))
                )
            except TimeoutException:
                logging.info(f"Sinbul: Site information table did not load for date {date}")
                return False # Table didn't load, assume no sites

            # Iterate through site type tabs (e.g., 작천정, 등억, 달빛)
            for i in range(1, 4): # Assuming 3 tabs
                activeSiteInfo = []
                activeRealSite = []
                try:
                    xpath_tab = f"//*[@id='divAjaxTable']/input[{i}]" # Find tab input
                    # Instead of clicking the input directly, click its associated label if possible
                    # This often works better. Adjust selector as needed.
                    label_xpath = f"//label[@for='{driver.find_element(By.XPATH, xpath_tab).get_attribute('id')}']"
                    driver.find_element(By.XPATH, label_xpath).click()
                    time.sleep(1.5) # Allow time for table content to update

                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    active_table = soup.find("table", {"id": "tableSite"})

                    if not active_table:
                        logging.warning(f"Sinbul: Site table not found for tab {i} on date {date}")
                        continue # Try next tab

                    activeA = active_table.find_all("tr")

                    for row in activeA:
                        site_details = [td.get_text().strip() for td in row.find_all("td", {"class": "lt_text"})] 
                        if site_details: # Ensure it's not an empty list (e.g., header row)
                            # Check based on expected structure. Adjust indices if needed.
                            if len(site_details) >= 2 and '-' in site_details[0] and '예약가능' in site_details[-1]: # Basic check for site name format and availability
                                if '하우스' not in site_details[1]:
                                     activeRealSite.append(site_details)
                    
                    if activeRealSite:
                        logging.info(f"Sinbul: Found {len(activeRealSite)} available sites in tab {i} for {date}")
                        for siteDetail in activeRealSite:
                             # Construct name carefully, ensure indices are valid
                             try:
                                campName = f'신불산({siteDetail[0]}) {siteDetail[1]}'
                                logging.info(f"Sinbul: Sending message for {campName} on {date} to {chatId}")
                                # Use await instead of asyncio.run
                                await telegramSendMessage(str(chatId), campName, date, 'none', 'none')
                                site_found = True # Mark that a message was sent
                             except IndexError:
                                 logging.error(f"Sinbul: IndexError constructing campName for siteDetail: {siteDetail}")
                             except Exception as e:
                                 logging.error(f"Sinbul: Error sending Telegram message: {e}")
                                 
                except NoSuchElementException:
                     logging.warning(f"Sinbul: Tab input/label {i} not found for date {date}.")
                     continue # Try next tab
                except Exception as e:
                    logging.error(f"Sinbul: Error processing tab {i} for date {date}: {e}")
                    continue # Try next tab even if one fails

        except Exception as e:
            logging.error(f"Sinbul: Error checking site availability details for date {date}: {e}")
            return False

    return site_found # Return True if a message was sent, False otherwise
