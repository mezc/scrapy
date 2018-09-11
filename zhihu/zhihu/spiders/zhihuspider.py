# -*- coding: utf-8 -*-
import json

import scrapy

from zhihu.items import ZhihuItem

"""
获取知乎用户关注列表的用户信息，再获取关注列表用户的关注列表
获取知乎用户的粉丝列表的用户信息，再获取粉丝列表的关注列表
"""
class ZhihuspiderSpider(scrapy.Spider):
    name = 'zhihuspider'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']
    start_user = "excited-vczh"
    #用户信息
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"
    user_query = "allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics"
    #关注列表
    followee_url = "https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}"
    followee_query = "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"
    #被关注列表
    follower_url = "https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}"
    follower_query = "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"

    def start_requests(self):
        #用户信息
        yield scrapy.Request(url=self.user_url.format(user=self.start_user,include=self.user_query),callback=self.parse_user)
        #关注列表
        yield scrapy.Request(url=self.followee_url.format(user=self.start_user,include=self.followee_query,offset=0,limit=20),callback=self.parse_followee)
        #粉丝列表
        yield scrapy.Request(url=self.follower_url.format(user=self.start_user,include=self.follower_query,offset=0,limit=20),callback=self.parse_follower)

    def parse_user(self, response):
        # print(response.text)
        result = json.loads(response.text)
        item = ZhihuItem()

        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        #获取关注列表的关注列表
        yield scrapy.Request(url=self.followee_url.format(user=result.get("url_token"),include=self.followee_query,offset=0,limit=20),callback=self.parse_followee)
        # #获取粉丝列表的关注列表
        # yield scrapy.Request(url=self.follower_url.format(user=result.get("url_token"),include=self.follower_query),offset=0,limit=20),callback=self.parse_follower)

    def parse_followee(self,response):
        # print(response.text)
        results = json.loads(response.text)
        #从关注列表获取url_token
        if "data" in results.keys():
            for result in results.get("data"):
                #获取关注列表的用户信息
                yield scrapy.Request(url=self.user_url.format(user=result.get("url_token"),include=self.user_query),callback=self.parse_user)
        #获取下一页关注列表
        if "paging" in results.keys() and results.get("paging").get("is_end") == False:
            next_page = results.get("paging").get("next")
            yield scrapy.Request(url=next_page,callback=self.parse_followee)

    def parse_follower(self,response):
        # print(response.text)
        results = json.loads(response.text)
        #从粉丝列表获取url_token
        if "data" in results.keys():
            for result in results.get("data"):
                #获取粉丝列表的用户信息
                yield scrapy.Request(url=self.user_url.format(user=result.get("url_token"),include=self.user_query),callback=self.parse_user)
        #获取下一页粉丝列表
        if "paging" in results.keys() and results.get("paging").get("is_end") == False:
            next_page = results.get("paging").get("next")
            yield scrapy.Request(url=next_page,callback=self.parse_follower)