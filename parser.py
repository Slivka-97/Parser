from datetime import datetime, timedelta
import re
import calendar

import requests
from bs4 import BeautifulSoup as BS

name_mount = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}


def convert_in_correct_form(convert):
    return "0" + str(convert) if len(str(convert)) == 1 else str(convert)


def get_date(date: str):
    if date.find("сегодня") >= 0:
        d = datetime.now()
        only_min_and_sec = date.replace('сегодня в ', "")
        year = d.year
        day = convert_in_correct_form(d.day)
        month = convert_in_correct_form(d.month)
    elif date.find("вчера") >= 0:
        only_min_and_sec = date.replace('вчера в ', "")
        d = datetime.now() - timedelta(days=1)
        year = d.year
        day = convert_in_correct_form(d.day)
        month = convert_in_correct_form(d.month)
    else:
        d = datetime.now()
        year = re.findall(r'\d{4}', date)
        if len(year) > 0:
            year = year[0]
        else:
            year = d.year
        only_min_and_sec = date.split(" в ")[1]
        day = date[0:2]
        month = name_mount.get(re.findall(r'[а-яА-ЯёЁ]+', date)[0])

    correct_data = str(year) + "-" + month + "-" + day + " " + only_min_and_sec
    date_formatter = "%Y-%m-%d %H:%M"
    return datetime.strptime(correct_data, date_formatter)


r = requests.get("https://bikepost.ru/index/page1/")
html = BS(r.content, 'html.parser')
t = html.find_all(class_="topic")

for el in t:
    title = el.find(class_="title-topic")
    author = el.find(class_="panel username")
    no_correct_data = el.find(class_="panel username").find_next_sibling().find_next_sibling().text
    if not no_correct_data[-1].isdigit():
        no_correct_data = el.find(class_="panel username").find_next_sibling().text

    date = get_date(no_correct_data)

    print(title.text)
    print(author.text)
    print(date)
    print("------------------")
