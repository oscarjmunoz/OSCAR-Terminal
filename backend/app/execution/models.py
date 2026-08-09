from dataclasses import dataclass
from enum import Enum


class ValidationStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class ValidationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(slots=True)
class ValidationResult:
    status: ValidationStatus
    message: str
    severity: ValidationSeverity
