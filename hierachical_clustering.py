#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import json
import os
from datetime import datetime, timedelta
from huhu_seg.clustering import Cluster

start = time.time()

c = Cluster()
for i in range(100) :
    path = './cluster_%d.json' % i
    if not os.path.exists(path) :
        break
    temp = Cluster()
    temp.load_model(path)
    c.merge_model(temp)

l = c.hierachical_cluster(0.15, 'Content', 'Title', 0.5)

index = 0
for item in l :
    print('Cluster %d' % index)
    for i in item :
        print('[%s (%s)]' % (i[-1]['Title'], i[0]['Date']), end = '==>\n')
    index += 1

duration = time.time() - start
print('Runs %.2f s' % duration)

