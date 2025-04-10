from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TrafficStats:
    """Represents traffic statistics for a client."""
    tx: int
    rx: int

    @property
    def upload_bytes(self) -> int:
        """Alias for tx (transmitted bytes)."""
        return self.tx

    @property
    def download_bytes(self) -> int:
        """Alias for rx (received bytes)."""
        return self.rx
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "TrafficStats":
        """Create a TrafficStats instance from a dictionary."""
        return cls(
            tx=data.get("tx", 0),
            rx=data.get("rx", 0)
        )


@dataclass
class OnlineStatus:
    """Represents online status information for clients."""
    connections: int

    @property
    def is_online(self) -> bool:
        """Check if the client is online (has at least one connection)."""
        return self.connections > 0
    
    @classmethod
    def from_int(cls, connections: int) -> "OnlineStatus":
        """Create an OnlineStatus instance from the connection count."""
        return cls(connections=connections)