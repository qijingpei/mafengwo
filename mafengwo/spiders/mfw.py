# -*- coding: utf-8 -*-
import json
import re
import requests
from scrapy import Request, Spider

from mafengwo.items import StrategyItem, CityItem, Str_urlItem

'''
注明：控制台最后输出的大量的403错误，是正常的，这些403错误的网页已经被再次访问直到爬取到数据，
所以不用担心
'''
class MfwSpider(Spider):
    name = "mfw"
    allowed_domains = ["www.mafengwo.cn"]
    start_urls = ['http://www.mafengwo.cn/']#这里要写成....cn而不是.com，不然解析不了攻略

    cities_url = 'http://www.mafengwo.cn/mdd/citylist/21536.html?mddid=21536&page={page}'

    test_str_url = 'http://www.mafengwo.cn/i/6536459.html'#单个攻略的url
    test_str_url2 = 'http://www.mafengwo.cn/i/5320703.html'#没有静态显示而是用js显示的出发时间的攻略
    test_str_list_url = 'http://www.mafengwo.cn/yj/10065/1-0-1.html'

    PROXY_POOL_URL = 'http://127.0.0.1:5000/get'
    MAX_COUNT = 5
    proxy = None# 建立一个全局的变量，来存代理
    #proxy = '185.35.67.191:1189'
    #proxy = '127.0.0.1:5000'
    # proxy = '163.172.211.176:3128'
    # proxies = {
    #     'http': 'http://' + proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
    # }
    str_count = 0

    def get_proxy(self):#获得代理
        try:
            response = requests.get(self.PROXY_POOL_URL)
            if response.status_code == 200:
                return response.text
            return None
        except ConnectionError:
            print('获取代理时发生异常')
            return None

    def get_html(self, url, count=1):# count默认值为1，如果有赋值则不使用默认值
        print('正在抓取', url)
        print('Trying Count', count)
        if count >= self.MAX_COUNT:
            print('Tried Too Many Counts')
            return None
        try:
            if self.proxy==None :# 如果代理不存在
                self.proxy = self.get_proxy()
            proxies = {
                'http': 'http://' + self.proxy
            }
            print('使用了代理：', self.proxy)
            response = requests.get(url, allow_redirects=False, proxies=proxies)#可以设定超时时间30s

            if response.status_code == 200:
                return response.text
            else:
                # 更换代理，重新访问
                print('302/403等错误')
                self.proxy = self.get_proxy()#获得新代理
                if self.proxy:
                    print('Using Proxy', self.proxy)
                    count = count + 1
                    return self.get_html(url, count)#更改后的代理，也可能不能用
                else:
                    print('Get Proxy Failed')
                    return None# 没有可用代理的时候返回none
        except ConnectionError as e:
            print('Error Occurred', e.args)# 输出错误信息
            self.proxy = self.get_proxy()
            count += 1
            return self.get_html(url, count)

    # 构建scrapy初始的请求
    def start_requests(self):
        #self.get_total_city_pages()
        self.proxy = self.get_proxy()
        #total = self.get_total_city_pages()#获取城市总页数
        total = 400
        print('城市总页数：'+str(total))#能够正确输出，注意如果不提交请求的话系统会报错误：TypeError: 'NoneType' object is not iterable,先不用管

        #测试用url= 'http://www.mafengwo.cn/mdd/citylist/21536.html?mddid=21536&page=1'

        for i in range(6, 7):#左闭右开
            print('正在获取第'+str(i)+'/'+str(total)+'页城市的信息')
            '''
            if self.proxy:  # 如果代理存在
                proxies = {
                    'http': 'http://' + self.proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
                }

                # 如果当前代理不行了，更换一下代理
                try:
                    print('1.1')
                    response = requests.get('http://www.mafengwo.cn/', allow_redirects=False, proxies=proxies)
                    print('1.2')
                    while response.status_code != 200:
                        print('1.3')
                        self.proxy = self.get_proxy()
                        print('93行：更换了代理：', self.proxy)
                        proxies = {
                            'http': 'http://' + self.proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
                        }
                        response = requests.get('http://www.mafengwo.cn/', allow_redirects=False, proxies=proxies)
                except Exception as e:
                    print('100行，解析每一页城市前，检测代理是否可用时出错了', e.args)
                    continue

            yield Request(self.cities_url.format(page=i), callback=self.parse_one_page_cities,
                          meta={'proxy': 'http://' + self.proxy})#解析每页城市
            '''
            yield Request(self.cities_url.format(page=i), callback=self.parse_one_page_cities,
                          meta={'proxy': 'http://' + self.proxy})  # 不使用动态代理解析每页城市


        #测试解析一页攻略：通过
        #yield Request(self.test_str_list_url, self.parse_one_page_strategies_url)
        # 测试解析单个攻略：通过
        #yield Request(self.test_str_url, self.parse_strategy)


    #获取城市列表总页数，成功

    def get_total_city_pages(self):
        html = self.get_html('http://www.mafengwo.cn/mdd/citylist/21536.html')
        #response.encoding = response.apparent_encoding
        #print(html)
        pattern = re.compile(r'count">共(.*?)页</span>')
        total = re.search(pattern, html).group(1)  # 获取总页数
        if total:
            #print('城市总页数：'+total)
            return int(total)
        else:
            print('没有获取到城市总页数：')
            return self.get_total_city_pages()

    # 解析一页的城市，小于等于9个
    def parse_one_page_cities(self, response):#解析一页的城市，小于等于9个
        #print(response.text)
        pattern = re.compile(r'class="item ".*?href="(.*?)".*?data-id="(.*?)".*?title">(.*?)<p.*?<b>(.*?)</b>[\s\S]*?'
                             + r'class="detail">(.*?)</div>.*?TOP3</span>'
                             + r'.*?href="(.*?)".*?title="(.*?)".*?</a>'
                             + r'.*?href="(.*?)".*?title="(.*?)".*?</a>'
                             + r'.*?href="(.*?)".*?title="(.*?)".*?</a>'
                             + r'\s*?</dd>',
                             re.S)  # 这是获取了3个景点的，基本上热门城市都是3个景点，不是的先不考虑了
        items = re.findall(pattern, response.text)  # 从中获取所有的城市
        if items:
            for item in items:
                city = CityItem()
                city['city_url'] = 'http://www.mafengwo.cn' + item[0].strip()  # item[i]的话从0开始，而如果是item.group(i)的话从1开始！！！
                city['cityid'] = item[1]
                city['city_name'] = item[2].strip()  # 城市名字
                city['nums'] = int(item[3])  # 人数
                city['detail'] = item[4].strip()  # 城市介绍
                city['top1_url'] = 'http://www.mafengwo.cn' + item[5]
                city['top1'] = item[6]
                city['top2_url'] = 'http://www.mafengwo.cn' + item[7]
                city['top2'] = item[8]
                city['top3_url'] = 'http://www.mafengwo.cn' + item[9]
                city['top3'] = item[10]
                #(city)
                #print('这个城市的URL是：'+city.get('url'))
                #请求一个城市下的所有攻略，
                # 1.获取一个城市的所有攻略的总页数
                index = city['cityid']  # 获取一个城市的标识
                #str_total = self.get_strategy_total_page(index)#获取一个城市的所有攻略的总页数
                str_total = 100
                # 2.调用解析一“页”攻略的方法，解析这个城市下的每一页攻略

                print('获取到城市的索引：'+index)
                yield city
                #continue #先不存攻略，只存城市
                if str_total >= 100:
                    page = 100
                else:
                    page = int(str_total)
                for i in range(1, page):  # 左闭右开
                    str_list_url = 'http://www.mafengwo.cn/yj/' + index + '/1-0-' + \
                                   str(i) + '.html'  # 攻略strategy列表的url
                    print('攻略列表的url：' + str_list_url)
                    #print('正在解析第'+str(i)+'/'+str(str_total)+'页攻略')
                    print('正在解析第' , str(i) , '/' , page , '页攻略')
                    '''
                    if self.proxy:  # 如果代理存在
                        proxies = {
                            'http': 'http://' + self.proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
                        }

                    # 如果当前代理不行了，更换一下代理
                    try:
                        response = requests.get('http://www.mafengwo.cn/', allow_redirects=False, proxies=proxies)
                        while (response.status_code != 200):
                            self.proxy = self.get_proxy()
                            print('184行：更换了代理：', self.proxy)
                            proxies = {
                                'http': 'http://' + self.proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
                            }
                            response = requests.get('http://www.mafengwo.cn/', allow_redirects=False, proxies=proxies)
                    except Exception as e:
                        print('190行，解析每一页攻略前，检测代理是否可用时出错了',e.args)
                        continue
                    #yield Request(str_list_url, callback=self.parse_one_page_strategies,
                    #              meta={'proxy': 'http://' + self.proxy})  # 提交请求，解析这个城市下的每一页攻略
                    yield Request(str_list_url, callback=self.parse_one_page_strategies_url,
                                meta={'proxy': 'http://' + self.proxy})  # 提交请求，解析这个城市下的每一页攻略
                    '''
                    yield Request(str_list_url, callback=self.parse_one_page_strategies_url,
                                  meta={'proxy': 'http://' + self.proxy})  # 不使用代理解析这个城市下的每一页攻略
                #break#先测试一个城市



    #获取一个城市的所有攻略的总页数
    def get_strategy_total_page(self, index):  # 获取一个城市的所有攻略的总页数, index是一个城市的标识
        #print('index:' + index)
        # 凑出攻略列表界面的类型：http://www.mafengwo.cn/yj/10189/1-0-1.html'，10189是城市标识，1-0-1中最后1个1是攻略列表页面的标识，通过修改他们俩获得所有攻略
        str_url = 'http://www.mafengwo.cn/yj/' + index + '/1-0-1.html'  # 攻略列表的url
        html = self.get_html(str_url)
        pattern = re.compile(r'class="count">共<span>(.*?)</span>页')
        total = re.search(pattern, html)
        if total:
            print('这个城市攻略总页数：' + total.group(1))  # 获取攻略总页数，这里的“.group(1)”会从中提取出页数
            return int(total.group(1))
        else:
            print('获取这个城市的攻略的总页数失败或者这个城市没有攻略')
            return 0

    #解析一页攻略（现在不用到这个函数）
    def parse_one_page_strategies(self, response):
        #print('1.3开始解析一页攻略')
        #url = 'http://www.mafengwo.cn/yj/10065/1-0-1.html' #测试用的用例
        #print('response.text'+response.text[0:100])
        html = response.text
        # print(html)
        # 网页中攻略的网址：href="/i/6536459.html"  ，匹配之
        pattern = re.compile(r'href="(/i/.*?.html)"\s{1}target="_blank">[\s\S]*?</h2>')
        # \s:表示空白字符，\s{1}：表示1个空格,可以用来处理去掉“宝藏”这种url
        items = re.findall(pattern, html)
        print(items)
        if items:
            for item in items:
                item = 'http://www.mafengwo.cn' + item
                print('捕获到每个攻略：'+item)
                #break # 用于测试，先让后面的代码不运行了
                if self.proxy:  # 如果代理存在
                    proxies = {
                        'http': 'http://' + self.proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
                    }

                # 如果当前代理不行了，更换一下代理
                try:
                    response = requests.get(item, allow_redirects=False, proxies=proxies, timeout=40)
                    while (response.status_code != 200):
                        self.proxy = self.get_proxy()
                        print('232行：更换了代理：', self.proxy)
                        proxies = {
                            'http': 'http://' + self.proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
                        }
                        response = requests.get(item, allow_redirects=False, proxies=proxies, timeout=40)
                except:
                    print('237行，解析单个攻略前，检测代理是否可用时出错了')
                    continue

                yield Request(item, callback=self.parse_strategy,
                              meta={'proxy': 'http://' + self.proxy})#解析单个攻略

    # 解析一页攻略，并且只把每个攻略的url存储到数据库就结束
    def parse_one_page_strategies_url(self, response):
        html = response.text
        # print(html)
        # 网页中攻略的网址：href="/i/6536459.html"  ，匹配之
        #pattern = re.compile(r'href="(/i/.*?.html)"\s{1}target="_blank">[\s\S]*?</h2>')
        # \s:表示空白字符，\s{1}：表示1个空格,可以用来处理去掉“宝藏”这种url
        pattern = re.compile(r'href="/i/(.*?).html"\s{1}target="_blank">[\s\S]*?</h2>')
        items = re.findall(pattern, html)
        print(items)
        if items:
            for item in items:
                str_url = Str_urlItem()

                str_url['id'] = item
                str_url['url'] = 'http://www.mafengwo.cn/i/' + item + '.html'
                print('捕获到每个攻略的url：http://www.mafengwo.cn/i/' + item + '.html')
                yield str_url

    # 解析单个攻略的url进行解析，得到出发时间、天数、标题、城市等信息（现在不用到这个函数）
    def parse_strategy(self, response):
        try:
            # url = 'http://www.mafengwo.cn/i/2996543.html'
            # url='http://www.mafengwo.cn/i/6536459.html'
            #url = 'http://www.mafengwo.cn/i/3313604.html'
            # url='http://www.mafengwo.cn/i/5320703.html'#没有静态显示的出发时间的攻略
            #response.encoding = response.apparent_encoding#注意！！：如果是request库的话需要转编码格式，但是scrapy已经帮我们弄好了一切
            #print(response.text)

            item = StrategyItem()

            # 获取标题和作者
            pattern_title = re.compile(
                r'<title>(.*?)</title>[\s\S]*?name="author"\s{1}content="(.*?),(.*?)"')  # [\s\S]*?能匹配任意的包括空格换行在内的字符
            # pattern = re.compile(r'<title>(.*?)</title>')
            str = re.search(pattern_title, response.text)
            if str:
                item['title'] = str.group(1)
                item['id'] = str.group(2)
                item['author'] = str.group(3)

            # 获取天数、出发时间、人物
            pattern_tianshu = re.compile(
                r'出发时间<span>/</span>(.*?)<i></i></li>[\s\S]*?出行天数<span>/</span>(\d*?)\s{1}天</li>'
                + r'[\s\S]*?人物<span>/</span>(.*?)</li>[\s\S]*?</li>')
            str = re.search(pattern_tianshu, response.text)
            # 如果没有获取得到天数，先不存储这条数据了
            if str == None:
                print('抓取不到出发时间，尝试下一条')
                return# 有循环时用continue1！
            if str:
                date = str.group(1)  # 出发的日期，把它分解开再存
                item['tianshu'] = str.group(2)
                item['partner'] = str.group(3)
                # item['pay'] = str.group(4)
                # 把出发时间分解成年、日、月，方便后续计算
                pattern_date = re.compile(r'^(\d*?)-(\d*?)-(\d*?)$')  # 注意要匹配字符结尾，不然最后一个最小匹配会匹配到空
                result = re.search(pattern_date, date)
                if result:
                    item['year'] = result.group(1)
                    item['month'] = result.group(2)
                    item['day'] = result.group(3)

            # 获取费用（有的攻略有，有的攻略没有）
            pattern_pay = re.compile(r'人均费用<span>/</span>(.*?)RMB')  # 正则表达式要按照response.text来写，而不是浏览器显示的html代码来写，它俩不完全一样
            str = re.search(pattern_pay, response.text)
            if str:
                item['pay'] = str.group(1)
                # print('花销是：', str.group(1))
            else:
                item['pay'] = 0
                print('没有花销，设置花销为0')

            # 获取城市索引、城市名称
            pattern_city_info = re.compile(r'相关目的地[\s\S]*?travel-scenic-spot/mafengwo/(\d*?).html"[\s\S]*?title="(.*?)"')
            # pattern_city_info = re.compile(r'相关目的地[\s\S]*?travel-scenic-spot/mafengwo/(.*?).html"')
            str = re.search(pattern_city_info, response.text)
            if str:
                item['cityid'] = str.group(1)
                item['city_name'] = str.group(2)

            #print(item)
            print('使用了代理:', self.proxy)
            print('提交给pipeline')
            self.str_count += 1
            print('捕获的攻略条数：', self.str_count)
            yield item
        except:
            print('解析一个攻略出现了异常，放弃这个攻略，解析下一个攻略')
            return




