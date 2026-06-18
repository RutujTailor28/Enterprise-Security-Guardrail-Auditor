"""Domain enumerations."""

from enum import Enum


class ScanStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FileType(str, Enum):
    TERRAFORM = "terraform"
    CLOUDFORMATION = "cloudformation"


class Resolution(str, Enum):
    RESOLVED = "resolved"
    PARTIAL = "partial"
    UNRESOLVED = "unresolved"
