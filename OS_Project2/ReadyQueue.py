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
                burst.
"""
import collections as col


class ReadyQueue(col.deque):
    def __init__(self):
        super(ReadyQueue, self).__init__()

    def sort(self):
        """
        Order PCBs contained in the ReadyQueue by the estimated burst minus
        the current burst (working_tau)

        The commented out line was used to break ties by age (PID since they
        are issued sequentially). It was removed because it was not required.

        A deque cannot sort itself. It must empty itself into a list, then
        sort the list, and reinsert that list into the deque.
        :return:
        """
        items = [self.pop() for x in range(len(self))]
        # items = sorted(items, key=lambda p: p.id)
        items = sorted(items, key=lambda p: p.working_tau)
        self.extend(items)

    # @Override the method popleft() from the parent collections.deque
    def popleft(self, *args, **kwargs):
        self.sort()
        return super(ReadyQueue, self).popleft()
