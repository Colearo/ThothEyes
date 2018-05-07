#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime
from thoth_eyes.sched import ThothEyes
from thoth_eyes.orm import ORM

start = time.time()
thoth_eyes = ThothEyes()
thoth_eyes.initialize()
thoth_eyes.refresh_today_news()
thoth_eyes.stop()

today = datetime.datetime.today()
today = today.strftime('%Y/%m/%d %H:%M')
print('[%s]' % today)

duration = time.time() - start
print('Runs %.2f s' % duration)

