from queue import Queue, Empty
from .rdt_sender import RDTSender
from .rdt_receiver import RDTReceiver
from .rdt_common import RDTManagerHeader, Peer, SYNC, DATA, TIMEOUT, MAX_TRIES
import threading

class RDT:
    def __init__(self, host='127.0.0.1', port=0):
        self.connections_state = {}

        self.to_sender_queue = Queue()
        self.from_receiver_queue = Queue()
        self.user_message_queue = Queue()

        self.peer_to_receiver = {}
        self.sender_to_peer = {}

        self.pending_connections = {}

        self.receiver = RDTReceiver(
            host=host,
            port=port,
            queue=self.from_receiver_queue,
            connections_state=self.connections_state
        )
        self.sender = RDTSender(
            queue=self.to_sender_queue,
            connections_state=self.connections_state
        )

        self.receiver_thread = threading.Thread(target=self.receiver.run, daemon=True)
        self.sender_thread = threading.Thread(target=self.sender.run, daemon=True)
        self.manager_thread = threading.Thread(target=self._run_manager, daemon=True)

        self.receiver_thread.start()
        self.sender_thread.start()
        self.manager_thread.start()

    def _enqueue_to_send(self, addr, payload_bytes: bytes):
        header = RDTManagerHeader(msg_type=DATA)
        wire = header.to_bytes() + payload_bytes
        self.to_sender_queue.put((addr, wire))

    def _send_sync(self, target_receiver_addr):
        my_info = RDTManagerHeader(
            msg_type=SYNC,
            ip=self.get_address()[0],
            receiver_port=self.get_address()[1],
            sender_port=self.sender.get_address()[1]
        )
        self.to_sender_queue.put((target_receiver_addr, my_info.to_bytes()))

    def _handle_control_message(self, hdr: RDTManagerHeader, sender_addr):
        if not hdr.is_sync():
            return
        
        peer = Peer(hdr.ip, hdr.receiver_port)
        self.peer_to_receiver[peer] = peer.get_address()
        self.sender_to_peer[sender_addr] = peer

        if peer not in self.pending_connections:
            self._send_sync(peer.get_address())

        evt = self.pending_connections.get(peer)
        if evt and not evt.is_set():
            evt.set()

    def _handle_data_message(self, payload: bytes, sender_addr):
        peer = self.sender_to_peer.get(sender_addr)
        if not peer:
            return
        self.user_message_queue.put((peer, payload))

    def _run_manager(self):
        while True:
            try:
                sender_addr, raw_payload = self.from_receiver_queue.get(timeout=0.01)

                try:
                    hdr, offset = RDTManagerHeader.from_bytes(raw_payload)
                except ValueError:
                    continue

                if hdr.is_sync():
                    self._handle_control_message(hdr, sender_addr)
                else:
                    self._handle_data_message(raw_payload[offset:], sender_addr)
            except Empty:
                continue
            except Exception:
                continue

    def connect(self, host, port) -> bool:
        target_peer = Peer(host, port)

        if target_peer in self.peer_to_receiver:
            return True
        
        event = threading.Event()
        self.pending_connections[target_peer] = event

        self._send_sync(target_peer.get_address())

        success = event.wait(timeout=TIMEOUT * (MAX_TRIES + 2))
        self.pending_connections.pop(target_peer, None)
        return success

    def send(self, data: bytes, peer: Peer):
        if peer not in self.peer_to_receiver:
            raise ConnectionError(f"Not connected to peer {peer}. Use connect() first.")
        self._enqueue_to_send(self.peer_to_receiver[peer], data)

    def broadcast(self, data: str):
        payload = data.encode('utf-8', errors='strict')
        for peer in self.peer_to_receiver:
            self._enqueue_to_send(self.peer_to_receiver[peer], payload)

    def receive(self, timeout=None):
        try:
            return self.user_message_queue.get(timeout=timeout)
        except Empty:
            return None, None

    def get_address(self):
        return self.receiver.get_address()