#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from fo.items import QuestionItem
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class S66law(scrapy.spiders.Spider):
    name = "66law"
    allowed_domains = ["66law.cn"]
    site_url = "http://www.66law.cn"
    start_urls = [
        "http://www.66law.cn/question/list_1_r1.aspx"
    ]

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
        "Connection": "keep-alive",
        "Host": "www.66law.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }

    def parse(self, response):
        selector = Selector(response)
        questions = selector.xpath('//td[@class="zx_lb_bt"]')
        for question in questions:
            item = QuestionItem()
            tag = question.xpath('a[@class="zx_fl"]/text()').extract()[0]
            title = question.xpath('a[@class="zx_tm"]/@title').extract()[0]
            url = question.xpath('a[@class="zx_tm"]/@href').extract()[0]
            full_url = self.site_url + str(url)
            item['url'] = full_url
            item['tag'] = tag
            item['title'] = title
            request = scrapy.Request(full_url, headers=self.headers,
                                     callback=self.parse_sub_page, dont_filter=True)
            request.meta['item'] = item
            yield request
        next_page = selector.xpath('//a[@class="nextprev"]/@href').extract()
        if next_page:
            if len(next_page) == 2:
                next_page = next_page[1]
            else:
                next_page = next_page[0]
            print "parse next page ======================" + self.site_url + str(next_page)
            yield scrapy.Request(self.site_url + str(next_page), headers=self.headers,
                                 callback=self.parse, dont_filter=True)

    def parse_sub_page(self, response):
        item = response.meta['item']
        # parse response and populate item as required
        selector = Selector(response)
        text = selector.xpath('//p[@class="f14 lh24 s-c666"]').extract()[0]
        soup = BeautifulSoup(text, 'lxml')
        question = ''.join(soup.find_all(text=True))
        answers = selector.xpath('//p[@class="f14 lh26"]/text()').extract()
        answer_list = []
        for answer in answers:
            answer_list.append(answer)
        item['question'] = question
        item['answers'] = '|'.join(answer_list).replace(' ', '').replace('\n', '')
        return item

