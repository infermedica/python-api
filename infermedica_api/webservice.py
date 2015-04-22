# -*- coding: utf-8 -*-

"""
infermedica_api.webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains classes and function responsible for making API requests.
"""

import json
import platform

import requests
from . import __version__, exceptions, models, API_CONFIG, DEFAULT_API_VERSION


class API(object):
    """Class which handles requests to the Infermedica API."""

    # User-Agent for HTTP request
    library_details = "requests %s; python %s" % (requests.__version__, platform.python_version())
    user_agent = "Infermedica-API-Python %s (%s)" % (__version__, library_details)

    def __init__(self, **kwargs):
        """
        Initialize API object.

        Usage::
            >>> import infermedica_api
            >>> api = infermedica_api.API(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
        """
        self.api_version = kwargs.get("api_version", DEFAULT_API_VERSION)
        self.app_id = kwargs["app_id"]  # Mandatory parameter, so not using `dict.get`
        self.app_key = kwargs["app_key"]  # Mandatory parameter, so not using `dict.get`

        self.endpoint = API_CONFIG[self.api_version]['endpoint']
        self.api_methods = API_CONFIG[self.api_version]['methods']

    def __get_url(self, method):
        return self.endpoint + self.api_version + method

    def __get_headers(self, override):
        """Returns default HTTP headers."""

        return dict({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "app_id": self.app_id,
            "app_key": self.app_key
        }, **override)

    def __api_call(self, url, method, **kwargs):

        kwargs['headers'] = self.__get_headers(kwargs['headers'] or {})

        response = requests.request(method, url, **kwargs)

        return self.__handle_response(response)

    def __handle_response(self, response):
        """
        Validates HTTP response, if response is correct decode json data and returns dict object.
        If response is not correct raise appropriate exception.

        :returns: dict or list with response data
        :rtype: dict or list
        :raises:
            infermedica_api.exceptions.BadRequest,
            infermedica_api.exceptions.UnauthorizedAccess,
            infermedica_api.exceptions.ForbiddenAccess,
            infermedica_api.exceptions.ResourceNotFound,
            infermedica_api.exceptions.MethodNotAllowed,
            infermedica_api.exceptions.ServerError,
            infermedica_api.exceptions.ConnectionError
        """
        status = response.status_code
        content = response.content.decode('utf-8')

        if 200 <= status <= 299:
            return json.loads(content) if content else {}
        elif status == 400:
            raise exceptions.BadRequest(response, content)
        elif status == 401:
            raise exceptions.UnauthorizedAccess(response, content)
        elif status == 403:
            raise exceptions.ForbiddenAccess(response, content)
        elif status == 404:
            raise exceptions.ResourceNotFound(response, content)
        elif status == 405:
            raise exceptions.MethodNotAllowed(response, content)
        elif 500 <= status <= 599:
            raise exceptions.ServerError(response, content)
        else:
            raise exceptions.ConnectionError(response, content)

    def __get(self, method, params=None, headers=None):
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "GET", headers=headers, params=params)

    def __post(self, method, data, headers=None):
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "POST", headers=headers, data=data)

    def info(self):
        """Makes an API request and returns basic API model information."""
        try:
            return self.__get(self.api_methods['info'])
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'info')

    def diagnosis(self, diagnosis_request):
        """
        Makes an diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A Diagnosis object with api response
        :rtype: :class:`infermedica_api.models.Diagnosis`
        """
        try:
            if isinstance(diagnosis_request, models.Diagnosis):
                response = self.__post(self.api_methods['diagnosis'], json.dumps(diagnosis_request.get_api_request()))
                diagnosis_request.update_from_api(response)

                return diagnosis_request

            return self.__post(self.api_methods['diagnosis'], json.dumps(diagnosis_request))
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'diagnosis')

    def observation_details(self, _id):
        """
        Makes an API request and returns observation details object.

        :param _id: Observation id
        :type _id: str

        :returns: A Observation object
        :rtype: :class:`infermedica_api.models.Observation`
        """
        try:
            url = self.api_methods['observation_details'].format(**{'id': _id})
            response = self.__get(url)
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'observation_details')

        return models.Observation.from_json(response)

    def observations_list(self):
        """
        Makes an API request and returns list of observation details objects.

        :returns: A ObservationList list object with Observation objects
        :rtype: :class:`infermedica_api.models.ObservationList`
        """
        try:
            response = self.__get(self.api_methods['observations'])
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'observations_list')

        return models.ObservationList.from_json(response)

    def condition_details(self, _id):
        """
        Makes an API request and returns condition details object.

        :param _id: Condition id
        :type _id: str

        :returns:A Condition object
        :rtype: :class:`infermedica_api.models.Condition`
        """
        try:
            url = self.api_methods['condition_details'].format(**{'id': _id})
            response = self.__get(url)
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'condition_details')

        return models.Condition.from_json(response)

    def conditions_list(self):
        """
        Makes an API request and returns list of condition details objects.

        :returns: A ConditionList list object with Condition objects
        :rtype: :class:`infermedica_api.models.ConditionList`
        """
        try:
            response = self.__get(self.api_methods['conditions'])
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'conditions_list')

        return models.ConditionList.from_json(response)

    def risk_factor_details(self, _id):
        """
        Makes an API request and returns risk factor details object.

        :param _id: risk factor id
        :type _id: str

        :returns: A RiskFactor object
        :rtype: :class:`infermedica_api.models.RiskFactor`
        """
        try:
            url = self.api_methods['risk_factor_details'].format(**{'id': _id})
            response = self.__get(url)
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'risk_factor_details')

        return models.RiskFactor.from_json(response)

    def risk_factors_list(self):
        """
        Makes an API request and returns list of risk factors details objects.

        :returns: A RiskFactorList list object with RiskFactor objects
        :rtype: :class:`infermedica_api.models.RiskFactorList`
        """
        try:
            response = self.__get(self.api_methods['risk_factors'])
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, 'risk_factors_list')

        return models.RiskFactorList.from_json(response)


__api__ = None


def get_api():
    """
    Returns global API object and if present,
    otherwise raise MissingConfiguration exception.

    :returns: An API object
    :rtype: :class:`infermedica_api.webservice.API`
    :raises: :class:`infermedica_api.exceptions.MissingConfiguration`
    """
    global __api__

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
    __api__ = API(**dict(options or {}, **config))

    return __api__
