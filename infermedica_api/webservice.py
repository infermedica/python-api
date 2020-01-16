# -*- coding: utf-8 -*-

"""
infermedica_api.webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains classes and function responsible for making API requests.
"""

import json
import platform
import warnings

import requests

from . import __version__, exceptions, models, API_CONFIG, DEFAULT_API_VERSION, DEFAULT_API_ENDPOINT

if platform.python_version_tuple()[0] == '3':
    basestring = (str, bytes)


class SearchFilters(object):
    """Simple class to hold search filter constants."""
    SYMPTOMS = "symptom"
    RISK_FACTORS = "risk_factor"
    LAB_TESTS = "lab_test"

    ALL = [SYMPTOMS, RISK_FACTORS, LAB_TESTS]


SEARCH_FILTERS = SearchFilters()


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
        self.endpoint = kwargs.get("endpoint", DEFAULT_API_ENDPOINT)
        self.api_version = kwargs.get("api_version", DEFAULT_API_VERSION)
        self.app_id = kwargs["app_id"]  # Mandatory parameter, so not using `dict.get`
        self.app_key = kwargs["app_key"]  # Mandatory parameter, so not using `dict.get`
        self.default_headers = self.__calculate_headers(kwargs)

        if self.api_version in kwargs.get("api_definitions", {}) or {}:
            self.api_methods = kwargs["api_definitions"][self.api_version]['methods']
        elif self.api_version in API_CONFIG:
            self.api_methods = API_CONFIG[self.api_version]['methods']
        else:
            self.api_methods = API_CONFIG[DEFAULT_API_VERSION]['methods']

    def __calculate_headers(self, parameters):
        headers = parameters.get("default_headers", {})
        if parameters.get("model", None):
            headers.update({
                "Model": parameters["model"]
            })

        if parameters.get("dev_mode", None) and parameters["dev_mode"] == True:
            headers.update({
                "Dev-Mode": "true"
            })

        return headers

    def __get_url(self, method):
        return self.endpoint + self.api_version + method

    def __get_headers(self, override):
        """Returns default HTTP headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "app_id": self.app_id,
            "app_key": self.app_key
        }
        headers.update(self.default_headers)
        headers.update(override)
        return headers

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

    def __post(self, method, data, params=None, headers=None):
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "POST", headers=headers, data=data, params=params)

    def __get_method(self, name):
        try:
            return self.api_methods[name]
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, name)

    def __get_interview_id_headers(self, diagnosis_request=None, interview_id=None):
        headers = {}
        if interview_id:
            headers['Interview-Id'] = interview_id
        elif isinstance(diagnosis_request, models.Diagnosis) and diagnosis_request.interview_id:
            headers['Interview-Id'] = diagnosis_request.interview_id

        return headers

    def info(self):
        """Makes an API request and returns basic API model information."""
        return self.__get(self.__get_method('info'))

    def search(self, phrase, sex=None, max_results=8, filters=None, **kwargs):
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param phrase: Phrase to look for.
        :type phrase: str

        :param sex: Sex of the patient 'female' or 'male'.
        :type sex: str

        :param max_results: Maximum number of result to return, default is 8.
        :type max_results: int

        :param filters: List of search filters, taken from SEARCH_FILTERS variable.
        :type filters: list

        :returns: A List of dicts with 'id' and 'label' keys.
        :rtype: list
        """
        method = self.__get_method('search')
        params = {
            'phrase': phrase,
            'max_results': max_results
        }
        params.update(kwargs.get('params', {}))

        if sex:
            params['sex'] = sex

        if filters:
            if isinstance(filters, (list, tuple)):
                params['type'] = filters
            elif isinstance(filters, basestring):
                params['type'] = [filters]

            for filter in params['type']:
                if filter not in SEARCH_FILTERS.ALL:
                    raise exceptions.InvalidSearchFilter(filter)

        return self.__get(method, params=params)

    def lookup(self, phrase, sex=None):
        """
        Makes an API lookup request and returns evidence details object.

        :param phrase: Phrase to look for.
        :type phrase: str

        :param sex: Sex of the patient 'female' or 'male'.
        :type sex: str

        :returns: Dictionary with details.
        :rtype: dict
        """
        method = self.__get_method('lookup')

        params = {
            'phrase': phrase
        }
        if sex:
            params['sex'] = sex

        return self.__get(method, params=params)

    def suggest(self, diagnosis_request, max_results=8, interview_id=None):
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A list of suggestions, dicts with 'id', 'name' and 'common_name' keys.
        :rtype: list
        """
        method = self.__get_method('suggest')
        headers = self.__get_interview_id_headers(interview_id=interview_id)

        request = diagnosis_request
        if isinstance(diagnosis_request, models.Diagnosis):
            request = diagnosis_request.get_api_request()

        return self.__post(method, headers=headers, data=json.dumps(request), params={'max_results': max_results})

    def parse(self, text, include_tokens=False, interview_id=None):
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.

        :param phrase: Text to parse.
        :type phrase: str

        :param include_tokens: Switch to manipulate the include_tokens parameter.
        :type include_tokens: bool

        :returns: A ParseResults object
        :rtype: :class:`infermedica_api.models.ParseResults`
        """
        method = self.__get_method('parse')
        headers = self.__get_interview_id_headers(interview_id=interview_id)

        request = {
            'text': text,
            'include_tokens': include_tokens
        }

        response = self.__post(method, json.dumps(request), headers=headers)

        return models.ParseResults.from_json(response)

    def diagnosis(self, diagnosis_request, interview_id=None, **kwargs):
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :param interview_id: Unique interview id for diagnosis
        :type interview_id: str

        :returns: A Diagnosis object with api response
        :rtype: :class:`infermedica_api.models.Diagnosis`
        """
        method = self.__get_method('diagnosis')

        if kwargs.get('case_id', None) is not None:
            warnings.warn("Parameter case_id is deprecated, please use interview_id.",
                          category=DeprecationWarning)

        headers = self.__get_interview_id_headers(
            diagnosis_request=diagnosis_request, interview_id=interview_id or kwargs.get('case_id', None))

        if isinstance(diagnosis_request, models.Diagnosis):
            response = self.__post(method, json.dumps(diagnosis_request.get_api_request()), headers=headers)
            diagnosis_request.update_from_api(response)

            return diagnosis_request

        return self.__post(method, json.dumps(diagnosis_request), headers=headers)

    def explain(self, diagnosis_request, target_id, interview_id=None):
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidences.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :param target_id: Condition id for which explain shall be calculated.
        :type target_id: str

        :returns: A Diagnosis object with api response
        :rtype: :class:`infermedica_api.models.Diagnosis`
        """
        method = self.__get_method('explain')
        headers = self.__get_interview_id_headers(diagnosis_request=diagnosis_request, interview_id=interview_id)

        if isinstance(diagnosis_request, models.Diagnosis):
            request = diagnosis_request.get_explain_request(target_id)
        else:
            request = dict(diagnosis_request, **{'target': target_id})

        response = self.__post(method, json.dumps(request), headers=headers)

        return models.ExplainResults.from_json(response)

    def triage(self, diagnosis_request, interview_id=None):
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/triage.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A dict object with api response
        :rtype: dict
        """
        method = self.__get_method('triage')
        headers = self.__get_interview_id_headers(diagnosis_request=diagnosis_request, interview_id=interview_id)

        request = diagnosis_request
        if isinstance(diagnosis_request, models.Diagnosis):
            request = diagnosis_request.get_api_request()

        return self.__post(method, json.dumps(request), headers=headers)

    def observation_details(self, _id):
        """
        Makes an API request and returns observation details object.

        :param _id: Observation id
        :type _id: str

        :returns: A Observation object
        :rtype: :class:`infermedica_api.models.Observation`
        """
        method = self.__get_method('observation_details')
        response = self.__get(method.format(**{'id': _id}))

        return models.Observation.from_json(response)

    def observations_list(self):
        """
        Makes an API request and returns list of observation details objects.

        :returns: A ObservationList list object with Observation objects
        :rtype: :class:`infermedica_api.models.ObservationList`
        """
        response = self.__get(self.__get_method('observations'))

        return models.ObservationList.from_json(response)

    def condition_details(self, _id):
        """
        Makes an API request and returns condition details object.

        :param _id: Condition id
        :type _id: str

        :returns:A Condition object
        :rtype: :class:`infermedica_api.models.Condition`
        """
        method = self.__get_method('condition_details')
        response = self.__get(method.format(**{'id': _id}))

        return models.Condition.from_json(response)

    def conditions_list(self):
        """
        Makes an API request and returns list of condition details objects.

        :returns: A ConditionList list object with Condition objects
        :rtype: :class:`infermedica_api.models.ConditionList`
        """
        response = self.__get(self.__get_method('conditions'))

        return models.ConditionList.from_json(response)

    def symptom_details(self, _id):
        """
        Makes an API request and returns symptom details object.

        :param _id: Symptom id
        :type _id: str

        :returns: A Symptom object
        :rtype: :class:`infermedica_api.models.Symptom`
        """
        method = self.__get_method('symptom_details')
        response = self.__get(method.format(**{'id': _id}))

        return models.Symptom.from_json(response)

    def symptoms_list(self):
        """
        Makes an API request and returns list of symptom details objects.

        :returns: A SymptomList list object with Symptom objects
        :rtype: :class:`infermedica_api.models.SymptomList`
        """
        response = self.__get(self.__get_method('symptoms'))

        return models.SymptomList.from_json(response)

    def lab_test_details(self, _id):
        """
        Makes an API request and returns lab_test details object.

        :param _id: LabTest id
        :type _id: str

        :returns: A LabTest object
        :rtype: :class:`infermedica_api.models.LabTest`
        """
        method = self.__get_method('lab_test_details')
        response = self.__get(method.format(**{'id': _id}))

        return models.LabTest.from_json(response)

    def lab_tests_list(self):
        """
        Makes an API request and returns list of lab_test details objects.

        :returns: A LabTestList list object with LabTest objects
        :rtype: :class:`infermedica_api.models.LabTestList`
        """
        response = self.__get(self.__get_method('lab_tests'))

        return models.LabTestList.from_json(response)

    def risk_factor_details(self, _id):
        """
        Makes an API request and returns risk factor details object.

        :param _id: risk factor id
        :type _id: str

        :returns: A RiskFactor object
        :rtype: :class:`infermedica_api.models.RiskFactor`
        """
        method = self.__get_method('risk_factor_details')
        response = self.__get(method.format(**{'id': _id}))

        return models.RiskFactor.from_json(response)

    def risk_factors_list(self):
        """
        Makes an API request and returns list of risk factors details objects.

        :returns: A RiskFactorList list object with RiskFactor objects
        :rtype: :class:`infermedica_api.models.RiskFactorList`
        """
        response = self.__get(self.__get_method('risk_factors'))

        return models.RiskFactorList.from_json(response)

    def red_flags(self, diagnosis_request, max_results=8, interview_id=None):
        """
        Makes an API request with provided diagnosis data and returns a list
        of observations that may be related to potentially life-threatening
        conditions.

        :param diagnosis_request: Diagnosis request object or diagnosis json.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :param interview_id: Unique interview id for diagnosis
        :type interview_id: str

        :returns: A list of RedFlag objects
        :rtype: :class:`infermedica_api.models.RedFlagList`
        """
        method = self.__get_method('red_flags')
        headers = self.__get_interview_id_headers(
            diagnosis_request=diagnosis_request,
            interview_id=interview_id,
        )

        request = diagnosis_request
        if isinstance(diagnosis_request, models.Diagnosis):
            request = diagnosis_request.get_api_request()

        response = self.__post(method, json.dumps(request), headers=headers, params={'max_results': max_results})

        return models.RedFlagList.from_json(response)

    def rationale(self, diagnosis_request, interview_id=None):
        """
        Makes an API request with provided diagnosis data and returns
        an explenation of why the given question has been selected by
        the reasoning engine.

        :param diagnosis_request: Diagnosis request object or diagnosis json.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :param interview_id: Unique interview id for diagnosis
        :type interview_id: str

        :returns: An instance of the RationaleResult
        :rtype: :class:`infermedica_api.models.RationaleResult`
        """
        method = self.__get_method('rationale')
        headers = self.__get_interview_id_headers(
            diagnosis_request=diagnosis_request,
            interview_id=interview_id,
        )

        request = diagnosis_request
        if isinstance(diagnosis_request, models.Diagnosis):
            request = diagnosis_request.get_api_request()

        response = self.__post(method, json.dumps(request), headers=headers)

        return models.RationaleResult.from_json(response)


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

    if isinstance(alias, basestring):
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

    if 'alias' in configuration and isinstance(configuration['alias'], basestring):
        __api_aliased__[configuration['alias']] = API(**configuration)

        if configuration.get('default', False):
            __api__ = __api_aliased__[configuration['alias']]

        return __api_aliased__[configuration['alias']]

    __api__ = API(**configuration)

    return __api__
