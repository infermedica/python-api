# -*- coding: utf-8 -*-

"""
infermedica_api.webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains classes and function responsible for making API requests.
"""

import json
import platform

import requests

from .. import __version__, exceptions, API_CONFIG, DEFAULT_API_VERSION, DEFAULT_API_ENDPOINT


class SearchFilters:
    """Simple class to hold search filter constants."""
    SYMPTOMS = "symptom"
    RISK_FACTORS = "risk_factor"
    LAB_TESTS = "lab_test"

    ALL = [SYMPTOMS, RISK_FACTORS, LAB_TESTS]


SEARCH_FILTERS = SearchFilters()


class APIConnector:
    """Class which handles requests to the Infermedica API."""

    def __init__(self, app_id, app_key, endpoint=DEFAULT_API_ENDPOINT, api_version=DEFAULT_API_VERSION,
                 model=None, dev_mode=None, default_headers=None, api_definitions=None):
        """
        Initialize API object.

        Usage::
            >>> import infermedica_api
            >>> api = infermedica_api.APIConnector(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
        """
        self.app_id = app_id
        self.app_key = app_key
        self.endpoint = endpoint
        self.api_version = api_version
        self.default_headers = self.__calculate_default_headers(
            model=model,
            dev_mode=dev_mode,
            default_headers=default_headers
        )

        if api_definitions and self.api_version in api_definitions:
            self.api_methods = api_definitions[self.api_version]['methods']
        elif self.api_version in API_CONFIG:
            self.api_methods = API_CONFIG[self.api_version]['methods']
        else:
            pass
            # TODO: Raise exception
            # self.api_methods = API_CONFIG[DEFAULT_API_VERSION]['methods']

    def __calculate_default_headers(self, model=None, dev_mode=None, default_headers=None):
        headers = default_headers or {}
        if model:
            headers["Model"] = model

        if dev_mode == True:
            headers["Dev-Mode"] = "true"

        return headers

    def __get_url(self, method):
        return self.endpoint + self.api_version + method

    def __get_headers(self, override):
        """Returns default HTTP headers."""

        # User-Agent for HTTP request
        library_details = [
            f"requests {requests.__version__}",
            f"python {platform.python_version()}",
            f"connector {self.__class__.__name__}"
        ]
        library_details = "; ".join(library_details)
        user_agent = f"Infermedica-API-Python {__version__} ({library_details})"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": user_agent,
            "App-Id": self.app_id,
            "App-Key": self.app_key
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

    def call_api_get(self, method, params=None, headers=None):
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "GET", headers=headers, params=params)

    def call_api_post(self, method, data, params=None, headers=None):
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "POST", headers=headers, data=data, params=params)

    def __get_method(self, name):
        try:
            return self.api_methods[name]
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, name)

    def __get_interview_id_headers(self, interview_id=None):
        headers = {}
        if interview_id:
            headers['Interview-Id'] = interview_id

        return headers

    # API Common Methods

    def info(self, params=None, headers=None):
        """Makes an API request and returns basic API model information."""
        method = self.__get_method('info')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def search(self, params=None, headers=None):
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param params: Search method params.
        :type params: dict

        :returns: A List of dicts with 'id' and 'label' keys.
        :rtype: list
        """
        method = self.__get_method('search')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def parse(self, data, interview_id=None, params=None, headers=None):
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
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def suggest(self, data, interview_id=None, params=None, headers=None):
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A list of suggestions, dicts with 'id', 'name' and 'common_name' keys.
        :rtype: list
        """
        method = self.__get_method('suggest')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def red_flags(self, data, interview_id=None, params=None, headers=None):
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.

        :param diagnosis_request: Diagnosis request object or diagnosis json.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :param interview_id: Unique interview id for diagnosis
        :type interview_id: str

        :returns: A list of RedFlag objects
        :rtype: :class:`infermedica_api.models.RedFlagList`
        """
        method = self.__get_method('red_flags')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def diagnosis(self, data, interview_id=None, params=None, headers=None):
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
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def explain(self, data, interview_id=None, params=None, headers=None):
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
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def triage(self, data, interview_id=None, params=None, headers=None):
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
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def rationale(self, data, interview_id=None, params=None, headers=None):
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
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=json.dumps(data),
            params=params,
            headers=headers
        )

    def condition_details(self, condition_id, params=None, headers=None):
        """
        Makes an API request and returns condition details object.

        :param condition_id: Condition id
        :type condition_id: str

        :returns:A Condition object
        :rtype: :class:`infermedica_api.models.Condition`
        """
        method = self.__get_method('condition_details')
        method = method.format(**{'id': condition_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def conditions_list(self, params=None, headers=None):
        """
        Makes an API request and returns list of condition details objects.

        :returns: A ConditionList list object with Condition objects
        :rtype: :class:`infermedica_api.models.ConditionList`
        """
        method = self.__get_method('conditions')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def symptom_details(self, symptom_id, params=None, headers=None):
        """
        Makes an API request and returns symptom details object.

        :param _id: Symptom id
        :type _id: str

        :returns: A Symptom object
        :rtype: :class:`infermedica_api.models.Symptom`
        """
        method = self.__get_method('symptom_details')
        method = method.format(**{'id': symptom_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def symptoms_list(self, params=None, headers=None):
        """
        Makes an API request and returns list of symptom details objects.

        :returns: A SymptomList list object with Symptom objects
        :rtype: :class:`infermedica_api.models.SymptomList`
        """
        method = self.__get_method('symptoms')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def risk_factor_details(self, risk_factor_id, params=None, headers=None):
        """
        Makes an API request and returns risk factor details object.

        :param _id: risk factor id
        :type _id: str

        :returns: A RiskFactor object
        :rtype: :class:`infermedica_api.models.RiskFactor`
        """
        method = self.__get_method('risk_factor_details')
        method = method.format(**{'id': risk_factor_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def risk_factors_list(self, params=None, headers=None):
        """
        Makes an API request and returns list of risk factors details objects.

        :returns: A RiskFactorList list object with RiskFactor objects
        :rtype: :class:`infermedica_api.models.RiskFactorList`
        """
        method = self.__get_method('risk_factors')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def lab_test_details(self, lab_test_id, params=None, headers=None):
        """
        Makes an API request and returns lab_test details object.

        :param _id: LabTest id
        :type _id: str

        :returns: A LabTest object
        :rtype: :class:`infermedica_api.models.LabTest`
        """
        method = self.__get_method('lab_test_details')
        method = method.format(**{'id': lab_test_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def lab_tests_list(self, params=None, headers=None):
        """
        Makes an API request and returns list of lab_test details objects.

        :returns: A LabTestList list object with LabTest objects
        :rtype: :class:`infermedica_api.models.LabTestList`
        """
        method = self.__get_method('lab_tests')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    # TODO: Add /concepts methods
