"""Application exceptions."""

from typing import Any


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__("NOT_FOUND", message, 404)


class ValidationError(AppError):
    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__("VALIDATION_ERROR", message, 400, details)


class PayloadTooLargeError(AppError):
    def __init__(self, message: str = "Payload too large"):
        super().__init__("PAYLOAD_TOO_LARGE", message, 413)


class UnsupportedMediaTypeError(AppError):
    def __init__(self, message: str = "Unsupported media type"):
        super().__init__("UNSUPPORTED_MEDIA_TYPE", message, 415)


class ParseError(AppError):
    def __init__(self, message: str = "Failed to parse IaC files"):
        super().__init__("PARSE_ERROR", message, 422)


class ScanInProgressError(AppError):
    def __init__(self, message: str = "Scan is still in progress"):
        super().__init__("SCAN_IN_PROGRESS", message, 409)


class RateLimitedError(AppError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__("RATE_LIMITED", message, 429)


class ScanTimeoutError(AppError):
    def __init__(self, message: str = "Scan timed out"):
        super().__init__("SCAN_TIMEOUT", message, 504)
