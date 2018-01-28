'''
1.从数据库mysql中获得str_url记录
2.进行访问并解析出各种信息，并置visited为true
3.存储到攻略表中（以攻略id为主键）
'''
import pymysql as MYSQLdb
import re
import requests
from multiprocessing import Pool#multi processing

from requests.packages.urllib3.exceptions import ConnectTimeoutError

from mafengwo.items import StrategyItem

proxy = None
proxies = None
MAX_COUNT = 5

PROXY_POOL_URL='http://127.0.0.1:5000/get'
def get_proxy():  # 获得代理
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('获取代理时发生异常')
        return None

def save_str_to_mysql():
    url_query = "select * from str_url where visited =FALSE"
    url_visited = "update str_url set visited=TRUE where id= %s"

    proxy = get_proxy()
    proxies = {
        'http': 'http://' + proxy
    }
    try:
        conn = MYSQLdb.connect(host='localhost', user='root', passwd='123', db='mfw', port=3306, charset='utf8')#如果mysql没有密码：把这两个注释掉
        cur = conn.cursor()
        cur_update = conn.cursor() #这个游标用于更新
        count = cur.execute(url_query)# 执行查询操作
        print(count)
        update_count=0
        while count > 0:
            count -= 1
            str_url = cur.fetchone()#把这一行记录存下来
            url = str_url[1]
            #url='http://www.mafengwo.cn/i/5451641.html' #测试没有pay的网页

            print('设置标志位为True，表示已经访问过.更新了', update_count,'/',count,'条记录')
            print('攻略的url是：', url)
            print('使用的代理是：',proxy)
            try:
                # url = 'http://www.mafengwo.cn/i/2996543.html'
                # url='http://www.mafengwo.cn/i/5320703.html'#没有静态显示的出发时间的攻略
                response = requests.get(url, allow_redirects=False, proxies=proxies, timeout=30)
                cur_update.execute(url_visited, str_url[0])  # 设置这条记录已经访问，置访问标志位visited=TRUE
                update_count += 1
                conn.commit()  # ！！！这里：事务别忘了提交
                #print(html)
                response.encoding = response.apparent_encoding#注意！！：如果是request库的话需要转编码格式，但是scrapy已经帮我们弄好了一切
                html = response.text
                # print(response.text)
                item = StrategyItem()
                # 获取标题和作者
                pattern_title = re.compile(
                    r'<title>(.*?)</title>[\s\S]*?name="author"\s{1}content="(.*?),(.*?)"')  # [\s\S]*?能匹配任意的包括空格换行在内的字符
                # pattern = re.compile(r'<title>(.*?)</title>')
                str = re.search(pattern_title, html)
                if str:
                    item['title'] = str.group(1)
                    item['id'] = str.group(2)
                    item['author'] = str.group(3)

                # 获取天数、出发时间、人物
                pattern_tianshu = re.compile(
                    r'出发时间<span>/</span>(.*?)<i></i></li>[\s\S]*?出行天数<span>/</span>(\d*?)\s{1}天</li>'
                    + r'[\s\S]*?人物<span>/</span>(.*?)</li>[\s\S]*?</li>')
                str = re.search(pattern_tianshu, html)
                # 如果没有获取得到天数，先不存储这条数据了
                if str == None:
                    print('抓取不到出发时间，尝试下一条')
                    continue
                if str:
                    date = str.group(1)  # 出发的日期，把它分解开再存
                    item['tianshu'] = str.group(2)
                    item['partner'] = str.group(3)
                    #item['pay'] = str.group(4)
                    # 把出发时间分解成年、日、月，方便后续计算
                    pattern_date = re.compile(r'^(\d*?)-(\d*?)-(\d*?)$')  # 注意要匹配字符结尾，不然最后一个最小匹配会匹配到空
                    result = re.search(pattern_date, date)
                    if result:
                        item['year'] = result.group(1)
                        item['month'] = result.group(2)
                        item['day'] = result.group(3)

                # 获取费用（有的攻略有，有的攻略没有）
                pattern_pay = re.compile(r'人均费用<span>/</span>(.*?)RMB')#正则表达式要按照response.text来写，而不是浏览器显示的html代码来写，它俩不完全一样
                str = re.search(pattern_pay, html)
                if str:
                    item['pay'] = str.group(1)
                    #print('花销是：', str.group(1))
                else:
                    item['pay'] = 0
                    print('没有花销，设置花销为0')

                # 获取城市索引、城市名称
                pattern_city_info = re.compile(
                    r'相关目的地[\s\S]*?travel-scenic-spot/mafengwo/(\d*?).html"[\s\S]*?title="(.*?)"')
                # pattern_city_info = re.compile(r'相关目的地[\s\S]*?travel-scenic-spot/mafengwo/(.*?).html"')
                str = re.search(pattern_city_info, html)
                if str:
                    item['cityid'] = str.group(1)
                    item['city_name'] = str.group(2)

                print(item)
                save(item)
            except requests.exceptions.ConnectTimeout as e:
                print(e.args)
                print('访问时间过长，更换代理')
                proxy = get_proxy()
                proxies = {
                    'http': 'http://' + proxy
                }
                print('更换后的代理是：', proxy, proxies)
                continue
            except requests.exceptions.Timeout as e:
                print(e.args)
                print('访问时间过长，更换代理')
                proxy = get_proxy()
                proxies = {
                    'http': 'http://' + proxy
                }
                print('更换后的代理是：', proxy, proxies)
                continue
            except Exception as e:
                print(e.args)
                print('解析一个攻略出现了异常，放弃这个攻略，解析下一个攻略')
                continue


        conn.commit()
    except MYSQLdb.Error as e:
        print(e.args)
    finally:
        cur.close()
        conn.close()

def save(item):#存储一个攻略的各种信息到数据库中
    str_insert = "insert into strategy(id,title,author,tianshu,partner,pay," \
                 "year, month, day, cityid, city_name)" \
                 "VALUES (%s,%s,%s,   %s,%s,%s,    %s,%s,%s,%s,%s)"  # 攻略的mysql语句
    '''
    proxy = get_proxy()
    proxies = {
        'http': 'http://' + proxy
    }
    '''
    try:
        conn = MYSQLdb.connect(host='localhost', user='root', passwd='123', db='mfw', port=3306,
                               charset='utf8')  # 没有密码：把这两个注释掉
        cur = conn.cursor()
        cur.execute(str_insert, (item['id'], item['title'], item['author'], item['tianshu'],
                                 item['partner'], item['pay'], item['year'], item['month'],
                                 item['day'], item['cityid'], item['city_name']))  # 执行插入操作
        conn.commit()#经过验证，攻略能存进去
        print('提交了一次攻略的存储操作')
    except MYSQLdb.Error as e:
        print(e.args)
    finally:
        cur.close()
        conn.close()

def main():
    print('')
    save_str_to_mysql()


if __name__=='__main__':
    main()
    #pool = Pool()
    #pool.map(main, [i*10 for i in range(10)])#开启多线程