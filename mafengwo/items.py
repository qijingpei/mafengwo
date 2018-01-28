# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
#这么引入之后，调用Item时就不用再写scrapy.xxx来调用了
from scrapy import Item, Field

class Str_urlItem(Item):
    id = Field()
    url =Field()


#创建Item
class StrategyItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #id = Field()#声明它是Field类型
    id = Field()#攻略的索引，按照蚂蜂窝攻略的索引号来
    title = Field()
    author = Field()
    #下面三个只有部分攻略有
    tianshu = Field()
    partner = Field()
    pay = Field()
    # 下面三个,目前有的从js中获取不到
    year = Field()
    month = Field()
    day = Field()

    cityid = Field()#城市的索引，值等于蚂蜂窝上的索引号
    city_name = Field()

class CityItem(Item):
    cityid = Field()
    city_name = Field()
    city_url = Field()
    nums = Field()#去过的人数
    detail = Field()#介绍


    #top3景点，每个景点有自己的url链接，链接到蚂蜂窝上
    top1 = Field()
    top1_url = Field()
    top2 = Field()
    top2_url = Field()
    top3 = Field()
    top3_url = Field()




