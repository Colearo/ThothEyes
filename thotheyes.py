#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import traceback
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from huhu_seg.clustering import Cluster, Timeline
from huhu_seg.hotspot import HotSpot
from huhu_seg.topic import Topic
from huhu_seg.textrank import TextRank
from huhu_seg.tfidf import TFIDF

def task_cluster(data, index) :
    topics = list()
    try :
        c = Cluster()
        c.load_corpura(data, 'Content')
        clusters = c.centroid_cluster_bow(3)
        h = HotSpot(clusters, 'Content')
        hot_news = h.computing_clusters()
        for cluster, hotspot in hot_news :
            min_title_len = 1000
            content = ''.join(corpus['Content'] for corpus in h.flat(cluster))
            for i in range(len(cluster)) :
                for j in range(len(cluster[i])) :
                    if len(cluster[i][j]['Title']) < min_title_len :
                        title = cluster[i][j]['Title']
                        min_title_len = len(title)
            t = Topic()
            topic, keywords = t.gen_topic(content, title)
            topics.append((cluster,(topic, hotspot, keywords)))
            print('Topic: ', topic)
            print('Keywords: [%s]' % (''.join(k[0] + ' ' for k in keywords)))
            print('HotSpot: ', hotspot)
        c.clusters = topics
        return c
    except Exception as exc:
        print('[%d] generated an exception: %s' % (index, exc))
        traceback.print_exc()
        return None
 
class ThothEyes :

    def __init__(self) :
        self.redis = redis.Redis(host = 'localhost', port = 6379, decode_responses = True)
        self.today_news = None
        self.timeline = None

    def get_latest_news(self, days_window) :
        today = datetime.today()
        dates_from = today - timedelta(days = days_window)
        data = list()
        for i in self.redis.sscan_iter('news_content') :
            d = eval(i)
            content = d.get('Content')
            if content is None or content.strip() == '':
                continue
            date = d.get('Date')
            if date is None or datetime.strptime(date, '%Y/%m/%d %H:%M') < dates_from :
                continue
            data.append(d)
        data.sort(key= lambda d:d['Date'])
        return data, dates_from

    def chunk_news(self, data, dates_start, days_window) :
        index = 0
        chunks = list()
        for item in data :
            if len(chunks) == 0 :
                chunks.append([item,])
                continue
            cur_date = datetime.strptime(item['Date'], '%Y/%m/%d %H:%M')
            delta = cur_date - dates_start
            if (delta.days/days_window > 1) :
                index += 1
                chunks.append([item,])
                dates_start += timedelta(days = days_window)
            else :
                chunks[index].append(item)

        return chunks

    def initialize(self) :
        data, dates_from = self.get_latest_news(21)
        chunks = self.chunk_news(data, dates_from, 1)
        print('[Notice] News data initialized')
        clusters_inst = list()
        with ProcessPoolExecutor(max_workers = 4) as executor :
            for cluster_inst in executor.map(task_cluster, (chunk for chunk in chunks), (i for i in range(len(chunks)))) :
                if cluster_inst is not None :
                    clusters_inst.append(cluster_inst)
        print('[Notice] News data were clustered')
        self.today_news = clusters_inst[-1]
        self.timeline = Timeline(clusters_inst)
        self.timeline.timeline_topics()
        print('[Notice] News data were timelined')

    def hotspot_now(self) :
        if self.today_news is None :
            data, dates_from = self.get_latest_news(2)
            self.today_news = task_cluster(data, 0)

    def get_news_timeline(self) :
        self.hotspot_now()
        timeline = list()
        for topic in self.timeline.topics :
            for cluster in self.today_news.clusters :
                if cluster in topic:
                    timeline.append((cluster, topic))
        return timeline

    def get_news_hotwords(self) :
        top_words = dict()
        word2news = dict()
        self.hotspot_now()
        for cluster, (topic, hotspot, keywords) in self.today_news.clusters :
            for c in cluster :
                content = ''.join([item['Content'] + '\n' for item in c])
                for keyword, weight in TextRank(content, hmm_config = True).extract_kw(3, False) :
                    try :
                        top_words[keyword] += (1 / hotspot) * weight
                        word2news[keyword].append(c)
                    except :
                        top_words[keyword] = (1 / hotspot) * weight
                        word2news[keyword] = list()
                        word2news[keyword].append(c)
        top_words = sorted(iter(top_words.items()), key = lambda d:d[1], reverse = True)
        word_list = list()
        for word, hits in top_words :
            word_list.append((word, hits, word2news[word]))

        return word_list


