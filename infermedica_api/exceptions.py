# -*- coding: utf-8 -*-

"""
infermedica_api.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the set of API request exceptions.
"""


class ConnectionError(Exception):
    """API connection error."""

    def __init__(self, response, content=None):
        self.response = response
        self.content = content

    def __str__(self):
        message = "Failed."
        if hasattr(self.response, 'status_code'):
            message += " Response status: %s." % (self.response.status_code)
        if hasattr(self.response, 'reason'):
            message += " Reason: %s." % (self.response.reason)
        if self.content is not None:
            message += " Error message: " + str(self.content)
        return message


class BadRequest(ConnectionError):
    """400 Bad Request."""


class UnauthorizedAccess(ConnectionError):
    """401 Unauthorized."""


class ForbiddenAccess(ConnectionError):
    """403 Forbidden."""


class ResourceNotFound(ConnectionError):
    """404 Not found."""


class ServerError(ConnectionError):
    """5xx Server Error."""


class MissingConfiguration(Exception):
    """API not configured."""

    def __init__(self, alias=None):
        self.alias = alias

    def __str__(self):
        if self.alias:
            return "API credentials for alias '%s' has not been configured." % self.alias
        return "API credentials has not been configured."


class MethodNotAllowed(ConnectionError):
    """405 Method Not Allowed."""


class MethodNotAvailableInAPIVersion(Exception):
    """Try to call API method, which is not available."""

    def __init__(self, current_api_version, method):
        self.api_version = current_api_version
        self.method = method

    def __str__(self):
        return "Method '%s' is not available in the %s api version." % (self.method, self.api_version)


class InvalidSearchFilter(Exception):
    """API not configured."""

    def __init__(self, filter):
        self.filter = filter

    def __str__(self):
        return "Invalid search filter: '%s'." % self.filter
