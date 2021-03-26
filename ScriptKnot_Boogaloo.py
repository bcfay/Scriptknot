import glob
import os
import time
from threading import Timer

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.firefox import GeckoDriverManager

watchdog_timer = 12
LOGIN_URL = 'https://www.facebook.com/login.php'


class FacebookLogin():
    def __init__(self, email, password, browser='Chrome'):
        # Store credentials for login
        self.email = email
        self.password = password
        if browser == 'Chrome':
            # Use chrome
            chrome_options = Options()
            chrome_options.add_argument("--disable-notifications")
            self.driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
            self.driver.fullscreen_window()

        elif browser == 'Firefox':
            # Set it to Firefox
            self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get(LOGIN_URL)
        time.sleep(1) # Wait for some time to load

    def login(self):
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email)  # Give keyboard input

        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password)  # Give password as input too

        login_button = self.driver.find_element_by_id('loginbutton')
        login_button.click()  # Send mouse click

        time.sleep(2)  # Wait for 2 seconds for the page to show up

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
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

FILE_PATH_FOLDER = '~/Documents/ScrapeKnot Files'

mycsvdir = '/home/bcfay/Documents/PycharmProjects/ScrapeKnot/venv'

# get all the csv files in that directory (assuming they have the extension .csv)
csvfiles = glob.glob(os.path.join(mycsvdir, '*.csv'))
#watchdog = Watchdog(15)

wb_driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
wb_driver.fullscreen_window()

fb_login = FacebookLogin(email='briancfay@hotmail.com', password='password', browser='Chrome')
fb_login.login()
fb_driver = fb_login.driver

# time.sleep(5)

total_counter = 0
found_email_counter = 0



for file in csvfiles:
    if file == '/home/bcfay/Documents/PycharmProjects/ScrapeKnot/venv/DomesticWeddingPlannerEmailListCities.csv':
        continue

    #watchdog.stop()
    sheet_succ_counter = 0
    sheet_total_counter = 0
    if file.endswith(".csv"):
        print(file)
        df = pd.read_csv(file)
        df.dropna(subset=['First Name'], inplace=True)
        df.dropna(subset=['Last Name'], inplace=True)
        df_emails = df.copy()
        df_emails = df_emails.iloc[0:0]

        city_name = ""
        state_name = ""
        for j, row in df.iterrows():
            #watchdog.stop()


            city_name = row[2]
            state_name = row[3]

            if sheet_total_counter > 0:
                print("")
                print("We're in " + row[2] + ", " + row[3] + " on entry number " + str(total_counter) + ". ")
                print("Of that " + str(found_email_counter) + " have been sucsessful.   " + str(round((found_email_counter/total_counter),4)*100) + " %.")
                print(str(sheet_succ_counter) + " of " + str(sheet_total_counter) + " in this state have emails found.  " + str(round((sheet_succ_counter/sheet_total_counter),4)*100) + " %.")


            total_counter = total_counter + 1
            sheet_total_counter = sheet_total_counter + 1

            print("Selenium Facebook")

            fb_search_query = row["FB Page"]  # facebook link
            print(fb_search_query)
            fb_driver.get(fb_search_query)
            try:
                time.sleep(.5)
                entry_email = fb_driver.find_element_by_partial_link_text('@').text
                row[0] = entry_email
                print("Email inserted from Facebook")
                print(entry_email)
                found_email_counter = found_email_counter + 1
                sheet_succ_counter = sheet_succ_counter + 1
                print(" ")
                print(row)
                #df_emails.append(row)
                continue
            except (NoSuchElementException, Watchdog, Exception):
                print("Facebook Selenium attempt failed")

            print("Selenium website")
            try:

                print(row["Website"])
                wb_driver.get(row["Website"])
                wb_driver.fullscreen_window()
                entry_email = wb_driver.find_element_by_partial_link_text('@').text
                row[0] = entry_email
                print("email inserted from Selenium website")
                print(entry_email)
                print(" ")
                print(row)
                #df_emails.append(row)


            except (NoSuchElementException, Watchdog, Exception):
                print("Selenium website failed")
                print(row)
                print("Dropping row")
                continue
            # watchdog.stop()

            print(row)
            print("")

    index_names = df[df['Email Address'] == "needs to be found"].index
    df.drop(index_names, inplace=True)

    df.to_csv('/home/bcfay/Documents/PycharmProjects/ScrapeKnot/venv/Emails/cleanmails_' + 'knotPages' + '_' + city_name + '_' + state_name + '.csv', index=False)
    os.remove(file)
