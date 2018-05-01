#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import traceback
from datetime import datetime, timedelta, date
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from huhu_seg.clustering import Cluster, Timeline
from huhu_seg.hotspot import HotSpot
from huhu_seg.topic import Topic
from huhu_seg.textrank import TextRank

def window_cluster(chunk_data) :
    subtopics = list()
    try :
        c = Cluster()
        c.load_corpura(chunk_data[1], 'Content')
        clusters = c.centroid_cluster_bow(3)
        h = HotSpot(clusters, 'Content')
        hot_news = h.computing_clusters()
        for cluster, hotspot in hot_news :
            corpura = h.flat(cluster)
            corpura.sort(key= lambda d:d['Date'])
            content = ''.join(corpus['Content'] for corpus in corpura)
            title = corpura[0]['Title']
            t = Topic()
            subtopic, keywords = t.gen_topic(content, title)
            subtopics.append((corpura,(subtopic, hotspot, keywords)))

        return (chunk_data[0], subtopics)
    except Exception as exc:
        print('[%s] generated an exception: %s' % (chunk_data[0], exc))
        traceback.print_exc()
        return None

class ThothEyes :

    def __init__(self) :
        self.redis = redis.Redis(host = 'localhost', port = 6379, decode_responses = True, password="lemonHUHUHE")
        self.hotspot_inst = HotSpot()
        self.subtopiced_news = list()

    def initialize(self) :
        old_news, date_from = self.init_old_news(30)
        print("[NOTICE] Old News Initialized")
        chunked_old_news = self.chunk_news(old_news, date_from, 1)
        print("[NOTICE] Old News Chunked")
        subtopiced_old_news = self.init_news_subtopics(chunked_old_news)
        print("[NOTICE] Old News Generated Subtopics")
        self.subtopiced_news = subtopiced_old_news
        self.chunked_news = chunked_old_news

    def refresh_today_news(self) :
        today_news, today = self.init_today_news()
        today = today.strftime('%Y/%m/%d')
        subtopiced_today_news = self.refresh_today_subtopics((today, today_news))
        self.init_news_timelines(self.subtopiced_news + subtopiced_today_news)

    def refresh_today_subtopics(self, today_news) :
        subtopiced_today_news = list()
        subtopics_keywords = list()
        today, today_subtopics = window_cluster(today_news)
        for subtopic, (title, hotspot, keywords) in today_subtopics :
            print('=========')
            print('Subtopic: ', title)
            print('Keywords: [%s]' % (''.join(k[0] + ' ' for k in keywords)))
            print('HotSpot: ', hotspot)

            subtopic_id = None
            unrecord_news = list()
            for news_item in subtopic :
                sscan = [item for item in self.redis.sscan_iter("newsid_subtopicid_index", str(news_item['Id']) + '_*')]
                if len(sscan) == 0 :
                    unrecord_news.append(news_item)
                elif len(sscan) > 0 and subtopic_id is None :
                    subtopic_id = int(sscan[0].split('_')[1])

            if subtopic_id is None :
                subtopic_id = self.redis.incr("subtopic_id_count", amount = 1)
            subtopic_attr_dict = dict()
            subtopic_attr_dict['Title'] = title
            subtopic_attr_dict['Hotspot'] = hotspot
            subtopic_attr_dict['Keywords'] = keywords
            subtopic_attr_dict['Date'] = subtopic[0]['Date']
            self.redis.hset("subtopics_attr", subtopic_id, subtopic_attr_dict)
            for news_item in unrecord_news :
                self.redis.sadd("newsid_subtopicid_index", str(news_item['Id']) + '_' + str(subtopic_id))
            subtopiced_today_news.append((subtopic_id, subtopic))
            subtopics_keywords.append((subtopic_id, keywords))
        self.get_keywords_hi(today, subtopics_keywords, dict((self.chunked_news + [today_news, ])))
        return subtopiced_today_news

    def chunk_news(self, data, date_start, days_window) :
        index = 0
        chunks = list()
        for item in data :
            if len(chunks) == 0 :
                chunks.append((date_start.strftime('%Y/%m/%d'), 
                    [item,]))
                continue
            cur_date = datetime.strptime(item['Date'], 
                    '%Y/%m/%d %H:%M')
            delta = cur_date - date_start
            if (delta/timedelta(days = days_window) > 1) :
                index += 1
                date_start += timedelta(days = days_window)
                chunks.append((date_start.strftime('%Y/%m/%d'), 
                    [item,]))
            else :
                chunks[index][1].append(item)
        return chunks

    def get_news(self, date_from, date_to) :
        data = list()
        for item in self.redis.hscan_iter('news') :
            d = eval(item[1])
            content = d.get('Content')
            if content is None or content.strip() == '':
                continue
            date = d.get('Date')
            if (date is None or 
        datetime.strptime(date, '%Y/%m/%d %H:%M') < date_from or
        datetime.strptime(date, '%Y/%m/%d %H:%M') >= date_to) :
                continue
            d['Id'] = item[0];
            print("News: ", d['Title'])
            data.append(d)
        data.sort(key= lambda d:d['Date'])
        return data

    def init_old_news(self, days_window) :
        today = date.today()
        today = datetime(today.year, today.month, today.day)
        date_from = today - timedelta(days = days_window)
        data = self.get_news(date_from, today)
        return data, date_from

    def init_today_news(self) :
        today = date.today()
        today = datetime(today.year, today.month, today.day)
        now = datetime.today()
        data = self.get_news(today, now)
        return data, today

    def init_news_timelines(self, subtopiced_news) :
        timeline = Timeline(subtopiced_news, 'Content')
        timeline.timeline_topics()
        self.redis.delete("subtopicid_topicid_index", "topic_id_count", "timeline_days")
        for topic in timeline.topics :
            topic_id = self.redis.incr("topic_id_count")
            subtopic_titles = list()
            for subtopic_id, subtopic in topic :
                self.redis.sadd("subtopicid_topicid_index", str(subtopic_id) + '_' + str(topic_id))
                subtopic_attr = eval(self.redis.hget("subtopics_attr", subtopic_id))
                subtopic_titles.append(subtopic_attr['Title'])
            print(subtopic_titles)
        for days in [7, 14, 30] :
            topics = self.find_timeline_by_days(days)
            self.redis.hset("timeline_days", days, topics)

    def init_news_subtopics(self, chunked_old_news) :
        clustered_old_news = list()
        unclustered_chunks = list()
        subtopiced_old_news = list()
        for date, chunk in chunked_old_news :
            if self.redis.sismember("clustered_news_date", date) is not True :
                unclustered_chunks.append((date, chunk))
            else :
                subtopiced_old_news.extend(self.find_subtopics_by_date(date))

        with ProcessPoolExecutor(max_workers = 4) as executor :
            for subtopics in executor.map(window_cluster, 
                ((date, chunk) for date, chunk in 
                unclustered_chunks)) :
                if subtopics is None or len(subtopics[0]) == 0 :
                    continue
                clustered_old_news.append(subtopics)

        for date, subs in clustered_old_news :
            self.redis.sadd("clustered_news_date", date)
            subtopics_keywords = list()
            for sub,(title, hotspot, keywords) in subs:
                print('=========')
                print('Subtopic: ', title)
                print('Keywords: [%s]' % (''.join(k[0] + ' ' for k in keywords)))
                print('HotSpot: ', hotspot)
                subtopic_id = None
                unrecord_news = list()
                for news_item in sub :
                    sscan = [item for item in self.redis.sscan_iter("newsid_subtopicid_index", str(news_item['Id']) + '_*')]
                    if len(sscan) == 0 :
                        unrecord_news.append(news_item)
                    elif len(sscan) > 0 and subtopic_id is None :
                        subtopic_id = int(sscan[0].split('_')[1])
                if subtopic_id is None :
                    subtopic_id = self.redis.incr("subtopic_id_count", amount = 1)
                subtopic_attr_dict = dict()
                subtopic_attr_dict['Title'] = title
                subtopic_attr_dict['Hotspot'] = hotspot
                subtopic_attr_dict['Keywords'] = keywords
                subtopic_attr_dict['Date'] = sub[0]['Date']
                self.redis.hset("subtopics_attr", subtopic_id, subtopic_attr_dict)
                subtopiced_old_news.append((subtopic_id, sub))
                for news_item in unrecord_news :
                    self.redis.sadd("newsid_subtopicid_index", str(news_item['Id']) + '_' + str(subtopic_id))
                subtopics_keywords.append((subtopic_id, keywords))

            self.get_keywords_hi(date, subtopics_keywords, dict(chunked_old_news))

        return subtopiced_old_news

    def get_keywords_hi(self, date, subtopics_keywords, chunked_news_dict) :
        cur_date = datetime.strptime(date, '%Y/%m/%d')
        start_date = cur_date - timedelta(days = 6)

        if chunked_news_dict.get(start_date.strftime('%Y/%m/%d')) is None:
            return None
        days_corpura = list()
        for i in range(7) :
            d = start_date + timedelta(days = i)
            d = d.strftime('%Y/%m/%d')
            days_corpura.append((d, chunked_news_dict[d]))

        for subtopic_id, keywords_set in subtopics_keywords :
            keywords_hi = self.hotspot_inst.computing_keywords(keywords_set, days_corpura)
            print('******')
            print('TopicID: ', subtopic_id)
            for keyword, hi in iter(keywords_hi.items()) : 
                hi_dict2list = list(hi.items())
                hi_dict2list.sort(key=lambda d:d[0])
                print(keyword, [item[1] for item in hi_dict2list])
                hi_labels = [item[0] for item in hi_dict2list]
                hi_data = [item[1] for item in hi_dict2list]
                self.redis.hset("subtopicid_keyword_index", str(subtopic_id) + '_' + keyword, (hi_labels, hi_data))

    def find_subtopics_by_date(self, date) :
        subtopics = list()
        date = datetime.strptime(date, '%Y/%m/%d')
        end_date = date + timedelta(days = 1)
        for key, value in self.redis.hscan_iter("subtopics_attr"):
            subtopic_id = int(key)
            subtopic_attr = eval(value)
            cur_date = datetime.strptime(subtopic_attr['Date'], '%Y/%m/%d %H:%M')
            if cur_date >= date and cur_date < end_date :
                subtopics.append((subtopic_id, self.find_news_by_subtopicid(subtopic_id)))

        return subtopics

    def find_subtopicids_by_date(self, date) :
        subtopic_ids = list()
        date = datetime.strptime(date, '%Y/%m/%d')
        end_date = date + timedelta(days = 1)
        for key, value in self.redis.hscan_iter("subtopics_attr"):
            subtopic_id = int(key)
            subtopic_attr = eval(value)
            cur_date = datetime.strptime(subtopic_attr['Date'], '%Y/%m/%d %H:%M')
            if cur_date >= date and cur_date < end_date :
                subtopic_ids.append(subtopic_id)
        return subtopic_ids

    def del_subtopics_by_date(self, date) :
        subtopic_ids = self.find_subtopicids_by_date(date)
        for subtopic_id in subtopic_ids :
            self.redis.hdel("subtopics_attr", subtopic_id)
            index_list = [item for item in self.redis.sscan_iter("newsid_subtopicid_index", match = '*_' + str(subtopic_id))]
            for index in index_list :
                self.redis.srem("newsid_subtopicid_index", index)
        self.redis.srem("clustered_news_date", date)

    def find_news_by_subtopicid(self, subtopic_id) :
        news = list()
        for item in self.redis.sscan_iter("newsid_subtopicid_index", match = '*_' + str(subtopic_id)) :
            news_id = int(item.split(sep = '_')[0])
            news_item = self.redis.hget("news", news_id)
            news_item = eval(news_item)
            news_item['Id'] = news_id
            news.append(news_item)
        return news

    def find_topsubtopics_by_date(self, date) :
        topsubtopic_dict = dict()
        subtopic_ids = self.find_subtopicids_by_date(date)
        for subtopic_id in subtopic_ids :
            date, hotspot = self.find_hotspot_by_subtopicid(subtopic_id)
            title = self.find_title_by_subtopicid(subtopic_id)
            topsubtopic_dict[subtopic_id] = (hotspot, title)
        topsubtopic_list = sorted(iter(topsubtopic_dict.items()), key = lambda d:d[1][0], reverse = True)
        return topsubtopic_list

    def find_topwords_by_date(self, date) :
        topword_dict = dict()
        word_news_map = dict()
        subtopic_ids = self.find_subtopicids_by_date(date)
        for subtopic_id in subtopic_ids :
            keywords_hi_tuple = self.find_keywordshi_by_subtopicid(subtopic_id)
            subtopic_title = self.find_title_by_subtopicid(subtopic_id)
            for keyword, values in dict(keywords_hi_tuple[1]).items() :
                try :
                    topword_dict[keyword] += values[-1]
                    word_news_map[keyword].append(subtopic_title)
                except :
                    topword_dict[keyword] = values[-1]
                    word_news_map[keyword] = [subtopic_title,]
        topword_list = sorted(iter(topword_dict.items()), key = lambda d:d[1], reverse = True)
        topwords = list()
        for keyword, value in topword_list :
            topwords.append((keyword, value, word_news_map[keyword]))
        return topwords

    def find_timeline_by_date(self, date) :
        topics = list()
        subtopics = self.find_subtopics_by_date(date)
        for subtopic_id, subtopic_news in subtopics :
            topic_set = self.find_timeline_by_subtopicid(subtopic_id)
            if topic_set is not None and topic_set not in topics:
                topics.append(topic_set)
        return topics

    def find_timeline_by_subtopicid(self, subtopic_id) :
        sscan = [item for item in self.redis.sscan_iter("subtopicid_topicid_index", str(subtopic_id) + '_*')]
        if len(sscan) != 0 :
            topic_id = sscan[0].split('_')[1]
        else :
            return None
        topic_set = [int(item.split('_')[0]) for item in self.redis.sscan_iter("subtopicid_topicid_index", '*_' + topic_id)]
        topic_set.sort()
        return topic_set

    def find_timeline_by_days(self, days) :
        if self.redis.hexists("timeline_days", days) is False :
            topics = list()
            today = datetime.today()
            today = datetime(today.year, today.month, today.day)
            for day in range(days) :
                date = today - timedelta(days = day)
                date = date.strftime('%Y/%m/%d')
                date_topics = self.find_timeline_by_date(date)
                for topic in date_topics :
                    if topic not in topics and len(topic) > 1:
                        topics.append(topic)
        else :
            topics = eval(self.redis.hget("timeline_days", days))
            
        return topics

    def find_keywordshi_by_subtopicid(self, subtopic_id) :
        keywords_dict = dict()
        labels = list()
        for subtopicid_keyword, value in self.redis.hscan_iter("subtopicid_keyword_index", str(subtopic_id) + '_*') :
            value = eval(value)
            keyword = subtopicid_keyword.split('_')[1]
            labels = value[0]
            keywords_dict[keyword] = value[1]
        dates = list()
        for label in labels :
            cur_date = datetime.strptime(label, '%Y/%m/%d')
            dates.append(cur_date.strftime('%m/%d'))
        keywords_hi_tuple = (dates, list(keywords_dict.items()))
        return keywords_hi_tuple

    def find_hotspot_by_subtopicid(self, subtopic_id) :
        subtopic_attr = eval(self.redis.hget("subtopics_attr", subtopic_id))
        hotspot = subtopic_attr['Hotspot']
        date = subtopic_attr['Date']
        return date, hotspot

    def find_title_by_subtopicid(self, subtopic_id) :
        subtopic_attr = eval(self.redis.hget("subtopics_attr", subtopic_id))
        title = subtopic_attr['Title']
        return title

    def find_keywords_by_subtopicid(self, subtopic_id) :
        subtopic_attr = eval(self.redis.hget("subtopics_attr", subtopic_id))
        keywords = subtopic_attr['Keywords']
        return keywords

    def find_timelinehi_by_subtopicid(self, subtopic_id) :
        topic = self.find_timeline_by_subtopicid(subtopic_id)
        subtopic_date = None
        hotspot_dict = dict()
        for item_subtopic_id in topic :
            cur_date, hotspot = self.find_hotspot_by_subtopicid(item_subtopic_id)
            cur_date = datetime.strptime(cur_date, '%Y/%m/%d %H:%M')
            cur_date = cur_date.strftime('%Y/%m/%d')
            if item_subtopic_id == subtopic_id :
                subtopic_date = cur_date
            hotspot_dict[cur_date] = hotspot

        subtopic_date = datetime.strptime(subtopic_date, '%Y/%m/%d')
        timeline_hi = list()
        for day in range(14) :
            cur_date = subtopic_date - timedelta(days = day) 
            day = cur_date.strftime('%Y/%m/%d')
            hotspot = hotspot_dict.get(day)
            if hotspot is None :
                hotspot = 0
            timeline_hi.append((cur_date.strftime('%m/%d'), hotspot))
        timeline_hi.reverse()
        timeline_hi_tuple = tuple(zip(*timeline_hi))
        return timeline_hi_tuple


