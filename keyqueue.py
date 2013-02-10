
"""
keyqueue
========

Provides the class KeyQueue, a (hopefully) threadsafe implementation of a
queue that supports random access to its elements.
"""

import collections
import Queue
import contextlib

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

    # The following are used to over-write default 
    # queue implementation to use an OrderedDict
    # as the data structure rather than a deque.

    def _init(self,maxsize):
        self.queue = collections.OrderedDict()

    def _put(self,item):
        self.queue[item[0]] = item[1]

    def _get(self):
        return self.queue.popitem(last=False)

    def getitem(self,key):
        """
        Non-threadsafe access to a key.

        :Example:
            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> with q.locked(): # lock the queue
            ...    print q.getitem(1)
            'item-1'
        """
        return self.queue[key]

    def setitem(self,key,value):
        """
        Non-threadsafe alteration of an element.

        :Example:
            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> with q.locked(): # lock the queue ; guarantee thread safety.
            ...    q.setitem(1,"new-item")
            ...    print q.getitem(1)
            'new-item'
        """
        self.queue[key] = value

    def _pop(self,key):
        return self.queue.pop(key)

    @contextlib.contextmanager
    def locked(self):
        """
        Lock the queue to prevent other threads accessing it.

        :Example:
            >>> q = KeyQueue()
            >>> q.put((1,'item-1'))
            >>> with q.locked():
            ...     # modify q as much as you want without risking
            ...     # interference from other treads.
            ...     pass

        Note that, due to the current implementation, only operations
        which do not guarantee thread safety can be processed while a 
        queue is locked. Thus, the following will cause a deadlock:

            >>> with q.locked():
            ...    q.put(('2','item-2'))
            ...    # Deadlocks. q.put waits for q to be released.

        Non-threadsafe operations that can be used while a thread
        is locked include: `_put`, `_get`, `_pop`, `getitem`, 
        `setitem`.
        """
        self.mutex.acquire()
        yield
        self.mutex.release()

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



