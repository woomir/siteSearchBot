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


def connectWebsite(driver, date, term):
    url = 'https://www.nakdongcamping.com/reservation/real_time?user_id=&site_id=&site_type=&dis_rate=0&user_dis_rate=&resdate=' + \
        date + '&schGugun=' + term + '&price=0&bagprice=2000&allprice=0'
    try:
        driver.get(url)
        time.sleep(0.7)
    except Exception as e:
        logging.error(f"Samrak: Error connecting to website for date {date}: {e}")
        raise


async def siteSearch(driver, campName, chatId, date, term):
    count = 0
    try:
        html = driver.page_source
        samrakSoup = BeautifulSoup(html, 'html.parser')

        page_title_element = samrakSoup.select_one('title')
        if not page_title_element or "실시간예약" not in page_title_element.string:
            logging.warning(f"Samrak: Page title not as expected for date {date}. Title: {page_title_element.string if page_title_element else 'Not Found'}")
            return

        activeSite = samrakSoup.find_all('a', class_='cbtn_on')
        for title in activeSite:
            if title.has_attr('class') and "area_c" not in title['class']:
                count += 1

        if count > 0:
            logging.info(f"Samrak: Found {count} available sites for {date}. Sending message to {chatId}")
            await telegramSendMessage(chatId, campName, date, 'none', term)

    except Exception as e:
        logging.error(f"Samrak: Error in siteSearch for date {date}, chatId {chatId}: {e}")
