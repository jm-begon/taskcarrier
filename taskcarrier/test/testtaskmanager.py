# -*- coding: utf-8 -*-
"""
tests of the :mod:`taskcarrier` module
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "26 Mar. 2015"

from nose.tools import assert_equal

from taskcarrier import *


def test_cpt_partition_balanced():
    nb_workers = 5
    data_size = 330
    slices = [slice(0, 66), slice(66, 132), slice(132, 198),
              slice(198, 264), slice(264, 330)]
    partition = Partition(nb_workers, data_size)
    assert_equal(nb_workers, len(partition))
    for i, sl in enumerate(partition):
        assert_equal(sl, slices[i])

def test_cpt_partition_unbalanced():
    nb_workers = 5
    data_size = 333
    slices = [slice(0, 67), slice(67, 134), slice(134, 201),
              slice(201, 267), slice(267, 333)]
    partition = Partition(nb_workers, data_size)
    assert_equal(nb_workers, len(partition))
    for i, sl in enumerate(partition):
        assert_equal(sl, slices[i])

def test_cpt_partition_less_data():
    nb_workers = 100
    data_size = 5
    slices = [slice(0, 1), slice(1, 2), slice(2, 3),
              slice(3, 4), slice(4, 5)]
    partition = Partition(nb_workers, data_size)
    assert_equal(data_size, len(partition))
    for i, sl in enumerate(partition):
        assert_equal(sl, slices[i])

def x_plus_y(x, y):
    return x+y


def test_serial_mapper():
    xs = range(1000)
    ys = range(1000, 2000)
    assert_equal(len(xs), len(ys))
    expected = [x+y for x,y in zip(xs, ys)]
    mapper = SerialMapper()
    res = mapper(x_plus_y, xs, ys)
    assert_equal(res, expected)

def test_dynamic_para_mapper():
    xs = range(1000)
    ys = range(1000, 2000)
    assert_equal(len(xs), len(ys))
    expected = [x+y for x,y in zip(xs, ys)]
    mapper = DynamicParallelMapper()
    res = mapper(x_plus_y, xs, ys)
    assert_equal(res, expected)


def test_static_para_mapper():
    xs = range(10)
    ys = [1]*len(xs)
    assert_equal(len(xs), len(ys))
    expected = [x+y for x,y in zip(xs, ys)]
    mapper = StaticParallelMapper()
    res = mapper(x_plus_y, xs, ys)
    assert_equal(res, expected)



def test_zerolength():
    SerialMapper()(abs, [])
    StaticParallelMapper()(abs, [])
    DynamicParallelMapper()(abs, [])



