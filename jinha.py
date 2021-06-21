from bs4 import BeautifulSoup
import time
from telegramCustomFunc import telegramSendMessage


def connectWebsite(driver, date):
    url = 'https://xn--om2bi2o9qdy7a48exzk3vf68fzzd.kr/reserve/month?day=' + date + '&cate_no=a'
    driver.get(url)
    time.sleep(0.5)
    html = driver.page_source


def thisMonthSearch(driver, campName, chatId, selectDate, term):
    dataValList = ['a', 'b', 'c', 'd', 'e', 'f']
    for area in dataValList:
        xpath = "//button[@data-val='" + area + "']"
        driver.find_element_by_xpath(xpath).click()
        time.sleep(0.1)
        html = driver.page_source
        global jinhaSoup
        jinhaSoup = BeautifulSoup(html, 'html.parser')
        siteFind = jinhaSoup.select('a.num')
        activeSiteCount = 0
        for active in siteFind:
            if selectDate in active['data-val']:
                if '예약가능' in active.select_one('img')['alt']:
                    activeSiteCount += 1
        if activeSiteCount > 0:
            telegramSendMessage(str(chatId), campName,
                                selectDate, area.upper())
