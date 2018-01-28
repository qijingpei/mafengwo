import json
import re
import requests
from scrapy import  Request
import pymysql as MYSQLdb # 起个别名
from mafengwo.items import StrategyItem, CityItem

def parse_str():
    #url='http://www.mafengwo.cn/i/6536459.html'
    url='http://www.mafengwo.cn/i/3313604.html'
    #url='http://www.mafengwo.cn/i/5320703.html'#没有静态显示的出发时间的攻略
    response= requests.get(url)
    response.encoding=response.apparent_encoding
    print(response.text)

    item= StrategyItem()

    #获取标题、攻略的索引号和作者
    pattern_title = re.compile(r'<title>(.*?)</title>[\s\S]*?name="author"\s{1}content="(.*?),(.*?)"')#[\s\S]*?能匹配任意的包括空格换行在内的字符
    #pattern = re.compile(r'<title>(.*?)</title>')
    str=re.search(pattern_title, response.text)
    if str:
        #print(str.group(1)+str.group(2))
        item['title'] = str.group(1)
        item['id'] = str.group(2)
        item['author'] = str.group(3)
        #print(item['title'])

    pattern_tianshu = re.compile(r'出发时间<span>/</span>(.*?)<i></i></li>[\s\S]*?出行天数<span>/</span>(\d*?)\s{1}天</li>'
                         +r'[\s\S]*?人物<span>/</span>(.*?)</li>[\s\S]*?人均费用<span>/</span>(\d*?)RMB</li>')
    str=re.search(pattern_tianshu,response.text)
    if str:
        print(str.group(1)+'天数：'+str.group(2)+str.group(3)+str.group(4))
        date=str.group(1)#出发的日期，把它分解开再存
        item['tianshu']=str.group(2)
        item['partner'] = str.group(3)
        item['pay'] = str.group(4)

        pattern_date = re.compile(r'^(\d*?)-(\d*?)-(\d*?)$')#注意要匹配字符结尾，不然最后一个最小匹配会匹配到空
        result = re.search(pattern_date, date)
        if result:
            item['year']= result.group(1)
            item['month']= result.group(2)
            item['day']= result.group(3)
            #print('获取到攻略的出发时间：' + result.group(1) + result.group(2) + result.group(3))

    pattern_city_info = re.compile(r'相关目的地[\s\S]*?travel-scenic-spot/mafengwo/(\d*?).html"[\s\S]*?title="(.*?)"')
    #pattern_city_info = re.compile(r'相关目的地[\s\S]*?travel-scenic-spot/mafengwo/(.*?).html"')
    str = re.search(pattern_city_info, response.text)
    if str:
        item['cityid']=str.group(1)
        item['city_name']= str.group(2)

    print(item)

def parse_city():
    url='http://www.mafengwo.cn/mdd/citylist/21536.html?mddid=21536&page=1'#没有静态显示的出发时间的攻略
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    print(response.text)

    pattern = re.compile(r'class="item ".*?href="(.*?)".*?data-id="(.*?)".*?title">(.*?)<p.*?<b>(.*?)</b>[\s\S]*?'
                         + r'class="detail">(.*?)</div>.*?TOP3</span>'
                         + r'.*?href="(.*?)".*?title="(.*?)".*?</a>'
                         + r'.*?href="(.*?)".*?title="(.*?)".*?</a>'
                         + r'.*?href="(.*?)".*?title="(.*?)".*?</a>'
                         + r'\s*?</dd>',
                         re.S)  # 这是有3个景点的，[\u4e00-\u9fa5]表示任意一个汉字
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
            print(city)

db = 'test'
def save_to_mysql():
    try:
        conn = MYSQLdb.connect(host='localhost', user='root', passwd='123', db=db, port=3306, charset='utf8')#没有密码：把这两个注释掉
        cur = conn.cursor()
        sql_update = "update student set sname=%s where sno=%s "
        sql_insert = "insert into student(sno, sname) values(%s, %s)"

        count = cur.execute(sql_update, ('李四','7'))# 先执行更新操作
        if count == 0:# 如果更新操作没有影响到一行，就执行插入,这样如果已经有数据就不用插入了
            cur.execute(sql_insert, ('7', '李四'))
            print('插入了一条数据到数据库')

        cur.close()
        conn.commit()
        conn.close()
    except MYSQLdb.Error as e:
        print(e.args)

PROXY_POOL_URL = 'http://127.0.0.1:5000/get'
def get_proxy():#获得代理
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('获取代理时发生异常')
        return None

cities_url = 'http://www.mafengwo.cn/mdd/citylist/21536.html?mddid=21536&page={page}'
def change_proxy():
    count = 1
    proxy = '1.82.216.135:80'

    for i in range(1, 200):
        count =0
        #if count % 2 == 0:  # 不断更新代理
        #    proxy = get_proxy()
        proxies = {
            'http': 'http://' + proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
        }
        response = requests.get('http://www.mafengwo.cn/', allow_redirects=False, proxies=proxies)
        while (response.status_code != 200):
            proxy = get_proxy()
            print('131行：更换了代理：', proxy)
            proxies = {
                'http': 'http://' + proxy  # requests.get()方法中代理用字典类型，而scrapy的代理则稍有不同
            }
            response = requests.get('http://www.mafengwo.cn/', allow_redirects=False, proxies=proxies)
        response = requests.get(cities_url.format(page=i), allow_redirects=False, proxies=proxies)
        print(count,'次访问,使用代理：',proxy,'访问了：', cities_url.format(page=i),'状态码：',response.status_code)

def get_pay():
    url = 'http://www.mafengwo.cn/i/3312527.html'
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    html = response.text
    print(html)
    pattern_pay = re.compile(r'人均费用<span>/</span>(.*?)RMB')
    str = re.search(pattern_pay, html)
    if str:
        print('花销是：', str.group(1))

def main():
    print('')
    #get_pay()
    #change_proxy()
    #save_to_mysql()
    #parse_city()
    parse_str()

if __name__ =='__main__':
    main()

'''

response = requests.get('http://www.mafengwo.cn/mdd/citylist/21536.html')
html = response.text
# print(html)
pattern = re.compile(r'count">共(.*?)页</span>')
total = re.search(pattern, html).group(1)  # 获取总页数
print('总页数：'+total)
'''
'''
#由一个城市的索引，生成这个城市所有攻略的url
url = 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10065.html'#测试用的用例,一个城市的url
index = re.search(r'mafengwo/(\d*?).html', url)  # 获取一个城市的标识
print('index:' + index.group(1))
# 凑出攻略列表界面的类型：http://www.mafengwo.cn/yj/10189/1-0-1.html'，10189是城市标识，1-0-1中最后1个1是攻略列表页面的标识，通过修改他们俩获得所有攻略
str_url = 'http://www.mafengwo.cn/yj/' + index.group(1) + '/1-0-1.html'  # 攻略列表的url
r = requests.get(str_url)
html = r.text
print('攻略界面：'+html)
'''