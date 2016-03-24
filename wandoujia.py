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
            #"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            #"Connection":"keep-alive",
            #"Accept-Encoding":"gzip, deflate, sdch",
            #"Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            #"Cookie":"hxck_sq_common=LoginStateCookie=; Hm_lvt_cb1b8b99a89c43761f616e8565c9107f=1422013312,1422070860; Hm_lpvt_cb1b8b99a89c43761f616e8565c9107f=1422070860; __utma=232688221.1600897606.1422070864.1422070864.1422070864.1; __utmc=232688221; __utmz=232688221.1422070864.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=%E8%82%A1%E7%A5%A8%E5%88%97%E8%A1%A8%20hexun; ASP.NET_SessionId=uofawnqc5404mx455ocaif55; vjuids=2e5d1a4f.14b1696e9ec.0.01e018a5; hxck_webdev1_general=stocklist=600216_1; __utma=194262068.170830345.1422013312.1422070864.1422075855.3; __utmc=194262068; __utmz=194262068.1422075855.3.3.utmcsr=so.hexun.com|utmccn=(referral)|utmcmd=referral|utmcct=/default.do; vjlast=1422013164.1422070859.13; HexunTrack=SID=2015012319392701377959271ecde4f0bbf60c73654e82ee4&CITY=31&TOWN=0"
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
