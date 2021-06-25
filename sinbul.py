import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telegram
import random
import datetime
from telegramCustomFunc import telegramSendMessage
import platform
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.alert import Alert


def connectWebsite(driver):

    url = 'https://camping.ulju.ulsan.kr/Pmreservation.do'

    # driver.get(url)
    time.sleep(1)
    response = requests.get(url)

    print(response.status_code)
    # print(response.text)
    # driver.save_screenshot("main.png")

    # xpath = "//*[@id='header']/div[1]/div/ul/li[1]/a"

    # xpath = "//*[@id='main_menu']/li[1]/a"
    # xpath = "//a[@id='login_ulsan']"
    # driver.find_element_by_xpath(xpath).click()
    # driver.find_element_by_xpath("//input[@name='userid']").send_keys("woomir")
    # driver.find_element_by_xpath(
    #     "//input[@name='password']").send_keys("$52Telecast")
    # xpath = "//*[@id='loginfrm']/div/input"
    # driver.find_element_by_xpath(xpath).click()

    # url = 'https://camping.ulju.ulsan.kr/Pmreservation.do'
    # driver.get(url)

    # test = driver.find_element_by_css_selector('li.depth1.menu04')
    # driver.find_element_by_css_selector('li.depth1.menu04').click()

    # driver.execute_script("arguments[0].click();", test)
    # time.sleep(1)
    # driver.save_screenshot("menu.png")


def siteSearch(driver, chatId, date):
    errorCheck = 0

    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        active = soup.find("table", {"id": "tableSite"})
        # print(soup)
        xpath = "//td[@data-date='" + date + "']"
        # xpath = "//td[@data-date='2021-06-24']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(1)
        print("date click")
    except:
        driver.save_screenshot("test.png")
        print("date click failure")
        return False
    try:
        Alert(driver).accept()
        print("Alert click")
    except:
        print("Alert click failure")
        errorCheck = 1

    time.sleep(1)

    if errorCheck == 1:
        try:
            xpath = "//*[@id='divAjaxTable']/div/label"
            driver.find_element_by_xpath(xpath).click()
            time.sleep(1)
            print("label click")

            for i in range(1, 4):
                activeSiteInfo = []
                activeSiteDetail = []
                activeRealSite = []
                xpath = "//*[@id='divAjaxTable']/input[" + str(i) + "]"
                driver.find_element_by_xpath(xpath).click()
                time.sleep(1)
                print("input click")

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
                        telegramSendMessage(
                            str(chatId), campName, date, 'none', 'none')
        except:
            print("input click failure")
