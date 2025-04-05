import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform
import asyncio
import logging


def connectWebsite(driver, year, month, day):
    url = 'https://www.gyeongju.go.kr/hwarang/page.do?step=list&mnu_uid=1996&tabNum=1&csi_uid=12&initYear=20' + \
        year + '&initMonth=' + month + '&initDay=' + day + '&daynum=' + day
    try:
        driver.get(url)
        time.sleep(0.7)
    except Exception as e:
        logging.error(f"Hwarang: Error connecting to website for {year}-{month}-{day}: {e}")
        raise


async def siteSearch(driver, campName, chatId, date, term):
    count = 0
    try:
        html = driver.page_source
        hwarangSoup = BeautifulSoup(html, 'html.parser')

        page_title_element = hwarangSoup.select_one('title')
        if not page_title_element or "시설예약" not in page_title_element.string:
            logging.warning(f"Hwarang: Page title not as expected for {date}. Title: {page_title_element.string if page_title_element else 'Not Found'}")
            return

        activeSite = hwarangSoup.find_all('a', 'wp50')
        if activeSite:
            count = len(activeSite)

        if count > 0:
            logging.info(f"Hwarang: Found {count} available sites for {date}. Sending message to {chatId}")
            await telegramSendMessage(str(chatId), campName, date, 'none', term)

    except Exception as e:
        logging.error(f"Hwarang: Error in siteSearch for date {date}, chatId {chatId}: {e}")
