# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql as MYSQLdb # 起个别名
import pymongo
class MysqlPipeline(object):
    city_count=0
    str_count=0
    str_url_count=0
    def __init__(self, mysql_host, mysql_db, mysql_user, mysql_password):
        self.mysql_host = mysql_host
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password

    @classmethod  # 定义一个类的方法，应该是类似于静态方法，用来从settings中获取配置信息
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_db=crawler.settings.get('MYSQL_DATABASE'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
        )
    def process_item(self, item, spider):
        try:
            conn = MYSQLdb.connect(host=self.mysql_host, user=self.mysql_user, passwd=self.mysql_password,
                                   db=self.mysql_db, port=3306, charset='utf8')  # 没有密码：把用户名和密码两个注释掉
            cur = conn.cursor()
            city_update = "update city set sname='1' where sno='1' " #城市的mysql语句
            city_insert = "insert into city(cityid, city_name,city_url,nums,detail," \
                          "top1, top1_url, top2, top2_url, top3, top3_url) " \
                          "values(%s,%s,%s,%s,%s   ,%s,%s,%s,%s,%s,%s)"
            str_update = "update strategy set title=%s,author=%s,tianshu=%s,partner=%s,pay=%s," \
                          "year=%s, month=%s, day=%s, cityid=%s, city_name=%s " \
                          "where id=%s " #攻略的mysql语句
            str_insert = "insert into strategy(id,title,author,tianshu,partner,pay," \
                          "year, month, day, cityid, city_name)" \
                          "VALUES (%s,%s,%s,   %s,%s,%s,    %s,%s,%s,%s,%s)" #攻略的mysql语句

            str_url_insert = "insert into str_url(id,url,visited) VALUES (%s, %s, FALSE )"# 插入一条攻略的url
            '''
            if 'author' in item:  # 如果是攻略的item(只有攻略才有作者)
                count = cur.execute(str_update, (item['title'],item['author'],item['tianshu'],
                                        item['partner'], item['pay'], item['year'], item['month'],
                                        item['day'], item['cityid'], item['city_name'], item['id']))
                # 如果记录完全一样，更新操作会返回0，这时会进入插入操作，
                # 插入操作会报主键重复错，异常被捕获了可以用管
                #print('count:',count)
                if count == 0:  # 如果更新操作没有影响到一行，就执行插入,这样如果已经有数据就不用插入了
                    cur.execute(str_insert, (item['id'], item['title'], item['author'], item['tianshu'],
                                             item['partner'], item['pay'], item['year'], item['month'],
                                             item['day'], item['cityid'], item['city_name']))
                self.str_count += 1
                print('存储了', self.str_count, '条攻略的数据到数据库')
            '''
            if 'nums' in item:  # 如果是城市的item
                count = cur.execute(city_insert, (item['cityid'], item['city_name'], item['city_url'],
                                                 item['nums'], item['detail'], item['top1'], item['top1_url'],
                                                 item['top2'], item['top2_url'], item['top3'], item['top3_url']))
                self.city_count += 1
                print('存储了', self.city_count, '条城市的数据到数据库')

            else: #如果是存一个攻略的url
                cur.execute(str_url_insert, (item['id'], item['url']))
                self.str_url_count += 1
                print('存储了', self.str_url_count, '条攻略的url到数据库')
            '''
            count = cur.execute(sql_update, ('李四', '7'))  # 先执行更新操作
            if count == 1:
                print('更新了一条数据库')
            if count == 0:  # 如果更新操作没有影响到一行，就执行插入,这样如果已经有数据就不用插入了
                cur.execute(sql_insert, ('7', '李四'))
                print('插入了一条数据到数据库')
            '''
            conn.commit()
        except MYSQLdb.Error as e:
            print('捕获到数据库异常',e.args)
        except Exception as e2:
            print('捕获到数据库异常', e2.args)

        finally:
            cur.close()
            conn.close()

        return item



'''
class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod#定义一个类的方法，应该是类似于静态方法，用来从settings中获取配置信息
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        #通过更新来去重，按照攻略的索引来去重
        if 'author' in item:# 如果是攻略的item(只有攻略才有作者)
            self.db['strategy'].update({'id': item['id']}, {'#set:': item}, True)#如果数据库中的url_token不等于item中的url——token，则更新之
        else:# 如果是城市的item
            self.db['city'].update({'cityid': item['cityid']}, {'$set': item}, True)
        return item
'''
