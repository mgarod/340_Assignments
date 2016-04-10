import collections as col
import ProcessControlBlock as pcb
import random as r


class Disk(col.deque):
    def __init__(self, cylinders):
        super(Disk, self).__init__()
        self.max_cylinders = cylinders

    # http://stackoverflow.com/questions/19795642/how-to-sort-class-on-datetime-sort-collections-deque
    def sort(self):
        items = [self.pop() for x in range(len(self))]
        items = sorted(items, key=lambda p: p.cylinder)
        self.extend(items)

"""
JUST FOR TESTING

def print_pcb(l):
    for i in l:
        print str(i.tau_current)+",",
    print


def go():
    d = Disk(20)
    pid = 1
    for x in range(0,20):
        p = pcb.PCB(pid, r.randint(0,100), 0.5)
        d.append(p)
        pid += 1

    print_pcb(d)

    d.sort()

    print_pcb(d)

go()
"""
