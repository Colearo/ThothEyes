#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .sched import ThothEyes

class ORM :

    def __init__(self) :
        self.te = ThothEyes()
        self.redis = self.te.redis

    def orm_subtopics_by_pageandsize(self, date, page, size) :
        topsubtopics = [subtopic_id for subtopic_id, tuple in self.te.find_topsubtopics_by_date(date)]
        selected = topsubtopics[(page - 1) * size : page * size]
        subtopic_list = list()
        for subtopic_id in selected :
            subtopic = self.orm_subtopic_by_subtopicid(subtopic_id)
            if subtopic is None :
                continue
            subtopic_list.append(subtopic)
        return subtopic_list

    def orm_subtopicstotal_by_date(self, date) :
        topsubtopics = [subtopic_id for subtopic_id, tuple in self.te.find_topsubtopics_by_date(date)]
        return len(topsubtopics)

    def orm_subtopics_by_date(self, date) :
        topsubtopics = [subtopic_id for subtopic_id, tuple in self.te.find_topsubtopics_by_date(date)]
        subtopic_list = list()
        for subtopic_id in topsubtopics :
            subtopic = self.orm_subtopic_by_subtopicid(subtopic_id)
            if subtopic is None :
                continue
            subtopic_list.append(subtopic)
        return subtopic_list

        return len(topsubtopics)

    def orm_subtopic_by_subtopicid(self, subtopic_id) :
        subtopic_item = dict()

        subtopic_item['topic'] = self.te.find_title_by_subtopicid(subtopic_id)

        subtopic_item['keywords'] = [keyword for keyword, weight in self.te.find_keywords_by_subtopicid(subtopic_id)]

        news = self.te.find_news_by_subtopicid(subtopic_id)
        news_list = list()
        for news_item in news :
            item = dict()
            item['title'] = news_item['Title']
            item['content'] = news_item['Content']
            item['date'] = news_item['Date']
            item['link'] = news_item['Link']
            if news_item.get('Source') is not None :
                item['source'] = news_item['Source']
            if len(news_list) == 6 :
                break
            news_list.append(item)
        subtopic_item['news'] = news_list

        topic = self.te.find_timeline_by_subtopicid(subtopic_id)
        if topic is None :
            return None
        timelines = list()
        for subtopic in topic :
            timeline_item = dict()
            if subtopic == subtopic_id :
                news_item = news[0]
            else :
                news_item = self.te.find_news_by_subtopicid(subtopic)
                news_item = news_item[0]
            timeline_item['title'] = news_item['Title']
            timeline_item['date'] = news_item['Date'].split(' ')[0]
            paragraphs = news_item['Content'].split('\n')
            extra = ''
            for paragraph in paragraphs :
                if len(paragraph) > 50 :
                    extra = paragraph
                    break
            timeline_item['extraction'] = extra
            timelines.append(timeline_item)
        timelines.sort(key = lambda x:x['date'])
        timelines = timelines[-5:]
        subtopic_item['timelines'] = timelines

        hotspot_hi = dict()
        date, hotspot = self.te.find_hotspot_by_subtopicid(subtopic_id)
        hotspot_hi['index'] = round(hotspot, 2)
        news_hi = dict()
        labels, data = self.te.find_timelinehi_by_subtopicid(subtopic_id)
        news_hi['labels'] = labels
        news_hi['data'] = data
        hotspot_hi['news'] = news_hi
        words_hi = dict()
        labels, data = self.te.find_keywordshi_by_subtopicid(subtopic_id)
        words_hi['labels'] = labels
        words_hi['data'] = data
        hotspot_hi['words'] = words_hi
        subtopic_item['hotspot'] = hotspot_hi

        return subtopic_item

    def orm_topwords_by_date(self, date) :
        topword_list = self.te.find_topwords_by_date(date)
        word_value_list = list()
        word_news_dict = dict()
        for keyword, value, news_list in topword_list :
            word_value_list.append((keyword, value))
            word_news_dict[keyword] = news_list
        topword_dict = dict()
        topword_dict['list'] = word_value_list
        topword_dict['news'] = word_news_dict

        return topword_dict

    def orm_topsubtopics_by_date(self, date) :
        topsubtopics = list()
        for subtopic_id, (hotspot, title) in self.te.find_topsubtopics_by_date(date) :
            topsubtopic_dict = dict()
            topsubtopic_dict['title'] = title
            topsubtopic_dict['id'] = subtopic_id
            topsubtopic_dict['hotspot'] = hotspot
            topsubtopics.append(topsubtopic_dict)

        return topsubtopics

    def orm_timelines_by_days(self, days) :
        timelines = list()
        for topic in self.te.find_timeline_by_days(days) :
            print(topic)
            timeline_dict = dict()
            timeline_dict['topic'] = self.te.find_title_by_subtopicid(topic[0])
            timeline_dict['keywords'] = [keyword for keyword, weight in self.te.find_keywords_by_subtopicid(topic[0])]
            timeline_items = list()
            for subtopic in topic :
                timeline_item = dict()
                news_item = self.te.find_news_by_subtopicid(subtopic)
                news_item = news_item[0]
                timeline_item['title'] = news_item['Title']
                timeline_item['date'] = news_item['Date'].split(' ')[0]
                paragraphs = news_item['Content'].split('\n')
                extra = ''
                for paragraph in paragraphs :
                    if len(paragraph) > 50 :
                        extra = paragraph
                        break
                timeline_item['extraction'] = extra
                timeline_items.append(timeline_item)
            timeline_items.sort(key = lambda x:x['date'])
            timeline_items = timeline_items[-5:]
            timeline_dict['timelines'] = timeline_items
            timelines.append(timeline_dict)
        return timelines

    def orm_topicsearch_by_search(self, search_words) :
        subtopic_ids = self.te.find_subtopicids_by_search(search_words)
        subtopic_list = list()
        for subtopic_id in subtopic_ids :
            subtopic = self.orm_subtopic_by_subtopicid(subtopic_id)
            if subtopic is None :
                continue
            subtopic_list.append(subtopic)
            if len(subtopic_list) >= 12 :
                break
        return subtopic_list

