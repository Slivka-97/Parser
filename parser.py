from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup as BS
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import host, user, password, database, port

url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(url, echo=False)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Articles(Base):
    __tablename__ = 'Articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    data = Column(String)


class Parser(Base):
    __tablename__ = 'Parser'
    id = Column(Integer, primary_key=True)
    site_name = Column(String)
    count_proc = Column(Integer)


# Base.metadata.create_all(engine)


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


def get_date(data: str):
    if data.find("сегодня") >= 0:
        d = datetime.now()
        only_min_and_sec = data.replace('сегодня в ', "")
        year = d.year
        day = convert_in_correct_form(d.day)
        month = convert_in_correct_form(d.month)
    elif data.find("вчера") >= 0:
        only_min_and_sec = data.replace('вчера в ', "")
        d = datetime.now() - timedelta(days=1)
        year = d.year
        day = convert_in_correct_form(d.day)
        month = convert_in_correct_form(d.month)
    else:
        d = datetime.now()
        year = re.findall(r'\d{4}', data)
        if len(year) > 0:
            year = year[0]
        else:
            year = d.year
        only_min_and_sec = data.split(" в ")[1]
        day = data[0:2]
        month = name_mount.get(re.findall(r'[а-яА-ЯёЁ]+', data)[0])

    correct_data = str(year) + "-" + month + "-" + day + " " + only_min_and_sec

    return correct_data


next_page = True
page = 1
parser = session.query(Parser)
for new_parser in parser:  # цикл для каждой записи в таблице базы данных
    for i in range(new_parser.count_proc):  # цикл для каждого пока в текущей записи
        while next_page:  # цикл для каждой страницы на сайте
            req = requests.get(f"https://{new_parser.site_name}/index/page{page}/")
            html = BS(req.content, 'html.parser')

            max_page = html.find(class_='pagination').find_all('li')[9].text
            max_page = max_page.replace("... ", "")
            if max_page == page:
                next_page = False
            else:
                page += 1

            topic = html.find_all(class_="topic")
            for el in topic:
                title = el.find(class_="title-topic")
                author = el.find(class_="panel username")
                no_correct_data = el.find(class_="panel username").find_next_sibling().find_next_sibling().text
                if not no_correct_data[-1].isdigit():
                    no_correct_data = el.find(class_="panel username").find_next_sibling().text

                date = get_date(no_correct_data)

                new_articles = session.query(Articles).filter(Articles.title == title.text,
                                                              Articles.author == author.text,
                                                              Articles.data == date).count()
                if new_articles == 0:
                    art = Articles(title=title.text, author=author.text, data=date)
                    session.add(art)
                    session.commit()
