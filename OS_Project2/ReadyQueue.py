"""
Title:          ReadyQueue.py
Author:         Michael Garod
Date Created:   4/10/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #2
Description:    Add ReadyQueue class to simulate history based preemption.
                ReadyQueue inherits from collections.deque.
Note:           Really, the only difference here is that the ReadyQueue sorts
                itself by working_tau before popleft (return an object).
                Working_tau is the current estimated burst less the current
                burst. There is a secondary sort by PID in the event of a tie
                on working_tau.
"""
import collections as col


class ReadyQueue(col.deque):
    def __init__(self):
        super(ReadyQueue, self).__init__()

    def sort(self):
        """
        Order PCBs contained in the ReadyQueue by the estimated burst minus
        the current burst (working_tau) and secondarily sorted by PID.

        This secondary sort is necessary because sort is unstable with respect
        to PID, even though documentation claims to be stable. Or maybe I don't
        understand how the sorting is occuring.

        A deque cannot sort itself. It must empty itself into a list, then
        sort the list, and reinsert that list into the deque.
        :return:
        """
        items = [self.pop() for x in range(len(self))]
        items = sorted(items, key=lambda p: p.id)
        items = sorted(items, key=lambda p: p.working_tau)
        self.extend(items)

    # @Override the method append() from the parent collections.deque
    def append(self, item):
        super(ReadyQueue, self).append(item)
        self.sort()


    # @Override the method popleft() from the parent collections.deque
    def popleft(self, *args, **kwargs):
        self.sort()
        return super(ReadyQueue, self).popleft()
