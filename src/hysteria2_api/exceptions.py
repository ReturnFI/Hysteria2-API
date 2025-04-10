class Hysteria2Error(Exception):
    """Base exception for all Hysteria2 API errors."""
    pass


class Hysteria2AuthError(Hysteria2Error):
    """Raised when authentication with the Hysteria2 API fails."""
    pass


class Hysteria2ConnectionError(Hysteria2Error):
    """Raised when there's an error connecting to the Hysteria2 API."""
    pass