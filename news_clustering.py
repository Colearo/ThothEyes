#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import time
import re
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from huhu_seg.clustering import Cluster

r = redis.Redis(host = 'localhost', port = 6379, decode_responses = True)

dates_from = datetime.strptime('2018/02/01 00:00', '%Y/%m/%d %H:%M')

def date_chunking(data, days_window = 14) :
    dates_start = dates_from
    index = 0
    chunks = []
    for d in data :
        if len(chunks) == 0 :
            chunks.append([d,])
            continue

        cur_date = datetime.strptime(d['Date'], '%Y/%m/%d %H:%M')

        if (dates_start < cur_date and
        dates_start + timedelta(days = days_window) > cur_date) :
            chunks[index].append(d)
        else :
            index += 1
            dates_start += timedelta(days = days_window)
            chunks.append([d,])

    return chunks


def clustering(data, index) :
    c = Cluster()
    c.load_corpura(data, 'Content', 'BOW', 0.8)
    c.centroid_cluster(3, False)
    c.save_model('./cluster_%d.json' % index)
    print('[%d]Generated %d clusters' % (index, len(c.model['clusters'])))

    
start = time.time()
data = []
for i in r.sscan_iter('news_content') :
    d = eval(i)
    content = d.get('Content')
    if content is None or content.strip() == '':
        continue
    date = d.get('Date')
    if date is None or datetime.strptime(date, '%Y/%m/%d %H:%M') < dates_from :
        continue
    data.append(d)
    print('[%s] %s' % (d['Title'], date))

data.sort(key= lambda d:d['Date'])
data = date_chunking(data, 3)
for d in data :
    print(len(d), end = '|')
print(' ')

with ProcessPoolExecutor(max_workers = 4) as executor :
    futures = executor.map(clustering, (d for d in data), (i for i in range(len(data))))

duration = time.time() - start
print('Runs %.2f s' % duration)

