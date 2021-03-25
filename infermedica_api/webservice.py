# -*- coding: utf-8 -*-

"""
infermedica_api.webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains function responsible for manging a global handlers for API Connector classes.
"""
from inspect import isclass
from typing import Optional, Any, Union

from . import exceptions, connectors

__api__ = None
__api_aliased__ = {}


def get_api(alias: str = None) -> connectors.APIConnectorType:
    """
    Returns global API object if present,
    otherwise raise MissingConfiguration exception.

    :param alias: Alias of the API to retrieve

    :returns: An API object

    :raises: :class:`infermedica_api.exceptions.MissingConfiguration`
    """
    global __api__
    global __api_aliased__

    if alias:
        try:
            return __api_aliased__[alias]
        except KeyError:
            raise exceptions.MissingConfiguration(alias)

    if __api__ is None:
        raise exceptions.MissingConfiguration()

    return __api__


def configure(
    app_id: str,
    app_key: str,
    alias: Optional[str] = None,
    default: Optional[bool] = False,
    api_connector: Optional[Union[connectors.APIConnectorType, str]] = "APIv3Connector",
    **kwargs: Any
) -> connectors.APIConnectorType:
    """
    Configure and create new global API object with given configuration. Many global configurations can be created
    upfront (e.g. with different credentials or language models configured) by providing a unique alias
    for each configuration. The configrations can be latter accessed any where in the projcts by
    simply calling `infermedica_api.get_api()` or `infermedica_api.get_api('<alias>')`.

    Usage:
        >>> import infermedica_api
        >>> infermedica_api.configure(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')

        # Then somewhere in the project:
        >>> import infermedica_api
        >>> api = infermedica_api.get_api()
        >>> api.info()

    :param app_id: Infermedica API App Id
    :param app_key: Infermedica API App Key
    :param alias: (optional) Alias for the configuration, if not provided the configuration
                  became the default configuration when calling `get_api` without alias
    :param default: (optional) If alias proveded determinates if this configuration
                    should also be set as the default configuration when calling `get_api` without alias
    :param api_connector: (optional) APIConnector class (may be custom) or a name of the of
                          the build in API connector classes to be used
    :param kwargs: (optional) Config to be used to initialise API connector class

    :returns: An API connctor object
    """
    global __api__
    global __api_aliased__

    if isclass(api_connector):
        api_connector_class = api_connector
    else:
        api_connector_class = getattr(connectors, api_connector)
    api_obj = api_connector_class(app_id=app_id, app_key=app_key, **kwargs)

    if alias:
        __api_aliased__[alias] = api_obj

        if default:
            __api__ = api_obj
    else:
        __api__ = api_obj

    return api_obj
