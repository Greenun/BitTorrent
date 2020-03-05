import heapq


class DistanceQueue(object):
    def __init__(self):
        self.heap = list()

    def __lt__(self, other):
        # temp
        return self[0] < other[0]