from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from time import sleep


class CrawlerBot:

    def __init__(self, username, password, run_in_background=False):
        if run_in_background:
            options = Options()
            options.add_argument("--headless")
            self.driver = webdriver.Chrome('chromedriver', options=options)
        else:
            self.driver = webdriver.Chrome('chromedriver')
        self.address = "https://helli1.iranlms.org"
        self.username = username
        self.password = password
        self.driver.get(self.address)

    def login(self):
        username = self.driver.find_element_by_id("username")
        username.send_keys(self.username)
        password = self.driver.find_element_by_id("password")
        password.send_keys(self.password)
        self.driver.find_element_by_id("loginbtn").click()

    def find_the_classes(self):
        r = BeautifulSoup(self.driver.page_source, "html.parser")
        url = r.find("a", {"class": "d-inline-block aabtn"}).get("href")
        self.driver.get(url)
        r = BeautifulSoup(self.driver.page_source, "html.parser")
        div_tags = r.find_all("div", {"class": "card-body row"})
        for div in div_tags:
            url = div.find("a").get("href")
            self.driver.get(url)
            r = BeautifulSoup(self.driver.page_source, "html.parser")
            li_tags = r.find_all("li", {"class": "activity bigbluebuttonbn modtype_bigbluebuttonbn"})
            for li in li_tags:
                url = li.find("a").get("href") if li.find("a") else None
                if url:
                    self.driver.get(url)
                    element = None
                    while not element:
                        r = BeautifulSoup(self.driver.page_source, "html.parser")
                        element = r.find("input", {"id": "join_button_input"})
                    button = element.get("onclick")
                    r = BeautifulSoup(self.driver.page_source, "html.parser")
                    class_title = r.find("h1").text
                    title = r.find_all("div", {"class": "card-body"})[1].find("h3").text
                    if not r.find("input", {"id": "join_button_input"}).get("disabled"):
                        url = button.split("'")[1]
                        self.driver.get(url)
                        number = self.find_the_number_of_users()
                        names = "\n".join(self.get_the_name_of_users())
                        print("«{}» - «{}» : {}".format(class_title, title, number))
                        if number:
                            print("کاربران : \n{}".format(names))
                    else:
                        print("«{}» - «{}» : {}".format(class_title, title, "ناموفق"))

    def find_the_number_of_users(self):
        button = None
        while not button:
            r = BeautifulSoup(self.driver.page_source, "html.parser")
            button = r.find("button", {"aria-label": "بستن ملحق شدن به مدال صدا"})
            sleep(1)
        while True:
            try:
                self.driver.find_element_by_id(button.get("id")).click()
            except Exception:
                sleep(0.4)
            else:
                break
        r = BeautifulSoup(self.driver.page_source, "html.parser")
        elements = r.find_all("h2")
        number = None
        for element in elements:
            text = re.findall('کاربران\xa0\([0-9]+\)', str(element))
            if text:
                try:
                    number = eval(text[0].replace('کاربران\xa0', '')) - 1
                    break
                except Exception:
                    continue
        return number

    def get_the_name_of_users(self):
        r = BeautifulSoup(self.driver.page_source, "html.parser")
        tag_class = re.findall('userItemContents--[A-Za-z0-9]+', self.driver.page_source)
        users = r.find_all("div", {"class": tag_class[0]})
        for user in users:
            try:
                if user.find("i").text != "(شما)":
                    moderator = re.findall('class="[a-zA-Z0-9\- ]*moderator[a-zA-Z0-9\- ]*"', str(user))
                    if moderator:
                        name = "{} ({})".format(user.find("span").text.strip(), "مدیر")
                    else:
                        name = "{} ({})".format(user.find("span").text.strip(), "کاربر")
                    yield name
            except Exception:
                continue

    def exit(self):
        self.driver.close()


username, password = input("Username : "), input("Password : ")
bot = CrawlerBot(username, password, True)
bot.login()
bot.find_the_classes()
bot.exit()

