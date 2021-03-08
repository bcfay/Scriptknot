from threading import Timer

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Watchdog(Exception):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self

chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

FILE_PATH_FOLDER = '~/Documents/ScrapeKnot Files'

df = pd.read_csv("DomesticWeddingPlannerEmailListCities.csv")

#watchdog = Watchdog(10)


# cleaned_column = [0] * (100-last_city_index)
#
# for i in range(last_city_index+1, 99):
#     cleaned_column[i-last_city_index] = saved_column[i]
# print(cleaned_column)


main_driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
page_driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
main_driver.fullscreen_window()
page_driver.fullscreen_window()


for index, row in df.iterrows():

    city_name = row[0]
    city_name = city_name.replace(' ', '-')
    state_name = row[1]

    entry_email = "needs to be found"

    City_Entries = []

    fb_rejections = 0
    fb_limit = 5
    for page_number in range(1, 100):
        if fb_rejections > fb_limit:
            continue
        if page_number == 1:
            search_query = 'https://www.theknot.com/marketplace/wedding-planners-' + (city_name.lower()) + '-' + (
                state_name.lower())
        else:
            search_query = 'https://www.theknot.com/marketplace/wedding-planners-' + (city_name.lower()) + '-' + (
                    state_name.lower() + '?page=' + str(page_number))


        main_driver.get(search_query)



        time.sleep(1)
        main_driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        try:
            cardList = main_driver.find_elements_by_class_name("click-container--48a45")
        except NoSuchElementException:
            print("empty page")
            continue

        card_view = main_driver.current_window_handle
        window_counter = 0

        if len(cardList) == 0:
            fb_rejections = fb_limit + 1;


        for each_page in cardList:
            if fb_rejections > fb_limit:
                continue
            #watchdog.reset()
            try:
                #main_driver.switch_to.window(card_view)
                try:
                    page_driver.get(each_page.get_attribute('href'))
                    #time.sleep(.5)
                except WebDriverException:
                    print("card click error")
                    continue


                knot_page = page_driver.current_url
                # # Getting job info

                entry_city = city_name
                entry_state = state_name
                try:
                    entry_company = page_driver.find_element_by_css_selector('.vendor-name--4ff81.h1--bf424').text
                except NoSuchElementException:
                    entry_company = 'NA...somehow?'
                try:
                    entry_phone = page_driver.find_element_by_css_selector('.phone-number.body1--fd844').text
                except NoSuchElementException:
                    entry_phone = 'NA'
                try:
                    name = page_driver.find_element_by_css_selector('.name--5d0dd.body1--fd844').text
                    parsed_names = name.split(' ')
                except NoSuchElementException:
                    name = 'NA NA'
                    parsed_names = name.split(' ')

                entry_first_name = parsed_names[0]
                entry_last_name = parsed_names[-1]

                #watchdog.reset()
                try:
                    entry_fb_link = page_driver.find_element_by_xpath("//a[@title='facebook']").get_attribute('href')
                    fb_rejections = 0
                    #watchdog.stop()



                except (NoSuchElementException, Watchdog):
                    fb_rejections = fb_rejections + 1
                    print("No fb rejection criteria met. " + str(fb_rejections) + ' consecutive rejections. ')
                    #driver.close()
                    continue
                #watchdog.stop()
                try:
                    entry_website = page_driver.find_element_by_xpath("//a[@title='website']").get_attribute('href')

                    entry_email = "needs to be found"
                    # driver.find_element_by_xpath("//a[@title='website']").click()
                    # time.sleep(.5)
                    # web_page = driver.window_handles[2]
                    # driver.switch_to.window(web_page)
                    #
                    # entry_email = "init"
                    # try:
                    #     entry_email = driver.find_element_by_partial_link_text('mailto').get_attribute('href')
                    # except NoSuchElementException:
                    #     entry_email = 'Not_Automatically_Found'
                    #
                    # driver.close()
                    # driver.switch_to.window(home_page)

                except NoSuchElementException:
                    entry_website = 'NA'

                # Saving job info
                entry = [entry_email, entry_company, entry_city, entry_state, entry_fb_link, entry_phone,
                         entry_first_name, entry_last_name, entry_website, knot_page]
                # # Saving into job_details
                # page = [each_job.click()]
                print(entry)
                City_Entries.append(entry)
                #driver.close()



            except Watchdog:
                print("Watchdog Expired")
        if len(City_Entries) > 0:
            dataEntries = pd.DataFrame(City_Entries)
            dataEntries.columns = ['Email Address', 'Company', 'City', 'State', 'FB Page', 'Phone ', 'First Name',
                               'Last Name', 'Website', 'Knot Page']
            dataEntries.to_csv('knotPages' + '_' + city_name + '_' + state_name + '.csv', index=False)
        #driver.quit()

    df = df.iloc[1:]
    gfg_csv_data = df.to_csv('DomesticWeddingPlannerEmailListCities.csv', index=False)
