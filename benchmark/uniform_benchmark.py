# -*- coding: utf-8 -*-
"""
A set of classes for handling parallelization through joblib
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__date__ = "26 Mar. 2015"


import time
import random
import matplotlib.pyplot as plt

from taskcarrier import StaticParallelMapper, DynamicParallelMapper
try:
    from joblib import cpu_count
except ImportError:
    from sklearn.externals.joblib import cpu_count

class Timer(object):
    def __init__(self):
        self.t = time.time()
    def start(self):
        self.t = time.time()
    def stop(self):
        return time.time() - self.t

def light_task(x):
    sleep_sec = random.uniform(0, 0.001)
    time.sleep(sleep_sec)
    return x+1





if __name__ == '__main__':
    cpu = 4
    max_cpu = cpu_count()
    assert max_cpu >= cpu, "Not enough CPU"

    nb_run = 1  # Several runs would blur the results

    size_range = range(0, 3001, 50)
    timer = Timer()

    static = StaticParallelMapper(cpu)
    dynamic = DynamicParallelMapper(cpu)
    mappers = [static, dynamic]
    # light_task
    static_light = []
    dynamic_light = []
    light_tasks_res = [static_light, dynamic_light]


    lgt_exp = zip(mappers, light_tasks_res, [light_task]*3)


    for mapper, ls, task in lgt_exp:
        print "New experience ", mapper, task
        for size in size_range:
            data = range(size)
            t = 0
            for i in xrange(nb_run):
                timer.start()
                mapper(task, data)
                t += timer.stop()
            print "Size ", str(size), "time", str(t/nb_run)
            ls.append(t/nb_run)

        print

    try:
        plt.figure()
        plt.plot(size_range, static_light, "g", label="Static LB")
        plt.plot(size_range, dynamic_light, "b", label="Dynamic LB")
        plt.title("Mapper performances with random uniform computation time ("+str(cpu)+" cores)")
        plt.xlabel("Data size")
        plt.ylabel("Completion time (sec)")
        plt.legend(loc="upper left")
        plt.savefig("inc_size_light_task"+str(cpu)+".pdf", bbox_inches='tight')
        plt.savefig("inc_size_light_task"+str(cpu)+".png", bbox_inches='tight')


    finally:
        print size_range
        print static_light
        print dynamic_light










