import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform


def connectWebsite(driver):
    # url = 'https://camping.ulju.ulsan.kr/Pmreservation.do'
    url = 'https://camping.ulju.ulsan.kr'

    driver.get(url)
    time.sleep(1)


def siteSearch(driver, chatId, date):

    try:
        # xpath = "//*[@id='calendar']"
        # driver.find_element_by_xpath(xpath).click()
        # time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print('soup: ', soup)
        xpath = "//td[@data-date='" + date + "']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(2)
        # driver.find_element_by_xpath(
        # "//*[@id='divAjaxTable']/div/label").click()
        xpath = "//*[@id='divAjaxTable']/div/label"
        element = driver.find_element_by_xpath(xpath)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
        for i in range(1, 4):
            activeSiteInfo = []
            activeSiteDetail = []
            activeRealSite = []
            xpath = "//*[@id='divAjaxTable']/input[" + str(i) + "]"
            driver.find_element_by_xpath(xpath).click()
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            active = soup.find("table", {"id": "tableSite"})
            activeA = active.find_all("tr")

            for text in activeA:
                aa = text.find_all("td", {"class": "lt_text"})
                if aa != []:
                    for bb in aa:
                        cc = bb.get_text().strip()
                        activeSiteDetail.append(cc)
                    activeSiteInfo.append(activeSiteDetail)
                    activeSiteDetail = []

            for site in activeSiteInfo:
                if '하우스' not in site[1]:
                    activeRealSite.append(site)

            if len(activeRealSite) > 0:
                for siteDetail in activeRealSite:
                    campName = '신불산(' + siteDetail[0] + ') ' + siteDetail[1]
                    telegramSendMessage(
                        str(chatId), campName, date, 'none', 'none')
    except Exception as e:
        print("예약 불가")
        # logger.error('Failed: ' + str(e))
