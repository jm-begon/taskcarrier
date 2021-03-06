TaskCarrier
===========
TaskCarrier is a lightweight Python library built on top of [`joblib`](https://pythonhosted.org/joblib/) to ease some common use cases.

It is still in development. So far it provides:

1. Map-like utility in serial and parallel
    * `SerialMapper` is just a wrapper around list comprehension to provide an homogenous interface.
    * `DynamicParallelMapper` offers a map-like interface for `joblib`. Pieces of data are queued so as to provde *dynamic load balancing*
    * `StaticParallelMapper` offers a map-like interface. Data are still treated by `joblib` but each worker recieve all its data at the start (*static load balancing*)
2. Context manager to prevent parallel code to use nested parallel code.

# Note on load balancing

## Multiprocess context
In the case of multiprocessing, shipping data to worker processes usually brings a lot of overhead. The goal of the static load balancing is to reduce somewhat that overhead.

Here is a illustrating example in the case of a light task:

![Load balancing benchmark](inc_size_light_task.png)
>__Computation time performances of the Mappers for a ligth task with 4 multiprocessing workers with respect to the data size.__
>_Even though the task is light, one might want to take advantage of parallelization if there are lots of data. In this case, dynamic load balancing
will not even outperform the serial computation because the overhead is proprotionally too expensive. However, at 600-700 data, the initial overhead paid by static load balancing is counterbalanced by the parallelization, leaving it the most efficient method. Note that the difference between dynamic and static load balancing is roughly linear. With heavier task, the gap between both load policy is reduced but static load balancing will usually outperfoms dynamic with a linear trend nonetheless. See the benchmarks for more information_

**Rule of thumb for multiprocessing** :
* Homogenous computation time

The static load balancing should perform better. The performance difference should be most noticeable with light task and lots of data (this probably already helped stabilizing the average computation time).

* Heterogenous computation time

The dynamic load balancing may perform better in that situation provided there is "few" data or that the heteroginty is unevenly scattered throughout the data. Few data will encourage the latter and lessen the proportional shipping overhead cost.

**Rule of thumb for multithreading** :
Go for dynamic load balancing. Only for very homogenous computation time with light task and lots of data will difference be noticeable. Taking advantage of the nearly overhead-free dynamic load balancing will probably be more rewarding.

## Multithreaded context
In CPython, multithreading is not carried out in parallel because of the GIL. If you have some code releasing the GIL, using dynamic load balancing with a multithreading backend should be the optimal solution, though. Otherwise, stick to multiprocessing.

Getting the latest code
-----------------------

To get the latest code using git, simply type:


    git clone https://github.com/jm-begon/taskcarrier.git

If you don't have git installed, you can download a zip or tarball of the
latest code: https://github.com/jm-begon/taskcarrier/archive/master.zip



Installing
----------

As with any Python packages, simply do:

    python setup.py install

in the source code directory.


Running the test suite
----------------------

To run the test suite, you need nosetests and the coverage modules.
Run the test suite using:

    nosetests

from the root of the project.


How to contribute?
------------------

To contribute, fork the library, make your improvements and send back a pull request.
