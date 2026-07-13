"""Domain exceptions for the E2EE payload pipeline."""


class DecryptionError(Exception):
    """Raised when the encrypted payload cannot be decrypted with the configured key."""


class MalformedPayloadError(Exception):
    """Raised when the decrypted payload does not match the expected identity schema."""


class EventPublishError(Exception):
    """Raised when publishing the verified payload event fails."""
