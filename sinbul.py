from bs4 import BeautifulSoup
from selenium import webdriver
import time
from telegramCustomFunc import telegramSendMessage
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.alert import Alert
import asyncio
from selenium.webdriver.common.by import By

def connectWebsite(driver):

    url = 'https://camping.ulju.ulsan.kr/Pmreservation.do'

    driver.get(url)
    time.sleep(1)


def siteSearch(driver, chatId, date, numDate, today):
    errorCheck = 0

    try:
        if today.month != numDate:
            xpath = "//*[@id='calendar']/div[1]/div[2]"
            driver.find_element(By.XPATH, xpath).click()
        xpath = "//td[@data-date='" + date + "']"
        driver.find_element(By.XPATH, xpath).click()
        time.sleep(1)
    except Exception as e:
        print(e)
        return False
    try:
        Alert(driver).accept()
    except:
        errorCheck = 1

    time.sleep(1)

    if errorCheck == 1:
        try:
            xpath = "//*[@id='divAjaxTable']/div/label"
            driver.find_element(By.XPATH, xpath).click()

            time.sleep(2)

            for i in range(1, 4):
                activeSiteInfo = []
                activeSiteDetail = []
                activeRealSite = []
                xpath = "//*[@id='divAjaxTable']/input[" + str(i) + "]"
                driver.find_element(By.XPATH, xpath).click()

                time.sleep(2)
                # print("input click")

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
                        campName = '신불산(' + \
                            siteDetail[0] + ') ' + siteDetail[1]
                        asyncio.run(telegramSendMessage(
                            str(chatId), campName, date, 'none', 'none'))
        except:
            # print("input click failure")
            return False
