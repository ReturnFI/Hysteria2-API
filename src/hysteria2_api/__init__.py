from .client import Hysteria2Client as AsyncHysteria2Client, SyncHysteria2Client
from .exceptions import Hysteria2Error, Hysteria2AuthError, Hysteria2ConnectionError
from .models import TrafficStats, OnlineStatus

Hysteria2Client = SyncHysteria2Client 

__version__ = "0.1.1"
__all__ = [
    "Hysteria2Client",
    "AsyncHysteria2Client",
    "SyncHysteria2Client",
    "Hysteria2Error",
    "Hysteria2AuthError", 
    "Hysteria2ConnectionError",
    "TrafficStats",
    "OnlineStatus"
]
