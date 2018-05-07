#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime
import mysql.connector

start = time.time()
select_newsid_by_date = (
        "SELECT news_id FROM news "
        "WHERE DATE(news_date) BETWEEN DATE(%s) AND DATE(%s)"
        )
DB_NAME = 'db_news'
cnx = mysql.connector.connect(user = 'root', password = 'lemon', database = DB_NAME)
cursor = cnx.cursor()
cursor.execute(select_newsid_by_date, ('2018-05-02', '2018-05-06')) 
for news_id in cursor :
    print(news_id)

today = datetime.datetime.today()
today = today.strftime('%Y/%m/%d %H:%M')
print('[%s]' % today)

duration = time.time() - start
print('Runs %.2f s' % duration)

