
"""
keyqueue
========

Provides the class KeyQueue, a (hopefully) threadsafe implementation of a
queue that supports random access to its elements.

See :class:`keyqueue.KeyQueue` for more details.
"""

import collections
import Queue
import contextlib
import threading

class KeyQueue(Queue.Queue):
    """
    Queue that allows access to its elements.

    Besides the methods documented below, this queue implements all
    the methods of the base class Queue.Queue.

    The `put` method now expects a tuple, where the first argument
    is a key that can be used to access the object later.

    :Example:

        >>> q = KeyQueue(maxsize=0)
        >>> q.put((1,'item-1')) # put 'item-1' in the queue, with key 1.
        >>> q.put((2,'item-2')) # put 'item-2' in the queue, with key 2.
        >>> q.get() # pop off top item.
        (1, 'item-1')
        >>> q.get() # pop off next item
        (2, 'item-2')

        Among new methods provided, the 'locked' context manager
        is noteworthy. This allows locking the queue such that a 
        set of operations can be performed on the queue without 
        risking interference from other threads. See 'locked'
        docstring for more information. 

        Further examples of the additionaly methods are provided
        in the docstrings below.
    """

    def __init__(self,maxsize=0):
        # Almost exact copy of Queue.__init__.
        # The only difference is that self.mutex is now
        # a re-entrant lock. This avoids deadlocks if the
        # user runs threadsafe operations in the 'locked'
        # context. 
        self.maxsize = maxsize
        self._init(maxsize)
        self.mutex = threading.RLock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0


    # The following are used to over-write default 
    # queue implementation to use an OrderedDict
    # as the data structure rather than a deque.

    def _init(self,maxsize):
        self.queue = collections.OrderedDict()

    def _put(self,item):
        self.queue[item[0]] = item[1]

    def _get(self):
        return self.queue.popitem(last=False)

    def _pop(self,key):
        return self.queue.pop(key)

    def _get_all_keys(self):
        return self.queue.keys()

    def _get_all_values(self):
        return self.queue.values()

    def _get_all_items(self):
        return self.queue.items()


    # Threadsafe methods
    
    def getitem(self,key):
        """
        Return the value of the item associated with `key`.

        :Example:
            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> with q.locked(): # lock the queue
            ...    print q.getitem(1)
            'item-1'
        """
        with self.locked():
            return self.queue[key]

    def setitem(self,key,value):
        """
        Set the value of the item associated with `key` to `value`.

        :Example:
            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> with q.locked(): # lock the queue ; guarantee thread safety.
            ...    q.setitem(1,"new-item")
            ...    print q.getitem(1)
            'new-item'
        """
        with self.locked():
            self.queue[key] = value

    def remove_item(self,key):
        """
        Threadsafe implementation that removes an item from the 
        queue.

        :Example:
            
            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> q.remove_item(1)
            >>> with q.locked():
            ...    print q.getitem(1)
            ...    
            KeyError
        """
        self.mutex.acquire()
        try:
            self._pop(key)
            self.not_full.notify()
        finally:
            self.mutex.release()

    def keys(self):
        with self.locked():
            return self._get_all_keys()

    def values(self):
        with self.locked():
            return self._get_all_values()

    def items(self):
        with self.locked():
            return self._get_all_items()

    @contextlib.contextmanager
    def locked(self):
        """
        Lock the queue to prevent other threads accessing it.

        :Example:

            Sometimes, a user may want to run a set of operations on the
            queue without losing control:

            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> with q.locked():
            ...    value = q.getitem(1)
            ...    q.setitem(1,value+"-suffix")

            In this case, were the queue not locked, another thread 
            may, conceivably, delete item 1 in between the `getitem` and
            the `setitem` calls.
        """
        self.mutex.acquire()
        yield
        self.mutex.release()



