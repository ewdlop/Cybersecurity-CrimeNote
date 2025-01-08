```python
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
import time

class TCPState(Enum):
    """TCP Connection States"""
    CLOSED = auto()
    LISTEN = auto()
    SYN_SENT = auto()
    SYN_RECEIVED = auto()
    ESTABLISHED = auto()
    FIN_WAIT_1 = auto()
    FIN_WAIT_2 = auto()
    CLOSE_WAIT = auto()
    CLOSING = auto()
    LAST_ACK = auto()
    TIME_WAIT = auto()

class TCPFlag(Enum):
    """TCP Flags"""
    SYN = auto()
    ACK = auto()
    FIN = auto()
    RST = auto()

@dataclass
class TCPSegment:
    """TCP Segment with flags and sequence numbers"""
    flags: List[TCPFlag]
    seq_num: int
    ack_num: Optional[int] = None
    data: bytes = b''

class TCPEndpoint:
    """Represents one endpoint of a TCP connection"""
    
    def __init__(self, name: str):
        self.name = name
        self.state = TCPState.CLOSED
        self.seq_num = random.randint(0, 65535)
        self.ack_num: Optional[int] = None
        self.segments_sent: List[TCPSegment] = []
        self.segments_received: List[TCPSegment] = []
        
        # Define valid state transitions
        self.transitions = {
            # Current State: {(Flags received): Next State}
            TCPState.CLOSED: {
                (TCPFlag.SYN,): TCPState.SYN_RECEIVED,
            },
            TCPState.LISTEN: {
                (TCPFlag.SYN,): TCPState.SYN_RECEIVED,
            },
            TCPState.SYN_SENT: {
                (TCPFlag.SYN, TCPFlag.ACK): TCPState.ESTABLISHED,
                (TCPFlag.SYN,): TCPState.SYN_RECEIVED,
            },
            TCPState.SYN_RECEIVED: {
                (TCPFlag.ACK,): TCPState.ESTABLISHED,
            },
            TCPState.ESTABLISHED: {
                (TCPFlag.FIN,): TCPState.CLOSE_WAIT,
                (TCPFlag.FIN, TCPFlag.ACK): TCPState.CLOSE_WAIT,
            },
            TCPState.FIN_WAIT_1: {
                (TCPFlag.FIN, TCPFlag.ACK): TCPState.TIME_WAIT,
                (TCPFlag.ACK,): TCPState.FIN_WAIT_2,
                (TCPFlag.FIN,): TCPState.CLOSING,
            },
            TCPState.FIN_WAIT_2: {
                (TCPFlag.FIN,): TCPState.TIME_WAIT,
            },
            TCPState.CLOSE_WAIT: {
                # Application close triggers transition to LAST_ACK
            },
            TCPState.CLOSING: {
                (TCPFlag.ACK,): TCPState.TIME_WAIT,
            },
            TCPState.LAST_ACK: {
                (TCPFlag.ACK,): TCPState.CLOSED,
            },
            TCPState.TIME_WAIT: {
                # 2MSL timeout triggers transition to CLOSED
            },
        }
    
    def process_segment(self, segment: TCPSegment) -> Optional[TCPSegment]:
        """
        Process received TCP segment and generate response if needed
        Returns response segment or None
        """
        print(f"{self.name} received segment with flags {[f.name for f in segment.flags]}")
        
        # Store received segment
        self.segments_received.append(segment)
        
        # Check for valid state transition
        current_transitions = self.transitions.get(self.state, {})
        flags_tuple = tuple(sorted(segment.flags, key=lambda x: x.name))
        
        next_state = current_transitions.get(flags_tuple)
        if next_state:
            print(f"{self.name} transitioning from {self.state.name} to {next_state.name}")
            self.state = next_state
            
            # Generate response based on state transition
            response = self._generate_response(segment)
            if response:
                self.segments_sent.append(response)
                return response
                
        return None
    
    def _generate_response(self, received: TCPSegment) -> Optional[TCPSegment]:
        """Generate appropriate response segment based on current state"""
        if self.state == TCPState.SYN_RECEIVED:
            # Send SYN-ACK
            return TCPSegment(
                flags=[TCPFlag.SYN, TCPFlag.ACK],
                seq_num=self.seq_num,
                ack_num=received.seq_num + 1
            )
            
        elif self.state == TCPState.ESTABLISHED:
            # Send ACK for received data or FIN
            if TCPFlag.FIN in received.flags:
                self.ack_num = received.seq_num + 1
                return TCPSegment(
                    flags=[TCPFlag.ACK],
                    seq_num=self.seq_num,
                    ack_num=self.ack_num
                )
                
        elif self.state == TCPState.CLOSE_WAIT:
            # Send FIN-ACK
            return TCPSegment(
                flags=[TCPFlag.FIN, TCPFlag.ACK],
                seq_num=self.seq_num,
                ack_num=self.ack_num
            )
            
        elif self.state == TCPState.LAST_ACK:
            # Transition to CLOSED after receiving ACK
            if TCPFlag.ACK in received.flags:
                self.state = TCPState.CLOSED
                
        return None
    
    def active_open(self) -> TCPSegment:
        """Initiate connection (active open)"""
        if self.state == TCPState.CLOSED:
            self.state = TCPState.SYN_SENT
            segment = TCPSegment(flags=[TCPFlag.SYN], seq_num=self.seq_num)
            self.segments_sent.append(segment)
            return segment
        raise ValueError(f"Cannot perform active open in state {self.state}")
    
    def passive_open(self):
        """Prepare for incoming connection (passive open)"""
        if self.state == TCPState.CLOSED:
            self.state = TCPState.LISTEN
        else:
            raise ValueError(f"Cannot perform passive open in state {self.state}")
    
    def close(self) -> Optional[TCPSegment]:
        """Initiate connection termination"""
        if self.state == TCPState.ESTABLISHED:
            self.state = TCPState.FIN_WAIT_1
            segment = TCPSegment(
                flags=[TCPFlag.FIN],
                seq_num=self.seq_num,
                ack_num=self.ack_num
            )
            self.segments_sent.append(segment)
            return segment
        elif self.state == TCPState.CLOSE_WAIT:
            self.state = TCPState.LAST_ACK
            segment = TCPSegment(
                flags=[TCPFlag.FIN],
                seq_num=self.seq_num,
                ack_num=self.ack_num
            )
            self.segments_sent.append(segment)
            return segment
        return None

class TCPConnection:
    """Simulates a TCP connection between two endpoints"""
    
    def __init__(self):
        self.client = TCPEndpoint("Client")
        self.server = TCPEndpoint("Server")
        self.msl_timeout = 2  # Maximum Segment Lifetime in seconds
    
    def simulate_handshake(self):
        """Simulate three-way handshake"""
        print("\nSimulating TCP three-way handshake:")
        
        # Step 1: Client sends SYN
        print("\nStep 1: Client sends SYN")
        self.server.passive_open()
        syn = self.client.active_open()
        
        # Step 2: Server responds with SYN-ACK
        print("\nStep 2: Server sends SYN-ACK")
        syn_ack = self.server.process_segment(syn)
        if not syn_ack:
            raise RuntimeError("Failed to get SYN-ACK from server")
        
        # Step 3: Client sends ACK
        print("\nStep 3: Client sends ACK")
        ack = self.client.process_segment(syn_ack)
        if ack:
            self.server.process_segment(ack)
            
        print(f"\nConnection established: Client state: {self.client.state.name}, "
              f"Server state: {self.server.state.name}")
    a
    def simulate_termination(self):
        """Simulate connection termination"""
        print("\nSimulating TCP connection termination:")
        
        # Step 1: Client initiates close
        print("\nStep 1: Client sends FIN")
        fin = self.client.close()
        
        # Step 2: Server sends ACK
        print("\nStep 2: Server sends ACK")
        ack = self.server.process_segment(fin)
        if ack:
            self.client.process_segment(ack)
        
        # Step 3: Server sends FIN
        print("\nStep 3: Server sends FIN")
        server_fin = self.server.close()
        
        # Step 4: Client sends final ACK
        print("\nStep 4: Client sends final ACK")
        if server_fin:
            final_ack = self.client.process_segment(server_fin)
            if final_ack:
                self.server.process_segment(final_ack)
        
        # Wait for TIME_WAIT to expire
        if self.client.state == TCPState.TIME_WAIT:
            print(f"\nClient in TIME_WAIT, waiting {self.msl_timeout}s...")
            time.sleep(self.msl_timeout)
            self.client.state = TCPState.CLOSED
            
        print(f"\nConnection terminated: Client state: {self.client.state.name}, "
              f"Server state: {self.server.state.name}")

def example_usage():
    """Demonstrate TCP connection lifecycle"""
    
    connection = TCPConnection()
    
    # Perform three-way handshake
    connection.simulate_handshake()
    
    # Simulate some data transfer (not shown)
    time.sleep(1)
    
    # Terminate connection
    connection.simulate_termination()

if __name__ == "__main__":
    example_usage()
```
