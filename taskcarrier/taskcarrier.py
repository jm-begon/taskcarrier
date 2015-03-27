# -*- coding: utf-8 -*-
"""
A set of classes for handling parallelization through joblib
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__date__ = "26 Mar. 2015"



from abc import ABCMeta, abstractmethod
import copy_reg
import copy
import types
from functools import partial
try:
    from joblib import Parallel, delayed, cpu_count
except ImportError:
    from sklearn.externals.joblib import Parallel, delayed, cpu_count



def piclking_reduction(m):
    """Adds the capacity to pickle method of objects"""
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, piclking_reduction)



class BoundedIterable(object):

    def __init__(self, length, generator):
        self.length = length
        self.gen = generator

    def __len__(self):
        return self.length

    def __iter__(self):
        return self.gen

def bound_iterable(length):
    def wrap(iterable_factory):
        def build(*args, **kwargs):
            return BoundedIterable(length, iterable_factory(*args, **kwargs))
        return build
    return wrap



class Partition(object):
    """
    =========
    Partition
    =========
    A :class:`Partition` is a indexeable of slices. The slices are contiguous
    and homogenous in size.

    Constructor parameters
    ----------------------
    nb_parts : int (>0)
        The maximum number of slices. The actual number will be
        min(nb_parts, data_size)
    data_size : int > 0
        The size of the data to partition
    """

    def __init__(self, nb_parts, data_size):
        self._nb = min(nb_parts, data_size)
        self._mod = data_size % nb_parts
        self._inc = (data_size // nb_parts) + 1
        self._start_shift = 0

    def __len__(self):
        return self._nb

    def __getitem__(self, index):
        if hasattr(index, "stop") and hasattr(index, "start"):
            # Slice
            if hasattr(index, "step") and index.step is not None:
                # TODO do better
                return [x for x in self][index]
            start = index.start
            if start is None: start = 0
            clone = copy.copy(self)
            clone._nb = index.stop - start
            clone._start_shift = start
            return clone
        else:
            # Not slice --> simple index
            if index >= len(self):
                raise IndexError("Index out of range: "+str(index)+"/"+str(len(self)-1))
            actu_ind = index + self._start_shift
            sl_start = actu_ind * self._inc
            if actu_ind > self._mod:
                sl_start -= (actu_ind - self._mod)
            sl_end = sl_start +  self._inc
            if (actu_ind + 1) > self._mod:
                sl_end -= 1
            return slice(sl_start, sl_end)

    def apply_on(self, seq1, *seqs):
        """
        Apply the partition represented by this object on the given sequences

        Parameters
        ----------
        seq1 : a *sliceable* sequence
            The sequence to partition
        seqs : other such sequences of the same length as seq1

        Return
        ------
        slice_generator : a generator of sequences of tuples
            The generator yields 'len(self)' sequences. Each sequence
            correspond to a slice of the `Partition` instance. Each
            element of the sequence is a tuple of the input of the same index

        Example
        ------
        >>> p = Partition(5, 10)
        >>> l1 = range(10)
        >>> l2 = range(10, 20)
        >>> g = p.apply_on(l1, l2)
        >>> for el in g:
        ...     print el #doctest: +SKIP
        [(0, 10), (1, 11)]
        [(2, 12), (3, 13)]
        [(4, 14), (5, 15)]
        [(6, 16), (7, 17)]
        [(8, 18), (9, 19)]
        """
        zipped = zip(seq1, *seqs)
        return (zipped[s] for s in self)




class Mapper(object):
    """
    ======
    Mapper
    ======
    Like the map function, a :class:`Mapper` maps a function to one or more
    iterables.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def map(self, function, seq1, *seqs):
        """
        map(function, sequence[, sequence, ...]) -> sequence

        Return a list of the results of applying the function to the items of
        the argument sequence(s).  If more than one sequence is given, the
        function is called with an argument list consisting of the
        corresponding item of each sequence, substituting None for missing
        values when not all sequences have the same length.  If the function is
        None, return a list of the items of the sequence (or a list of tuples
        if more than one sequence).

        Note
        ----
        sequence is meant in a strict sense : indexeable, sliceable objects
        with a length.
        """
        pass

    def __call__(self, function, seq1, *seqs):
        """Delegate to :meth:`map` method"""
        return self.map(function, seq1, *seqs)

class SerialMapper(Mapper):
    """
    ============
    SerialMapper
    ============
    A :class:`SerialMapper` delegates to the built-in :func:`map` function.
    This class provide an homogenous interface in case of non-parallel
    mapping.
    """

    def map(self, function, seq1, *seqs):
        return [function(*tup) for tup in zip(seq1, *seqs)]


class StaticParallelMapper(Mapper):
    """
    ====================
    StaticParallelMapper
    ====================
    A :class:`StaticParallelMapper` compute the mapping in parallel (either
    by multiprocessing or multithreading) thanks to the :lib:`joblib` library.

    Load policy
    -----------
    The load will be splitted as equally as possible among the different workers
    beforehand so that there is no need of shipping data back and forth between
    processes.
    This may be suboptimal in term of processing time (as a worker can finish
    before others). However, dynamic balancing impose more overhead.
    Dynamic load balancing is more suited for threading backend.

    Constructor parameters
    ----------------------
    n_jobs : int (-1 or >0) (Default : -1)
        The number of core to use.
            If >0 : the number of workers
            If <0 : max(cpu_count() + 1 + n_jobs, 1)
    verbose : int [0, 50]
        The verbosity level. The more, the more verbose
    temp_folder : str, optional
        Folder to be used by the pool for memmaping large arrays
        for sharing memory with worker processes. If None, this will try in
        order:
        - a folder pointed by the JOBLIB_TEMP_FOLDER environment variable,
        - /dev/shm if the folder exists and is writable: this is a RAMdisk
          filesystem available by default on modern Linux distributions,
        - the default system temporary folder that can be overridden
          with TMP, TMPDIR or TEMP environment variables, typically /tmp
          under Unix operating systems.
        Only active when backend="multiprocessing".
    backend : str ("multiprocessing" or "threading") or None
    (default: None --> "multiprocessing")
        The backend to use

    Refer to joblib for more details
    """

    def __init__(self, n_jobs=-1, verbosity=0, temp_folder=None, backend=None):
        if n_jobs < 0:
            n_jobs = max(cpu_count() + 1 + n_jobs, 1)
        self.n_jobs = n_jobs
        self._parallelizer = Parallel(n_jobs=n_jobs, verbose=verbosity,
                                      temp_folder=temp_folder, backend=backend)

    def map(self, function, seq1, *seqs):
        gen = Partition(self.n_jobs, len(seq1)).apply_on(seq1, *seqs)
        # Since each worker will recieve a list of element to process
        # we need to map the function onto each element
        func = partial(map, partial(apply, function))
        # Note: a list having a length, it will be more efficient to
        # dispatch
        results = self._parallelizer([delayed(func)(l) for l in gen])
        # Flattening the results: (we get back a list (depth 0) of lists (depth
        # 1) where each list of depth 1 contains the results for each worker
        # subset. We need to make a whole iterable of depth 0 containing
        # all the results
        return [item for sublist in results for item in sublist]


class DynamicParallelMapper(Mapper):
    """
    =====================
    DynamicParallelMapper
    =====================
    A :class:`StaticParallelMapper` compute the mapping in parallel (either
    by multiprocessing or multithreading) thanks to the :lib:`joblib` library.

    Load policy
    -----------
    The load if dynamically balanced, that is when one worker is done with its
    piece of data, either a new one is shipped to him or it dies and a new
    worker is spawned.
    This produces much overhead in the case of multiprocessing but can still
    be faster than static load balancing if the completion time of the subtask
    has a high variability.

    Constructor parameters
    ----------
    n_jobs : int (-1 or >0) (Default : -1)
        The number of core to use.
            If >0 : the number of workers
            If -1 : the maximum number of CPU
    verbose : int [0, 50]
        The verbosity level. The more, the more verbose
    temp_folder : str, optional
        Folder to be used by the pool for memmaping large arrays
        for sharing memory with worker processes. If None, this will try in
        order:
        - a folder pointed by the JOBLIB_TEMP_FOLDER environment variable,
        - /dev/shm if the folder exists and is writable: this is a RAMdisk
          filesystem available by default on modern Linux distributions,
        - the default system temporary folder that can be overridden
          with TMP, TMPDIR or TEMP environment variables, typically /tmp
          under Unix operating systems.
        Only active when backend="multiprocessing".
    backend : str ("multiprocessing" or "threading") or None
    (default: None --> "multiprocessing")
        The backend to use

    Note
    ----
    ** Refer to joblib for more detaiseqs
    ** Beware that dynamically balancing load with multiprocessing might
    produce a lot of overhead if the computation time per datum is short
    and there are a lot of data
    """
    def __init__(self, n_jobs=-1, verbosity=0, temp_folder=None, backend=None):
        self._parallelizer = Parallel(n_jobs=n_jobs, verbose=verbosity,
                                      temp_folder=temp_folder, backend=backend)

    def map(self, function, seq1, *seqs):
        return self._parallelizer((delayed(function)(*i)
            for i in zip(seq1, *seqs)))


class MapperInstance(object):
    """
    ==============
    MapperInstance
    ==============
    A :class:`MapperInstance` is a singleton serving as context manager
    returning a predefined :class:`Mapper` instance. Its goal is twofold
    1. Defining only at the start the mapper to use in order to be able to
    access it everywhere without passing the arguments all over to keep the
    business code untouched
    2. To prevent nested parallel code to spauwn again new processes

    Intended usage
    --------------
    >>> def x_plus_y(x,y):
    ...     return x+y
    >>> with MapperInstance() as mapper:
    ...     mapper.map(x_plus_y, [1,2,3],[1,1,1])
    [2, 3, 4]
    """

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(MapperInstance, cls).__new__(cls, *args, **kwargs)
            cls._singleton._mapper = SerialMapper()
            cls._singleton._running = False
        return cls._singleton

    def register_mapper(self, mapper):
        self._mapper = mapper

    def retrieve_mapper(self):
        return self._mapper

    def __enter__(self):
        if self._running:
            return SerialMapper()
        else:
            self._running = True
            return self._mapper

    def __exit__(self, type, value, traceback):
        self._running = False
        # Let the exception propagate, if any
        return False






