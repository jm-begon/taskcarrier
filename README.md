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
In the case of multiprocessing, shipping data to worker processes usually brings a lot of overhead. The goal of the static load balancing is to reduce somewhat that overhead. However, this policy is suboptimal in the case where the processing time of each worker greatly vary.

Here is a illustrating example in the case of a light task:

![Load balancing benchmark](inc_size_light_task.pdf)

** Rule of thumb ** :
* Light task, homogenous computation time: static load balancing
* Medium/heavy task, heterogenous computation time : dynamic load balancing

## Multithreaded context
In CPython, multithreading is not carried out in parallel because of the GIL. If you have some code releasing the GIL, using dynamic load balancing with a multithreading backend should be the optimal solution, though. Otherwise, stick to multiprocessing

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
