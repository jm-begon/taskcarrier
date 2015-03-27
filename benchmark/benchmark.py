# -*- coding: utf-8 -*-
"""
A set of classes for handling parallelization through joblib
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__date__ = "26 Mar. 2015"


import time
import matplotlib.pyplot as plt

from taskcarrier import (SerialMapper, StaticParallelMapper,
                         DynamicParallelMapper)
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
    time.sleep(0.0001)
    return x+1

def heavy_task(x):
    time.sleep(0.01)
    return x+1



if __name__ == '__main__':
    # Fix #CPU, increasing size
    plotfile = "fix_cpu_increasing_size"
    max_cpu = cpu_count()
    assert max_cpu > 3, "Not enough CPU"
    cpu = 2
    nb_run = 10

    size_range = range(0, 3001, 50)
    timer = Timer()

    serial = SerialMapper()
    static = StaticParallelMapper(cpu)
    dynamic = DynamicParallelMapper(cpu)
    mappers = [static, dynamic, serial]
    # light_task
    serial_light = []
    static_light = []
    dynamic_light = []
    light_tasks_res = [static_light, dynamic_light, serial_light]
    # Heavy task
    serial_heavy = []
    static_heavy = []
    dynamic_heavy = []
    heavy_tasks_res = [static_heavy, dynamic_heavy, serial_heavy]

    lgt_exp = zip(mappers, light_tasks_res, [light_task]*3)
    hvy_exp = zip(mappers, heavy_tasks_res, [heavy_task]*3)[0:2]

    #experiences = lgt_exp
    #experiences = hvy_exp
    experiences = lgt_exp + hvy_exp

    for mapper, ls, task in experiences:
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


    plt.figure()
    plt.plot(size_range, serial_light, "r", label="Serial")
    plt.plot(size_range, static_light, "g", label="Static LB")
    plt.plot(size_range, dynamic_light, "b", label="Dynamic LB")
    plt.title("Performance of the Mapper for a light task ("+str(cpu)+" cores)")
    plt.xlabel("Data size")
    plt.ylabel("Completion time (sec)")
    plt.legend(loc="upper left")
    plt.savefig("inc_size_light_task"+str(cpu)+".pdf", bbox_inches='tight')


    plt.figure()
    plt.plot(size_range, static_heavy, "g", label="Static LB")
    plt.plot(size_range, dynamic_heavy, "b", label="Dynamic LB")
    plt.title("Performance of the Mapper for a heavy task ("+str(cpu)+" cores)")
    plt.xlabel("Data size")
    plt.ylabel("Completion time (sec)")
    plt.legend(loc="upper left")
    plt.savefig("inc_size_heavy_task"+str(cpu)+".pdf", bbox_inches='tight')









