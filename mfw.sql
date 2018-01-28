SHOW TABLES;
CREATE TABLE strategy(#攻略表
	id VARCHAR(20) PRIMARY KEY,
	title VARCHAR(50),
	author VARCHAR(20),
	tianshu INT,
	partner VARCHAR(20),
	pay INT,
	`year` INT,
	`month` INT,
	`day` INT,
	cityid VARCHAR(20),
	city_name VARCHAR(20)
);
SELECT * FROM strategy;
SELECT * FROM strategy GROUP BY cityid;
SELECT COUNT(*) FROM strategy;
SELECT * FROM strategy WHERE id ='5321199';
SELECT * FROM strategy WHERE city_name ='呼伦贝尔';
DESC strategy;
INSERT INTO strategy(id,title) VALUES('1','题目1');
#delete from student where sno=7;

CREATE TABLE str_url(#攻略的url表
	id VARCHAR(20) PRIMARY KEY,
	url VARCHAR(100),
	visited BOOLEAN	DEFAULT FALSE# 0 表示false
);
#SELECT count(*) FROM str_url
SELECT * FROM str_url ORDER BY visited;
SELECT * FROM str_url WHERE id='3289473';
SELECT * FROM str_url WHERE visited=TRUE;
SELECT * FROM str_url WHERE visited=FALSE;
UPDATE str_url SET visited=FALSE;
INSERT INTO str_url(url,visited) VALUES ('攻略1', FALSE);
#  delete from str_url; 
#  drop table str_url;

CREATE TABLE city(
	cityid VARCHAR(20) PRIMARY KEY,
	city_name VARCHAR(20),
	city_url VARCHAR(100),
	nums INT, #去过的人数
	detail VARCHAR(200),#介绍
	image VARCHAR(200),-- 图片
	
	top1 VARCHAR(40),#top3景点，每个景点有自己的url链接，链接到蚂蜂窝上
	top1_url VARCHAR(100),
	top2 VARCHAR(40),
	top2_url VARCHAR(100),
	top3 VARCHAR(40),
	top3_url VARCHAR(100)
);
#drop table city;
SELECT * FROM city ORDER BY nums DESC;
SELECT city_name,nums FROM city ORDER BY nums DESC LIMIT 10;
SELECT city_name AS city_name2,nums FROM city ORDER BY nums DESC LIMIT 11,10;

SELECT * FROM strategy ORDER BY city_name;
SELECT * FROM strategy WHERE id='5342577';
SELECT COUNT(*) FROM strategy WHERE city_name='北京1';
#DELETE FROM strategy;

SELECT COUNT(*) AS nums ,city_name,cityid FROM strategy GROUP BY city_name ORDER BY COUNT(*) DESC LIMIT 10;# 找在攻略表中访问城市出现最多的10条
SELECT COUNT(*) AS nums,`month`,cityid FROM strategy WHERE cityid = '10186' GROUP BY MONTH ;#丽江每个月的访问量
/* 
select * from(
	SELECT * FROM strategy WHERE cityid='10186' AND pay>0 order by pay desc limit 10,SELECT count(*) FROM strategy WHERE cityid='10186' AND pay>0 
	)
*/
SELECT AVG(pay) AS pay,cityid FROM strategy WHERE cityid='10186' AND pay>0 ;#某城市总的平均旅游花费
SELECT AVG(pay) AS pay,MONTH,cityid  FROM strategy WHERE cityid='10186' AND pay>0 GROUP BY MONTH;#某城市每个月的平均旅游花费（不和月访问量一起查询是因为有些攻略没写花费，即花费是0）

#找到所有的满足月份的攻略
SELECT COUNT(*) AS nums ,city_name,cityid FROM strategy 
WHERE id IN
(SELECT id FROM strategy WHERE MONTH = 1) 
GROUP BY city_name ORDER BY COUNT(*) DESC LIMIT 10;

#>找到所有的满足开始时间和结束时间的攻略：
SELECT COUNT(*) AS nums ,city_name,cityid FROM strategy 
WHERE id IN
(SELECT id FROM strategy WHERE (MONTH >1 AND MONTH<3) OR(MONTH=1 AND DAY>=22) OR(MONTH=3 AND DAY<=2) ) 
GROUP BY city_name ORDER BY COUNT(*) DESC LIMIT 10;
