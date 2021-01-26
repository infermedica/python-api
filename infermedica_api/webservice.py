# -*- coding: utf-8 -*-

"""
infermedica_api.webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains classes and function responsible for making API requests.
"""

from . import exceptions, connectors
from .connectors import APIConnector, APIv2Connector, APIv2ModelConnector, SEARCH_FILTERS


__api__ = None
__api_aliased__ = {}


def get_api(alias=None):
    """
    Returns global API object and if present,
    otherwise raise MissingConfiguration exception.

    :param alias: Alias of the API to retrieve
    :type alias: str

    :returns: An API object
    :rtype: :class:`infermedica_api.webservice.API`
    :raises: :class:`infermedica_api.exceptions.MissingConfiguration`
    """
    global __api__
    global __api_aliased__

    if isinstance(alias, str):
        try:
            return __api_aliased__[alias]
        except KeyError:
            raise exceptions.MissingConfiguration(alias)

    if __api__ is None:
        raise exceptions.MissingConfiguration()

    return __api__


def configure(options=None, **config):
    """
    Configure and create new global API object with given configuration.
    Configuration can be passed as a dict or separate arguments.
    Returns newly created object.

    Usage:
        >>> import infermedica_api
        >>> infermedica_api.configure({'app_id': 'YOUR_APP_ID', 'app_key': 'YOUR_APP_KEY'})

    ... or:
        >>> import infermedica_api
        >>> infermedica_api.configure(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')

    :param options: Dict with configuration data
    :type options: dict

    :returns: An API object
    :rtype: :class:`infermedica_api.webservice.API`
    """
    global __api__
    global __api_aliased__

    configuration = dict(options or {}, **config)

    api_connector_class = getattr(connectors, configuration.get('api_connector') or 'APIv2ModelConnector')

    if 'alias' in configuration and isinstance(configuration['alias'], str):
        __api_aliased__[configuration['alias']] = api_connector_class(**configuration)

        if configuration.get('default', False):
            __api__ = __api_aliased__[configuration['alias']]

        return __api_aliased__[configuration['alias']]

    __api__ = api_connector_class(**configuration)

    return __api__
