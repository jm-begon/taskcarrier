# -*- coding: utf-8 -*-
"""
===========
TaskCarrier
===========
:mod:`taskcarrier` contains a set of tools built on top of the `joblib`
library which allow to use transparently Parallel/Serial code using
simple but nice abstraction.
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "26 Mar. 2015"


from .taskcarrier import (BoundedIterable, bound_iterable, Partition, Mapper,
                          SerialMapper, StaticParallelMapper,
                          DynamicParallelMapper, MapperInstance)


__all__ = ["BoundedIterable", "bound_iterable", "Partition", "Mapper",
           "SerialMapper", "StaticParallelMapper", "DynamicParallelMapper",
           "MapperInstance"]


