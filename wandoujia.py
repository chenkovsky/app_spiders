# -*- coding: utf-8 -*-
import sys
import re
import scrapy
from bs4 import BeautifulSoup


class AppItem(scrapy.Item):
    category = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()


class WanDoujiaSpider(scrapy.Spider):
    name = "wandoujia"
    start_urls = (
        'http://t.wdjcdn.com/upload/www/wandoujia.com/nav.js?1',
    )

    def header(self):
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.http.Request(url,
                                      headers=self.header(),
                                      callback=self.parse)

    def parse(self, response):
        tokens = response.body.split("<a class=\\\"cate-link\\\"")
        for token in tokens:
            sub_tokens = token.split("</a> <ul> <li")
            category = sub_tokens[0].split("\"")[1][5:-1]
            if category == "class=":
                continue
            url = "http://www.wandoujia.com/tag/" + category
            yield scrapy.http.Request(url=url,
                                      headers=self.header(),
                                      callback=self.CrawlAppPage,
                                      meta={"category": category})

    # 获取某个分类下的页数
    def CrawlAppPage(self, response):
        soup = BeautifulSoup(response.body)
        links = soup.select("div.pagination div.roboto a.page-item")
        page_num = int(links[-2].text)
        for i in range(1, page_num + 1):
            yield scrapy.http.Request(url=response.url + "_" + str(i),
                                      headers=self.header(),
                                      callback=self.CrawlApp,
                                      meta=response.meta)

    def CrawlApp(self, response):
        category = response.meta["category"]
        soup = BeautifulSoup(response.body)
        app_list = soup.select("ul#j-tag-list li div.app-desc h2 a")
        for app in app_list:
            title = app.text
            url = app["href"]
            yield AppItem({"category": category, "name": title, "url": url})
