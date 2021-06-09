import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform


def connectWebsite(driver, date, term):
    url = 'https://www.nakdongcamping.com/reservation/real_time?user_id=&site_id=&site_type=&dis_rate=0&user_dis_rate=&resdate=' + \
        date + '&schGugun=' + term + '&price=0&bagprice=2000&allprice=0'
    driver.get(url)
    time.sleep(0.5)


def siteSearch(driver, campName, chatId, date, term):
    count = 0
    html = driver.page_source
    samrakSoup = BeautifulSoup(html, 'html.parser')
    activeSite = samrakSoup.find_all('a', 'cbtn_on')
    for title in activeSite:
        if "area_c" not in title["class"]:
            count += 1
    if count > 0:
        telegramSendMessage(chatId, campName, date, 'none', term)
