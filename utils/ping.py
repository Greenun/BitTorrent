import socket
import struct
import select
import sys


class Ping(object):
    def __init__(self, etime=0.5):
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
        # self.socket.settimeout(etime)
        self.packet = None
        self.sockets = None

    def make_packet(self, data="A"):
        _type = 8  # echo
        _code = 0  # no code in echo
        _checksum = 0
        _etc = 1
        header = struct.pack("!bbHI", _type, _code, _checksum, _etc)  # , _seq
        _checksum = self.calculate_chksum(header)
        # print(_checksum)
        header = struct.pack("!bbHI", _type, _code, _checksum, _etc)
        self.packet = header
        return header

    def calculate_chksum(self, data):
        _sum = 0
        size = len(data)
        if (size % 2) == 1:
            data += b'\x00'
            size += 1
        for i in range(0, size, 2):
            _sum += data[i] * 256 + data[i + 1]

        while not ((_sum >> 16) == 0):
            _sum = (_sum >> 16) + (_sum & 0xFFFF)
        _sum = ~_sum & 0xFFFF
        return _sum

    def send(self, ip_list, data=None):
        if not self.packet:
            self.make_packet()
        for ip in ip_list:
            self.socket.sendto(self.packet, (ip, 0))

    def multi_send(self, ip_list, data=None):
        if not self.packet:
            self.make_packet()

        sockets = []
        for ip in ip_list:
            info = {"ip": ip,
                    "socket": socket.socket(socket.AF_INET, socket.SOCK_RAW, 1),
                    }
            info["socket"].setblocking(1)
            sockets.append(info)
        for s in sockets:
            s["socket"].sendto(self.packet, (s["ip"], 0))
        self.sockets = sockets

    def receive(self, ip_list):
        # import time
        done_list = list()
        # failed_count = 0
        if self.sockets:
            while 1:
                rd, wr, _ = select.select([x["socket"] for x in self.sockets if not x["socket"].fileno() == -1], [], [], 0.5)
                print(rd)
                if not rd: break  # break if no waiting
                for d in rd:
                    try:
                        recv, addr = d.recvfrom(1)
                        # print(d, addr)
                        if recv and addr[0] not in done_list:
                            d.close()
                            done_list.append(addr[0])
                    except socket.timeout:
                        # failed_count += 1
                        print(sys.exc_info())
        for s in self.sockets:
            print(s["socket"])
            if not s["socket"].fileno() == -1:
                s["socket"].close()
        self.sockets = None
        print("Ping failed : ", (len(ip_list) - len(done_list)))
        return done_list

    def ping_check(self, ip_list):
        # self.send(ip_list)
        self.multi_send(ip_list)

        enable_ip = self.receive(ip_list)
        return enable_ip


if __name__ == '__main__':
    ip_list = ["8.8.8.8", "127.0.0.1", "120.152.122.1"]
    p = Ping()
    p.ping_check(ip_list)
