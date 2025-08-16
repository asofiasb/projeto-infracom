import socket
from queue import Queue
from .rdt_common import *

class RDTReceiver:
    def __init__(self, host='127.0.0.1', port=0, queue=None, connections_state=None):
        if queue is None or connections_state is None:
            raise ValueError("Queue and connections_state must be provided to RDTReceiver")
        self.queue = queue
        self.connections_state = connections_state

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.host, self.port = self.sock.getsockname()

    def send_ack(self, ack_num, addr):
        ack_header = PacketHeader(seq=0, ack=ack_num)
        self.sock.sendto(ack_header.to_bytes(), addr)

    def _handle_packet(self, data: bytes, addr):
        if len(data) < PacketHeader.size():
            return
        
        try:
            header = PacketHeader.from_bytes(data)
            content = data[PacketHeader.size():]
        except ValueError:
            return
        
        state = self.connections_state.setdefault(addr, ConnectionState())

        if header.seq == state.expected_seq:
            self.queue.put((addr, content))
            self.send_ack(header.seq, addr)
            state.expected_seq = 1 - state.expected_seq
        else:
            self.send_ack(1 - state.expected_seq, addr)

    def get_address(self):
        return (self.host, self.port)

    def run(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(65535)
                if data:
                    self._handle_packet(data, addr)
            except Exception:
                continue
