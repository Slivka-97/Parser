import requests
from bs4 import BeautifulSoup as BS

r = requests.get("https://bikepost.ru/index/page1/")
html = BS(r.content, 'html.parser')
t = html.find_all(class_="topic")


for el in t:
    w = el.find(class_= "title-topic")
    e = el.find(class_="panel username").find_next()
    q = el.find(class_="panel")
    print(w.text)
    print(e.text)
    print(q.text)
