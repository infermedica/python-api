# -*- coding: utf-8 -*-

"""
infermedica_api.webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains classes and function responsible for making API requests.
"""

import json
import platform
from typing import Optional, Dict, Union, List

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
    """Low level class which handles requests to the Infermedica API, works with row objects."""

    def __init__(self, app_id: str, app_key: str, endpoint: Optional[str] = DEFAULT_API_ENDPOINT,
                 api_version: Optional[str] = DEFAULT_API_VERSION, model: Optional[str] = None,
                 dev_mode: Optional[bool] = None, default_headers: Optional[Dict] = None,
                 api_definitions: Optional[Dict] = None) -> None:
        """
        Initialize API connector.

        :param app_id: Infermedica API App Id
        :param app_Key: Infermedica API App Key
        :param endpoint: (optional) Base API URL, default is 'https://api.infermedica.com/'
        :param api_version: (optional) API version, default is 'v2'
        :param model: (optional) API model to be used
        :param dev_mode: (optional) Flag that indicates request is made in testing environment
                         and does not provide real patient case
        :param default_headers: (optional) Dict with default headers that will be send with every request
        :param api_definitions: (optional) Dict with custom API method definitions

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

    def __calculate_default_headers(self, model: Optional[str] = None, dev_mode: Optional[bool] = None,
                                    default_headers: Optional[Dict] = None) -> Dict:
        headers = default_headers or {}

        if model:
            headers["Model"] = model

        if dev_mode == True:
            headers["Dev-Mode"] = "true"

        return headers

    def __get_url(self, method: str) -> str:
        return self.endpoint + self.api_version + method

    def __get_headers(self, passed_headers: Dict) -> Dict:
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
            "Accept": "application/json",
            "User-Agent": user_agent,
            "App-Id": self.app_id,
            "App-Key": self.app_key
        }
        headers.update(self.default_headers)
        headers.update(passed_headers)  # Make sure passed headers take precedence
        return headers

    def __api_call(self, url: str, method: str, **kwargs: Dict) -> Union[Dict, List]:
        kwargs['headers'] = self.__get_headers(kwargs['headers'] or {})

        response = requests.request(method, url, **kwargs)

        return self.__handle_response(response)

    def __handle_response(self, response: requests.Response) -> Union[Dict, List]:
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

    def call_api_get(self, method: str, params: Optional[Dict] = None,
                     headers: Optional[Dict] = None) -> Union[Dict, List]:
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "GET", headers=headers, params=params)

    def call_api_post(self, method: str, data: Dict, params: Optional[Dict] = None,
                      headers: Optional[Dict] = None) -> Union[Dict, List]:
        """Wrapper for a GET API call."""
        return self.__api_call(self.__get_url(method), "POST", headers=headers, json=data, params=params)

    def __get_method(self, name: str) -> str:
        try:
            return self.api_methods[name]
        except KeyError as e:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, name)

    def __get_interview_id_headers(self, interview_id: Optional[str] = None) -> Dict:
        headers = {}
        if interview_id:
            headers['Interview-Id'] = interview_id

        return headers

    # API Common Methods

    def info(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request and returns basic API information.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('info')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def search(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A List of dicts with 'id' and 'label' keys
        """
        method = self.__get_method('search')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def parse(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
              headers: Optional[Dict] = None) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('parse')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def suggest(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
                headers: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        method = self.__get_method('suggest')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def red_flags(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
                  headers: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        method = self.__get_method('red_flags')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def diagnosis(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
                  headers: Optional[Dict] = None) -> Dict:
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('diagnosis')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def explain(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
                headers: Optional[Dict] = None) -> Dict:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidences.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('explain')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def triage(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
               headers: Optional[Dict] = None) -> Dict:
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/triage.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('triage')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def specialist_recommender(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
                               headers: Optional[Dict] = None) -> Dict:
        """
        Makes a specialist recommendation API request with provided diagnosis data.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('specialist_recommender')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def rationale(self, data: Dict, interview_id: Optional[str] = None, params: Optional[Dict] = None,
                  headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request with provided diagnosis data and returns
        an explanation of why the given question has been selected by
        the reasoning engine.

        :param data: Request data
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self.__get_method('rationale')
        if headers is None:
            headers = {}
        headers.update(self.__get_interview_id_headers(interview_id=interview_id))

        return self.call_api_post(
            method=method,
            data=data,
            params=params,
            headers=headers
        )

    def condition_details(self, condition_id: str, params: Optional[Dict] = None,
                          headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request and returns condition details object.

        :param condition_id: Condition id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with condition details
        """
        method = self.__get_method('condition_details')
        method = method.format(**{'id': condition_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def conditions_list(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> List[Dict]:
        """
        Makes an API request and returns list of condition details objects.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with condition details
        """
        method = self.__get_method('conditions')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def symptom_details(self, symptom_id: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request and returns symptom details object.

        :param symptom_id: Symptom id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with symptom details
        """
        method = self.__get_method('symptom_details')
        method = method.format(**{'id': symptom_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def symptoms_list(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> List[Dict]:
        """
        Makes an API request and returns list of symptom details objects.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with symptom details
        """
        method = self.__get_method('symptoms')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def risk_factor_details(self, risk_factor_id: str, params: Optional[Dict] = None,
                            headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request and returns risk factor details object.

        :param risk_factor_id: risk factor id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with risk factor details
        """
        method = self.__get_method('risk_factor_details')
        method = method.format(**{'id': risk_factor_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def risk_factors_list(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> List:
        """
        Makes an API request and returns list of risk factors details objects.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with risk factor details
        """
        method = self.__get_method('risk_factors')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def lab_test_details(self, lab_test_id: str, params: Optional[Dict] = None,
                         headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request and returns lab test details object.

        :param lab_test_id: LabTest id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with lab test details
        """
        method = self.__get_method('lab_test_details')
        method = method.format(**{'id': lab_test_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def lab_tests_list(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> List:
        """
        Makes an API request and returns list of lab test details objects.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with lab test details
        """
        method = self.__get_method('lab_tests')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def concept_details(self, concept_id: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        Makes an API request and returns concept details object.

        :param concept_id: Concept id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with concept details
        """
        method = self.__get_method('concept_details')
        method = method.format(**{'id': concept_id})

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )

    def concept_list(self, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> List:
        """
        Makes an API request and returns list of concept details objects.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with concept details
        """
        method = self.__get_method('concepts')

        return self.call_api_get(
            method=method,
            params=params,
            headers=headers
        )


class APISharedConnector(APIConnector):
    """
    Intermediate level API Connector with methods shared between different API versions (mostly v2 and v3).
    """

    def search(self, phrase: str, sex: Optional[str] = None, max_results: Optional[int] = 8,
               filters: Optional[List[str]] = None, **kwargs: Dict) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param phrase: Phrase to look for
        :param sex: (optional) Sex of the patient 'female' or 'male' to narrow results
        :param max_results: (optional) Maximum number of result to return, default is 8
        :param filters: (optional) List of search filters, taken from SEARCH_FILTERS variable
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A List of dicts with 'id' and 'label' keys

        :raises: :class:`infermedica_api.exceptions.InvalidSearchFilter`
        """
        params = kwargs.pop('params', {})
        params.update({
            'phrase': phrase,
            'max_results': max_results
        })

        if sex:
            params['sex'] = sex

        if filters:
            if isinstance(filters, (list, tuple)):
                params['type'] = filters
            elif isinstance(filters, str):
                params['type'] = [filters]

            for filter_type in params['type']:
                if filter_type not in SEARCH_FILTERS.ALL:
                    raise exceptions.InvalidSearchFilter(filter_type)

        return super().search(
            params=params,
            **kwargs
        )

    def parse(self, text: str, include_tokens: Optional[bool] = False, interview_id: Optional[str] = None,
              **kwargs: Dict) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.

        :param phrase: Text to parse
        :param include_tokens: (optional) Switch to manipulate the include_tokens parameter
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        params = kwargs.pop('params', {})
        data = kwargs.pop('data', {})
        data.update({
            'text': text,
            'include_tokens': include_tokens
        })

        return super().parse(
            data=data,
            params=params,
            interview_id=interview_id,
            **kwargs
        )

    def suggest(self, data: Dict, max_results: Optional[int] = 8, interview_id: Optional[str] = None,
                **kwargs: Dict) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param data: Diagnosis request data
        :param max_results: (optional) Maximum number of result to return, default is 8
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        params = kwargs.pop('params', {})
        params.update({'max_results': max_results})

        return super().suggest(
            data=data,
            params=params,
            interview_id=interview_id,
            **kwargs
        )

    def red_flags(self, data: Dict, max_results: Optional[int] = 8, interview_id: Optional[str] = None,
                  **kwargs: Dict) -> List[Dict[str, str]]:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.

        :param data: Diagnosis request data
        :param max_results: (optional) Maximum number of result to return, default is 8
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        params = kwargs.pop('params', {})
        params.update({'max_results': max_results})

        return super().red_flags(
            data=data,
            params=params,
            interview_id=interview_id,
            **kwargs
        )

    def explain(self, data: Dict, target_id: str, interview_id: Optional[str] = None, **kwargs: Dict) -> Dict:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidences.

        :param data: Diagnosis request data
        :param target_id: Condition id for which explain shall be calculated
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        data_with_target = dict(data, **{'target': target_id})

        return super().explain(
            data=data_with_target,
            interview_id=interview_id,
            **kwargs,
        )
