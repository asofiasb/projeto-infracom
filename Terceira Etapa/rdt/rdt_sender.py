import socket
from queue import Queue, Empty
from .rdt_common import *

class RDTSender:
    def __init__(self, queue=None, connections_state=None):
        if queue is None or connections_state is None:
            raise ValueError("Queue and connections_state must be provided to RDTSender")
        self.queue = queue
        self.connections_state = connections_state

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 0))
        self.host, self.port = self.sock.getsockname()

    def send(self, data: bytes, rcv_addr):
        state = self.connections_state.setdefault(rcv_addr, ConnectionState())
        header = PacketHeader(seq=state.send_seq, ack=0)
        packet = header.to_bytes() + data

        self.sock.settimeout(TIMEOUT)

        try:
            for _ in range(MAX_TRIES):
                self.sock.sendto(packet, rcv_addr)
                try:
                    ack_data, _ = self.sock.recvfrom(PacketHeader.size())
                    if len(ack_data) == PacketHeader.size():
                        ack_header = PacketHeader.from_bytes(ack_data)

                        if ack_header.ack == state.send_seq:
                            state.send_seq = 1 - state.send_seq
                            return True
                except (socket.timeout, ValueError):
                    continue
            return False
        
        finally:
            self.sock.settimeout(None)

    def get_address(self):
        return (self.host, self.port)

    def run(self):
        while True:
            try:
                addr, data = self.queue.get(timeout=0.01)
                self.send(data, addr)
            except Empty:
                continue
            except Exception:
                continue