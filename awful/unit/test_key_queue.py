
import unittest
import os
import sys

sys.path.insert(0,os.path.abspath("../.."))

import awful.keyqueue as keyqueue

class TestKeyQueue(unittest.TestCase):
    """
    Test suite for the KeyQueue object.

    Currently this only tests whether the data structure works more or
    less as intended.
    It really doesn't test for thread safety. 
    """

    def setUp(self):
        self.queue = keyqueue.KeyQueue()
        self.item1 = ( 1, "item-1" )
        self.item2 = ( 2, "item-2" )
        self.item3 = ( 3, "item-3" )

    def test_put(self):
        self.queue.put(self.item1)
        self.queue.put(self.item2)
        self.queue.put(self.item3)
        assert self.queue.queue.keys() == [1,2,3]
        assert self.queue.queue.values() == \
                ["item-1", "item-2", "item-3"]

    def test_get(self):
        self.queue.put(self.item1)
        self.queue.put(self.item2)
        self.queue.put(self.item3)
        assert self.queue.get() == (1,"item-1")
        assert self.queue.get() == (2,"item-2")
        assert self.queue.get() == (3,"item-3")

    def test_remove_item(self):
        self.queue.put(self.item1)
        self.queue.put(self.item2)
        self.queue.put(self.item3)
        self.queue.remove_item(2)
        assert self.queue.get() == (1,"item-1")
        assert self.queue.get() == (3,"item-3")

    def test_setitem(self):
        self.queue.put(self.item1)
        self.queue.put(self.item2)
        self.queue.put(self.item3)
        self.queue.setitem(2,"new-item")
        assert self.queue.get() == (1,"item-1")
        assert self.queue.get() == (2,"new-item")
        assert self.queue.get() == (3,"item-3")

    def test_locked(self):
        self.queue.put(self.item1)
        self.queue.put(self.item2)
        self.queue.put(self.item3)
        with self.queue.locked():
            assert self.queue.get() == (1,"item-1")
            assert self.queue.getitem(2) == "item-2"

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKeyQueue)
    unittest.TextTestRunner(verbosity=2).run(suite)

