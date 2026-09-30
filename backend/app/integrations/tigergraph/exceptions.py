class TigerGraphError(Exception):
    """Base exception for all TigerGraph integration errors."""
    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details


class TigerGraphConnectionError(TigerGraphError):
    """Raised when establishing a connection to TigerGraph fails."""
    pass


class TigerGraphAuthenticationError(TigerGraphError):
    """Raised when secret/token authentication or login fails."""
    pass


class TigerGraphQueryError(TigerGraphError):
    """Raised when graph query execution fails."""
    pass


class TigerGraphUpsertError(TigerGraphError):
    """Raised when upserting vertices or edges fails."""
    pass
