import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform


def connectWebsite(driver, year, month, day):
    url = 'https://www.gyeongju.go.kr/hwarang/page.do?step=list&mnu_uid=1996&tabNum=1&csi_uid=12&initYear=' + \
        year + '&initMonth=' + month + '&initDay=' + day + '&daynum=' + day
    driver.get(url)
    time.sleep(0.5)


def siteSearch(driver, campName, chatId, date, term):
    count = 0
    html = driver.page_source
    hwarangSoup = BeautifulSoup(html, 'html.parser')
    activeSite = hwarangSoup.find_all('a', 'wp50')
    if len(activeSite) > 0:
        count += 1
    if count > 0:
        telegramSendMessage(str(chatId), campName, date, 'none', term)
