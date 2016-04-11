"""
Title:          DiskDrive.py
Author:         Michael Garod
Date Created:   4/10/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #2
Description:    Add a Disk Drive class which implements FSCAN. Every disk
                holds 2 deques, which is alternated every time the busy queue
                is emptied. The direction of the arm sweep also alternates.
Note:           Deques can be thought of as lists where you push on the right,
                append(), and pop from the left, popleft()
"""
import collections as col


class Disk:
    """
    This Disk Class implements FSCAN. Two queues are kept, busy and waiting.
    If both are empty, the process goes to the busy queue, otherwise it will
    enter the waiting queue. When the busy queue becomes empty, the waiting
    queue will become the busy queue.

    The initial position of the arm is at cylinder zero and will ascend to
    the value of max_cylinders. When the queues, switch, the arm will descend.
    This process repeats cyclically.
    """
    def __init__(self, cylinders):
        self.queues = [col.deque(), col.deque()]
        self.max_cylinders = cylinders
        self.busy_queue = 0  # Which queue is being serviced? 0 or 1
        self.descending = False  # arm sweep direction
        self.current_position = 0

    def append(self, element):
        if not self.get_busy_queue():  # If busy queue is empty, it item there
            self.get_busy_queue().append(element)
        else:  # if busy, then put the element in the waiting queue
            self.get_waiting_queue().append(element)
            self.sort_waiting_queue()

    def popleft(self):
        """
        Get the next item in the busy queue. If the busy queue becomes empty,
        the waiting queue becomes the busy queue and the sweep reverses.
        :return:
        """
        item = self.get_busy_queue().popleft()
        self.current_position = item.cylinder

        if len(self.get_busy_queue()) == 0:
            self.switch_queues()  # change queues, and alternate direction
            self.sort_busy_queue()

        return item

    def get_waiting_queue(self):
        return self.queues[(self.busy_queue + 1) % 2]

    def get_waiting_queue_iter(self):
        return self.get_waiting_queue().__iter__()

    def get_busy_queue(self):
        return self.queues[self.busy_queue]

    def get_busy_queue_iter(self):
        return self.get_busy_queue().__iter__()

    def get_arm_direction(self):
        if not self.descending:
            return "Ascending"
        else:
            return "Descending"

    def switch_queues(self):
        self.busy_queue = ((self.busy_queue + 1) % 2)
        self.descending = not self.descending  # Alternate arm direction
        self.set_initial_position()

    def set_initial_position(self):
        """
        Cylinder max if the current sweep is descending. Zero if ascending.
        :return:
        """
        if self.descending:
            self.current_position = self.max_cylinders
        else:
            self.current_position = 0

    def sort_busy_queue(self):
        busy_queue = self.get_busy_queue()
        items = [busy_queue.pop() for x in range(len(busy_queue))]
        items = sorted(items, key=lambda p: p.cylinder, reverse=self.descending)
        busy_queue.extend(items)

    def sort_waiting_queue(self):
        """
        Sort in the opposite fashion of the busy queue
        :return:
        """
        waiting_queue = self.get_waiting_queue()
        items = [waiting_queue.pop() for x in range(len(waiting_queue))]
        items = sorted(items, key=lambda p: p.cylinder,
                       reverse=(not self.descending))
        waiting_queue.extend(items)
