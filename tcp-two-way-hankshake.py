from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import random
import time

class TCPState(Enum):
    """TCP Connection States for Two-Way Handshake"""
    CLOSED = auto()
    LISTEN = auto()
    SYN_SENT = auto()
    ESTABLISHED = auto()
    FIN_WAIT = auto()
    LAST_ACK = auto()
    TIME_WAIT = auto()

class TCPFlag(Enum):
    """TCP Flags"""
    SYN = auto()      # Synchronize sequence numbers
    ACK = auto()      # Acknowledgment
    FIN = auto()      # Finish
    RST = auto()      # Reset
    SYN_ACK = auto()  # Combined SYN and ACK

@dataclass
class TCPSegment:
    """TCP Segment Structure"""
    flags: List[TCPFlag]
    seq_num: int
    ack_num: Optional[int] = None
    window_size: int = 65535
    data: bytes = b''
    
    def has_flag(self, flag: TCPFlag) -> bool:
        """Check if segment has specific flag"""
        return flag in self.flags

class TCPEndpoint:
    """TCP Endpoint implementing Two-Way Handshake"""
    
    def __init__(self, name: str):
        self.name = name
        self.state = TCPState.CLOSED
        self.seq_num = random.randint(0, 65535)
        self.ack_num: Optional[int] = None
        self.window_size = 65535
        self.mss = 1460  # Maximum Segment Size
        self.segments_sent: List[TCPSegment] = []
        self.segments_received: List[TCPSegment] = []
        
        # State transition table
        self.transitions = {
            TCPState.CLOSED: {
                TCPFlag.SYN: TCPState.SYN_SENT,
            },
            TCPState.LISTEN: {
                TCPFlag.SYN: TCPState.SYN_SENT,
                TCPFlag.SYN_ACK: TCPState.ESTABLISHED,
            },
            TCPState.SYN_SENT: {
                TCPFlag.SYN_ACK: TCPState.ESTABLISHED,
            },
            TCPState.ESTABLISHED: {
                TCPFlag.FIN: TCPState.FIN_WAIT,
            },
            TCPState.FIN_WAIT: {
                TCPFlag.ACK: TCPState.TIME_WAIT,
            }
        }
    
    def process_segment(self, segment: TCPSegment) -> Optional[TCPSegment]:
        """Process received TCP segment and generate response"""
        print(f"{self.name} received segment with flags {[f.name for f in segment.flags]}")
        self.segments_received.append(segment)
        
        response = None
        
        # Find matching flag for state transition
        for flag in segment.flags:
            if (self.state in self.transitions and 
                flag in self.transitions[self.state]):
                new_state = self.transitions[self.state][flag]
                print(f"{self.name} transitioning from {self.state.name} to {new_state.name}")
                self.state = new_state
                response = self._generate_response(segment)
                break
        
        if response:
            self.segments_sent.append(response)
        
        return response
    
    def _generate_response(self, received: TCPSegment) -> Optional[TCPSegment]:
        """Generate appropriate response segment"""
        if self.state == TCPState.ESTABLISHED:
            # Send ACK for connection establishment
            if TCPFlag.SYN in received.flags:
                self.ack_num = received.seq_num + 1
                return TCPSegment(
                    flags=[TCPFlag.ACK],
                    seq_num=self.seq_num,
                    ack_num=self.ack_num,
                    window_size=self.window_size
                )
        
        elif self.state == TCPState.SYN_SENT:
            # Send SYN-ACK for incoming SYN
            if TCPFlag.SYN in received.flags:
                self.ack_num = received.seq_num + 1
                return TCPSegment(
                    flags=[TCPFlag.SYN, TCPFlag.ACK],
                    seq_num=self.seq_num,
                    ack_num=self.ack_num,
                    window_size=self.window_size
                )
        
        elif self.state == TCPState.FIN_WAIT:
            # Send ACK for connection termination
            return TCPSegment(
                flags=[TCPFlag.ACK],
                seq_num=self.seq_num,
                ack_num=received.seq_num + 1,
                window_size=self.window_size
            )
        
        return None
    
    def initiate_connection(self) -> TCPSegment:
        """Initiate two-way handshake"""
        if self.state != TCPState.CLOSED:
            raise ValueError(f"Cannot initiate connection in state {self.state}")
        
        # Send initial SYN
        self.state = TCPState.SYN_SENT
        segment = TCPSegment(
            flags=[TCPFlag.SYN],
            seq_num=self.seq_num,
            window_size=self.window_size
        )
        self.segments_sent.append(segment)
        return segment
    
    def close_connection(self) -> TCPSegment:
        """Initiate connection termination"""
        if self.state != TCPState.ESTABLISHED:
            raise ValueError(f"Cannot close connection in state {self.state}")
        
        # Send FIN
        self.state = TCPState.FIN_WAIT
        segment = TCPSegment(
            flags=[TCPFlag.FIN],
            seq_num=self.seq_num,
            ack_num=self.ack_num,
            window_size=self.window_size
        )
        self.segments_sent.append(segment)
        return segment

class TwoWayTCPConnection:
    """Simulates Two-Way TCP Connection"""
    
    def __init__(self):
        self.client = TCPEndpoint("Client")
        self.server = TCPEndpoint("Server")
        self.established = False
        self.msl_timeout = 2  # Maximum Segment Lifetime (seconds)
    
    def simulate_handshake(self):
        """Simulate two-way handshake"""
        print("\nSimulating Two-Way TCP Handshake:")
        
        # Step 1: Client sends SYN
        print("\nStep 1: Client sends SYN")
        syn = self.client.initiate_connection()
        
        # Step 2: Server responds with SYN-ACK and establishes connection
        print("\nStep 2: Server responds with SYN-ACK and establishes")
        syn_ack = self.server.process_segment(syn)
        if syn_ack:
            self.client.process_segment(syn_ack)
            
        self.established = (
            self.client.state == TCPState.ESTABLISHED and 
            self.server.state == TCPState.ESTABLISHED
        )
        
        print(f"\nConnection established: {self.established}")
        print(f"Client state: {self.client.state.name}")
        print(f"Server state: {self.server.state.name}")
    
    def simulate_termination(self):
        """Simulate connection termination"""
        print("\nSimulating connection termination:")
        
        # Step 1: Client initiates close
        print("\nStep 1: Client sends FIN")
        fin = self.client.close_connection()
        
        # Step 2: Server acknowledges
        print("\nStep 2: Server sends ACK")
        ack = self.server.process_segment(fin)
        if ack:
            self.client.process_segment(ack)
            
        # Wait for TIME_WAIT to expire
        if self.client.state == TCPState.TIME_WAIT:
            print(f"\nClient in TIME_WAIT, waiting {self.msl_timeout}s...")
            time.sleep(self.msl_timeout)
            self.client.state = TCPState.CLOSED
            
        print(f"\nConnection terminated")
        print(f"Client state: {self.client.state.name}")
        print(f"Server state: {self.server.state.name}")

def example_usage():
    """Demonstrate Two-Way TCP handshake"""
    
    connection = TwoWayTCPConnection()
    
    # Perform handshake
    connection.simulate_handshake()
    
    # Simulate some data transfer (not shown)
    time.sleep(1)
    
    # Terminate connection
    connection.simulate_termination()

if __name__ == "__main__":
    example_usage()
