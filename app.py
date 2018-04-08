#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import traceback
from thotheyes import ThothEyes

start = time.time()
thoth_eyes = ThothEyes()
thoth_eyes.initialize()
hotwords = thoth_eyes.get_news_hotwords()
for word, hit, news in hotwords :
    print('++==%s==++' % word)
    print('hit: ', hit)
    print('news: ', ''.join(title[0]['Title'] + ' ' for title in news))
# timeline = thoth_eyes.get_news_timeline()

# for cluster, topic in timeline :
    # news, attr = cluster
    # print(attr)
    # print('+++====Timeline====+++')
    # for item, attr in topic :
        # print(attr)
    # print('++++====== ')

duration = time.time() - start
print('Runs %.2f s' % duration)

