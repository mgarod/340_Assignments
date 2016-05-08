"""
Title:          JobPool.py
Author:         Michael Garod
Date Created:   4/26/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #3
Description:    Implementation of the JobPool held on secondary memory
                when there is not enough primary memory available.
Note:           JobPool is just a list that maintains descending sorted order.
"""


class JobPool(list):
    def __init__(self):
        super(JobPool, self).__init__()

    def append(self, item):
        super(JobPool, self).append(item)
        super(JobPool, self).sort(key=lambda x: x.mem_usage, reverse=True)

    def get_largest_fit(self, avail_mem):
        """
        Find the largest job in the job pool that can make use of avail_mem

        :param avail_mem: The amount of memory (in_words) available.
        :return: An error code, or the largest job that will fit in memory
        """
        if len(self) == 0:  # If empty, don't continue
            return 0
        elif self[-1].mem_usage > avail_mem:  # Is there any job that could fit?
            # If the smallest element, is larger than available memory, halt
            return 1

        # There must exist an element that can be placed in memory
        for i, v in enumerate(self):
            if v.mem_usage <= avail_mem:
                return self.pop(i)
