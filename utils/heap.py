import heapq


class Node(object):
    def __init__(self, distance: int, node_info: dict):
        self.distance = distance
        self.node_info = node_info

    def __lt__(self, other):
        return self.distance < other.distance

    def __repr__(self):
        string = ""
        for key in self.node_info:
            string += f"{key}={self.node_info[key]}, "
        return f"<Node({string}distance={self.distance})>"


class DistanceHeap(object):
    def __init__(self):
        self.queue = list()

    def push(self, value: Node):
        heapq.heappush(self.queue, value)

    def pop(self) -> Node:
        return heapq.heappop(self.queue)
