#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import traceback
from sched import ThothEyes

start = time.time()
thoth_eyes = ThothEyes()
thoth_eyes.initialize()
thoth_eyes.refresh_today_news()

duration = time.time() - start
print('Runs %.2f s' % duration)

