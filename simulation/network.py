"""
simulation/network.py

Virtual network topology for AI-SNIDS.

Creates a software-only representation of a small network
for safe demonstration of intrusion detection scenarios.

SAFETY: No real network interfaces, sockets, or OS-level
resources are created. This is purely a data model.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VirtualDevice:
    """Represents a simulated logical node in the network."""
    device_id: str
    hostname: str
    ip_address: str
    device_type: str  # "Client", "Server", "Router", "Attacker", "IDS"
    status: str = "ONLINE"


@dataclass
class VirtualNetwork:
    """Represents the logical topology of the simulated network."""
    devices: List[VirtualDevice] = field(default_factory=list)

    def add_device(self, device: VirtualDevice):
        self.devices.append(device)

    def get_device_by_ip(self, ip: str) -> Optional[VirtualDevice]:
        for d in self.devices:
            if d.ip_address == ip:
                return d
        return None

    def get_clients(self) -> List[VirtualDevice]:
        return [d for d in self.devices if d.device_type == "Client"]

    def get_servers(self) -> List[VirtualDevice]:
        return [d for d in self.devices if d.device_type == "Server"]

    def get_attackers(self) -> List[VirtualDevice]:
        return [d for d in self.devices if d.device_type == "Attacker"]

    def get_router(self) -> Optional[VirtualDevice]:
        routers = [d for d in self.devices if d.device_type == "Router"]
        return routers[0] if routers else None


def create_default_topology() -> VirtualNetwork:
    """
    Creates the standard AI-SNIDS lab topology.

    Topology:
                        INTERNET
                           |
                     [ ROUTER ]
                      10.0.0.1
                           |
          +----------------+----------------+
          |                |                |
     [ CLIENT A ]    [ ATTACKER ]    [ SERVER B ]
      10.0.0.10       10.0.0.50      10.0.0.100
                                          |
                                     [ AI-SNIDS ]
    """
    net = VirtualNetwork()

    # Core infrastructure
    net.add_device(VirtualDevice("rt1",  "Router",       "10.0.0.1",   "Router"))
    net.add_device(VirtualDevice("srv1", "Server-B",     "10.0.0.100", "Server"))

    # Legitimate client
    net.add_device(VirtualDevice("cli1", "Client-A",     "10.0.0.10",  "Client"))

    # Primary attacker
    net.add_device(VirtualDevice("atk1", "Attacker",     "10.0.0.50",  "Attacker"))

    # DDoS attacker swarm (used only in DDoS scenario)
    for i in range(1, 7):
        net.add_device(VirtualDevice(
            f"atk_ddos_{i}",
            f"DDoS-Node-{i}",
            f"10.0.0.{50 + i}",
            "Attacker"
        ))

    # AI-SNIDS itself (logical node for visualization)
    net.add_device(VirtualDevice("ids1", "AI-SNIDS",     "10.0.0.200", "IDS"))

    return net
