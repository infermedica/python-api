# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.common
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains base a set of API Connector classes responsible for making API requests.
"""

import json
import platform
from abc import ABC
from enum import Enum
from typing import Optional, Dict, Union, List, Any

import requests

from .. import (
    __version__,
    exceptions,
    API_CONFIG,
    DEFAULT_API_VERSION,
    DEFAULT_API_ENDPOINT,
)

ConditionDetails = Dict[str, Any]
SymptomDetails = Dict[str, Any]
RiskFactorDetails = Dict[str, Any]
LabTestDetails = Dict[str, Any]
ConceptDetails = Dict[str, Any]

EvidenceList = List[Dict[str, str]]
ExtrasDict = Dict[str, Union[bool, str]]


class SearchConceptType(Enum):
    """Enum to hold search filter constants."""

    SYMPTOM = "symptom"
    RISK_FACTOR = "risk_factor"
    LAB_TEST = "lab_test"

    @staticmethod
    def has_value(val: Union["SearchConceptType", str]) -> bool:
        try:
            return val in SearchConceptType
        except TypeError:
            return val in (item.value for item in SearchConceptType)

    @staticmethod
    def get_value(val: Union["SearchConceptType", str]) -> str:
        if isinstance(val, SearchConceptType):
            return val.value
        return val


class BaseAPIConnector(ABC):
    """Low level class which handles requests to the Infermedica API, works with row objects."""

    def __init__(
        self,
        app_id: str,
        app_key: str,
        endpoint: Optional[str] = DEFAULT_API_ENDPOINT,
        api_version: Optional[str] = DEFAULT_API_VERSION,
        model: Optional[str] = None,
        dev_mode: Optional[bool] = None,
        default_headers: Optional[Dict] = None,
        api_definitions: Optional[Dict] = None,
    ) -> None:
        """
        Initialize API connector.

        :param app_id: Infermedica API App Id
        :param app_key: Infermedica API App Key
        :param endpoint: (optional) Base API URL, default is 'https://api.infermedica.com/'
        :param api_version: (optional) API version, default is 'v3'
        :param model: (optional) API model to be used
        :param dev_mode: (optional) Flag that indicates request is made in testing environment
                         and does not provide real patient case
        :param default_headers: (optional) Dict with default headers that will be send with every request
        :param api_definitions: (optional) Dict with custom API method definitions

        :raises: infermedica_api.exceptions.MissingAPIDefinition
        """
        self.app_id = app_id
        self.app_key = app_key
        self.endpoint = endpoint
        self.api_version = api_version
        self.default_headers = self.__calculate_default_headers(
            model=model, dev_mode=dev_mode, default_headers=default_headers
        )

        if api_definitions and self.api_version in api_definitions:
            self.api_methods = api_definitions[self.api_version]["methods"]
        elif self.api_version in API_CONFIG:
            self.api_methods = API_CONFIG[self.api_version]["methods"]
        else:
            raise exceptions.MissingAPIDefinition(self.api_version)

    def __calculate_default_headers(
        self,
        model: Optional[str] = None,
        dev_mode: Optional[bool] = None,
        default_headers: Optional[Dict] = None,
    ) -> Dict:
        headers = default_headers or {}

        if model:
            headers["Model"] = model

        if dev_mode:
            headers["Dev-Mode"] = "true"

        return headers

    def __get_headers(self, passed_headers: Dict) -> Dict:
        """Returns default HTTP headers."""

        # User-Agent for HTTP request
        library_details = [
            f"requests {requests.__version__}",
            f"python {platform.python_version()}",
            f"connector {self.__class__.__name__}",
        ]
        library_details = "; ".join(library_details)
        user_agent = f"Infermedica-API-Python {__version__} ({library_details})"

        headers = {
            "Accept": "application/json",
            "User-Agent": user_agent,
            "App-Id": self.app_id,
            "App-Key": self.app_key,
        }
        headers.update(self.default_headers)
        headers.update(passed_headers)  # Make sure passed headers take precedence
        return headers

    def get_interview_id_headers(self, interview_id: Optional[str] = None) -> Dict:
        headers = {}
        if interview_id:
            headers["Interview-Id"] = interview_id

        return headers

    def __get_url(self, method: str) -> str:
        return self.endpoint + self.api_version + method

    def _get_method(self, name: str) -> str:
        try:
            return self.api_methods[name]
        except KeyError:
            raise exceptions.MethodNotAvailableInAPIVersion(self.api_version, name)

    def __api_call(self, url: str, method: str, **kwargs: Any) -> Union[Dict, List]:
        kwargs["headers"] = self.__get_headers(kwargs["headers"] or {})

        response = requests.request(method, url, **kwargs)

        return self.__handle_response(response)

    def __handle_response(self, response: requests.Response) -> Union[Dict, List]:
        """
        Validates HTTP response, if response is correct decode json data and returns dict object.
        If response is not correct raise appropriate exception.

        :returns: dict or list with response data
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
        content = response.content.decode("utf-8")

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

    def call_api_get(
        self, method: str, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Union[Dict, List]:
        """Wrapper for a GET API call."""
        return self.__api_call(
            self.__get_url(method), "GET", headers=headers, params=params
        )

    def call_api_post(
        self,
        method: str,
        data: Dict,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Union[Dict, List]:
        """Wrapper for a GET API call."""
        return self.__api_call(
            self.__get_url(method), "POST", headers=headers, json=data, params=params
        )


# Common API functionalities


class BasicAPIInfoMixin(ABC):
    def info(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes an API request and returns basic API information.
        See the docs: https://developer.infermedica.com/docs/v3/basics#info-endpoint.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("info")

        return self.call_api_get(method=method, params=params, headers=headers)


class BasicAPISearchMixin(ABC):
    def search(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A List of dicts with 'id' and 'label' keys
        """
        method = self._get_method("search")

        return self.call_api_get(method=method, params=params, headers=headers)


class BasicAPIParseMixin(ABC):
    def parse(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.
        See the docs: https://developer.infermedica.com/docs/v3/nlp.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("parse")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )


class BasicAPISuggestMixin(ABC):
    def suggest(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.
        See the docs: https://developer.infermedica.com/docs/v3/suggest-related-concepts.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        method = self._get_method("suggest")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )


class BasicAPIDiagnosisMixin(ABC):
    def diagnosis(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.
        See the docs: https://developer.infermedica.com/docs/v3/diagnosis.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("diagnosis")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )


class BasicAPIRationaleMixin(ABC):
    def rationale(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes an API request with provided diagnosis data and returns
        an explanation of why the given question has been selected by
        the reasoning engine.
        See the docs: https://developer.infermedica.com/docs/v3/rationale.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("rationale")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )


class BasicAPIExplainMixin(ABC):
    def explain(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidence.
        See the docs: https://developer.infermedica.com/docs/v3/explain.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("explain")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )


class BasicAPITriageMixin(ABC):
    def triage(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/v3/triage.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("triage")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )


class BasicAPIConditionMixin(ABC):
    def condition_details(
        self,
        condition_id: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> ConditionDetails:
        """
        Makes an API request and returns condition details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#conditions.

        :param condition_id: Condition id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with condition details
        """
        method = self._get_method("condition_details")
        method = method.format(**{"id": condition_id})

        return self.call_api_get(method=method, params=params, headers=headers)

    def condition_list(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[ConditionDetails]:
        """
        Makes an API request and returns list of condition details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#conditions.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with condition details
        """
        method = self._get_method("conditions")

        return self.call_api_get(method=method, params=params, headers=headers)


class BasicAPISymptomMixin(ABC):
    def symptom_details(
        self,
        symptom_id: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> SymptomDetails:
        """
        Makes an API request and returns symptom details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#symptoms.

        :param symptom_id: Symptom id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with symptom details
        """
        method = self._get_method("symptom_details")
        method = method.format(**{"id": symptom_id})

        return self.call_api_get(method=method, params=params, headers=headers)

    def symptom_list(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[SymptomDetails]:
        """
        Makes an API request and returns list of symptom details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#symptoms.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with symptom details
        """
        method = self._get_method("symptoms")

        return self.call_api_get(method=method, params=params, headers=headers)


class BasicAPIRiskFactorMixin(ABC):
    def risk_factor_details(
        self,
        risk_factor_id: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> RiskFactorDetails:
        """
        Makes an API request and returns risk factor details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#risk-factors.

        :param risk_factor_id: risk factor id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with risk factor details
        """
        method = self._get_method("risk_factor_details")
        method = method.format(**{"id": risk_factor_id})

        return self.call_api_get(method=method, params=params, headers=headers)

    def risk_factor_list(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[RiskFactorDetails]:
        """
        Makes an API request and returns list of risk factors details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#risk-factors.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with risk factor details
        """
        method = self._get_method("risk_factors")

        return self.call_api_get(method=method, params=params, headers=headers)


class BasicAPILabTestMixin(ABC):
    def lab_test_details(
        self,
        lab_test_id: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> LabTestDetails:
        """
        Makes an API request and returns lab test details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#lab-tests-and-lab-test-results.

        :param lab_test_id: LabTest id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with lab test details
        """
        method = self._get_method("lab_test_details")
        method = method.format(**{"id": lab_test_id})

        return self.call_api_get(method=method, params=params, headers=headers)

    def lab_test_list(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[LabTestDetails]:
        """
        Makes an API request and returns list of lab test details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#lab-tests-and-lab-test-results.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with lab test details
        """
        method = self._get_method("lab_tests")

        return self.call_api_get(method=method, params=params, headers=headers)


class BasicAPICommonMethodsMixin(
    BasicAPIInfoMixin,
    BasicAPISearchMixin,
    BasicAPIParseMixin,
    BasicAPISuggestMixin,
    BasicAPIDiagnosisMixin,
    BasicAPIRationaleMixin,
    BasicAPIExplainMixin,
    BasicAPITriageMixin,
    BasicAPIConditionMixin,
    BasicAPISymptomMixin,
    BasicAPIRiskFactorMixin,
    BasicAPILabTestMixin,
    ABC,
):
    pass
