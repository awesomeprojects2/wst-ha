"""Exceptions for the WST integration."""


class WSTApiError(Exception):
    """Base exception for WST API errors."""


class WSTApiCommunicationError(WSTApiError):
    """Exception for communication errors with the WST API."""


class WSTApiAuthError(WSTApiError):
    """Exception for authentication errors with the WST API."""


class WSTApiTimeoutError(WSTApiError):
    """Exception for timeout errors when calling the WST API."""