"""
Custom exceptions for DhakaSmart platform.

These exceptions are explicit and never silently swallowed.
Every calculation failure surfaces as one of these.
"""
from __future__ import annotations


class DhakaSmartError(Exception):
    """Base exception for all platform errors."""

    def __init__(self, message: str, *, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class ValidationFailure(DhakaSmartError):
    """Raised when an input fails validation."""


class GeometryError(DhakaSmartError):
    """Raised when building/room geometry is inconsistent or impossible."""


class CalculationError(DhakaSmartError):
    """Raised when a deterministic calculation cannot produce a valid result."""


class InsufficientDataError(DhakaSmartError):
    """Raised when required inputs are missing.

    IMPORTANT: This is NOT a calculation failure — it means the result must be
    labelled "Insufficient data", never silently replaced with zero.
    """


class SourceUnavailableError(DhakaSmartError):
    """Raised when a required data source cannot be accessed."""


class UnitMismatchError(DhakaSmartError):
    """Raised when units are inconsistent within a calculation."""


class RegulatoryClaimError(DhakaSmartError):
    """Raised when code attempts to make an unverified regulatory claim.

    The platform must never declare compliance without verified rule + inputs.
    """