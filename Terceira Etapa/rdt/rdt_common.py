import socket
from dataclasses import dataclass
import struct

MAX_TRIES = 8
TIMEOUT = 0.05
SYNC = 0x01
DATA = 0x00


@dataclass
class PacketHeader:
    seq: int = 0
    ack: int = 0

    @staticmethod
    def from_bytes(data: bytes):
        if len(data) < PacketHeader.size():
            raise ValueError("Data too short to unpack Header")
        
        seq, ack = struct.unpack('!II', data[:PacketHeader.size()])
        return PacketHeader(seq=seq, ack=ack)

    def to_bytes(self) -> bytes:
        return struct.pack('!II', self.seq, self.ack)

    @staticmethod
    def size() -> int:
        return struct.calcsize('!II')


@dataclass
class RDTManagerHeader:
    msg_type: int = 0
    ip: str = ""
    receiver_port: int = 0
    sender_port: int = 0

    @staticmethod
    def control_size() -> int:
        return struct.calcsize('!B')

    @staticmethod
    def full_size() -> int:
        return struct.calcsize('!B4sHH')

    def byte_size(self) -> int:
        return RDTManagerHeader.full_size() if self.is_sync() else RDTManagerHeader.control_size()

    def is_sync(self) -> bool:
        return (self.msg_type & SYNC) != 0

    def to_bytes(self) -> bytes:
        if not self.is_sync():
            return struct.pack('!B', self.msg_type)
        
        ip_bytes = socket.inet_aton(self.ip)
        return struct.pack('!B4sHH', self.msg_type, ip_bytes, self.receiver_port, self.sender_port)

    @staticmethod
    def from_bytes(data: bytes):
        if len(data) < RDTManagerHeader.control_size():
            raise ValueError("Data too short to unpack RDTManagerHeader (control)")
        
        (msg_type,) = struct.unpack('!B', data[:1])

        if (msg_type & SYNC) != 0:
            need = RDTManagerHeader.full_size()

            if len(data) < need:
                raise ValueError("Data too short to unpack RDTManagerHeader (full)")
            
            _, ip_bytes, receiver_port, sender_port = struct.unpack('!B4sHH', data[:need])
            ip = socket.inet_ntoa(ip_bytes)

            return RDTManagerHeader(msg_type=msg_type, ip=ip,
                                    receiver_port=receiver_port, sender_port=sender_port), need
        else:
            return RDTManagerHeader(msg_type=msg_type), RDTManagerHeader.control_size()


@dataclass
class ConnectionState:
    send_seq: int = 0
    expected_seq: int = 0


@dataclass(frozen=True, eq=True)
class Peer:
    host: str
    port: int

    def __str__(self):
        return f"{self.host}:{self.port}"
    
    def get_address(self):
        return (self.host, self.port)
    
    def __iter__(self):
        yield self.host
        yield self.port
