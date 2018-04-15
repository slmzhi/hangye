# -*- coding:utf-8 -*-
with open('./wang.html', 'r') as f:
    data = f.read()

from lxml import html

doc = html.fromstring(data)
titles = []
urls = []
for i in doc.xpath('//ul[@class="numlist"]//li//a'):
    titles.append(i.xpath('@title'))
    urls.append(i.xpath('@href'))
print(titles)
print(len(titles))
print(urls)
print(len(urls))