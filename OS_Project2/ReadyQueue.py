import collections as col


class ReadyQueue(col.deque):
    def __init__(self):
        super(ReadyQueue, self).__init__()

    def sort(self):
        """
        Ordering first by working_tau, and break ties by pid
        :return:
        """
        items = [self.pop() for x in range(len(self))]
        items = sorted(items, key=lambda p: p.id)
        items = sorted(items, key=lambda p: p.working_tau)
        self.extend(items)

    # @Override
    def popleft(self, *args, **kwargs):
        self.sort()
        return super(ReadyQueue, self).popleft()
