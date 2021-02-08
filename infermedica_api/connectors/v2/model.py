# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.v2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes for API v2 version.
"""

from typing import Optional, List, Dict, Any

from .standard import APIv2Connector
from . import models


class ModelAPIv2Connector(APIv2Connector):
    """
    High level class which handles requests to the Infermedica API,
    provides methods that operates on data models.
    """

    def suggest(
        self,
        diagnosis_request: models.Diagnosis,
        max_results: Optional[int] = 8,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.
        See the docs: https://developer.infermedica.com/docs/suggest-related-concepts.

        :param diagnosis_request: Diagnosis request object
        :param max_results: (optional) Maximum number of results to return, default is 8
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A list of suggestions, dicts with 'id', 'name' and 'common_name' keys
        """
        data = diagnosis_request.get_api_request()

        response = super().suggest(
            max_results=max_results, interview_id=diagnosis_request.interview_id, **data
        )

        return response  # TODO: Pack response into model class

    def red_flags(
        self,
        diagnosis_request: models.Diagnosis,
        max_results: Optional[int] = 8,
        **kwargs: Any
    ) -> models.RedFlagList:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.
        See the docs: https://developer.infermedica.com/docs/red-flags.

        :param diagnosis_request: Diagnosis request object
        :param max_results: (optional) Maximum number of results to return, default is 8
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A list of RedFlag objects
        """
        data = diagnosis_request.get_api_request()

        response = super().red_flags(
            max_results=max_results, interview_id=diagnosis_request.interview_id, **data
        )

        return models.RedFlagList.from_json(response)

    def parse(
        self,
        text: str,
        include_tokens: Optional[bool] = False,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> models.ParseResults:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.
        See the docs: https://developer.infermedica.com/docs/nlp.

        :param text: Text to parse
        :param include_tokens: (optional) Switch to manipulate the include_tokens parameter
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A ParseResults object
        """
        response = super().parse(
            text=text,
            include_tokens=include_tokens,
            interview_id=interview_id,
            **kwargs
        )

        return models.ParseResults.from_json(response)

    def diagnosis(
        self, diagnosis_request: models.Diagnosis, **kwargs: Any
    ) -> models.Diagnosis:
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.
        See the docs: https://developer.infermedica.com/docs/diagnosis.

        :param diagnosis_request: Diagnosis request object
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A Diagnosis object with api response
        """
        data = diagnosis_request.get_api_request()

        response = super().diagnosis(
            interview_id=diagnosis_request.interview_id, **data, **kwargs
        )
        diagnosis_request.update_from_api(response)

        return diagnosis_request

    def rationale(
        self, diagnosis_request: models.Diagnosis, **kwargs: Any
    ) -> models.RationaleResult:
        """
        Makes an API request with provided diagnosis data and returns
        an explanation of why the given question has been selected by
        the reasoning engine.
        See the docs: https://developer.infermedica.com/docs/rationale.

        :param diagnosis_request: Diagnosis request object
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: An instance of the RationaleResult
        """
        data = diagnosis_request.get_api_request()

        response = super().rationale(
            interview_id=diagnosis_request.interview_id, **data, **kwargs
        )

        return models.RationaleResult.from_json(response)

    def explain(
        self, diagnosis_request: models.Diagnosis, target_id, **kwargs: Any
    ) -> models.ExplainResults:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidence.
        See the docs: https://developer.infermedica.com/docs/explain.

        :param diagnosis_request: Diagnosis request object
        :param target_id: Condition id for which explain shall be calculated
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A Diagnosis object with api response
        """
        data = diagnosis_request.get_api_request()

        response = super().explain(
            target_id=target_id,
            interview_id=diagnosis_request.interview_id,
            **data,
            **kwargs
        )

        return models.ExplainResults.from_json(response)

    def triage(self, diagnosis_request: models.Diagnosis, **kwargs: Any) -> Dict:
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/triage.

        :param diagnosis_request: Diagnosis request object
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A dict object with api response
        """
        data = diagnosis_request.get_api_request()

        response = super().triage(
            interview_id=diagnosis_request.interview_id, **data, **kwargs
        )

        return response  # TODO:  Pack response into model class

    def condition_details(self, condition_id: str, **kwargs: Any) -> models.Condition:
        """
        Makes an API request and returns condition details object.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#conditions.

        :param condition_id: Condition id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns:A Condition object
        """
        response = super().condition_details(condition_id=condition_id, **kwargs)

        return models.Condition.from_json(response)

    def condition_list(self, **kwargs: Any) -> models.ConditionList:
        """
        Makes an API request and returns list of condition details objects.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#conditions.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A ConditionList list object with Condition objects
        """
        response = super().condition_list(**kwargs)

        return models.ConditionList.from_json(response)

    def symptom_details(self, symptom_id: str, **kwargs: Any) -> models.Symptom:
        """
        Makes an API request and returns symptom details object.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#symptoms.

        :param symptom_id: Symptom id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A Symptom object
        """
        response = super().symptom_details(symptom_id=symptom_id, **kwargs)

        return models.Symptom.from_json(response)

    def symptom_list(self, **kwargs: Any) -> models.SymptomList:
        """
        Makes an API request and returns list of symptom details objects.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#symptoms.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A SymptomList list object with Symptom objects
        """
        response = super().symptom_list(**kwargs)

        return models.SymptomList.from_json(response)

    def risk_factor_details(
        self, risk_factor_id: str, **kwargs: Any
    ) -> models.RiskFactor:
        """
        Makes an API request and returns risk factor details object.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#risk-factors.

        :param risk_factor_id: Risk factor id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A RiskFactor object
        """
        response = super().risk_factor_details(risk_factor_id=risk_factor_id, **kwargs)

        return models.RiskFactor.from_json(response)

    def risk_factor_list(self, **kwargs: Any) -> models.RiskFactorList:
        """
        Makes an API request and returns list of risk factors details objects.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#risk-factors.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A RiskFactorList list object with RiskFactor objects
        """
        response = super().risk_factor_list(**kwargs)

        return models.RiskFactorList.from_json(response)

    def lab_test_details(self, lab_test_id: str, **kwargs: Any) -> models.LabTest:
        """
        Makes an API request and returns lab_test details object.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#lab-tests-and-lab-test-results.

        :param lab_test_id: Lab test id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A LabTest object
        """
        response = super().lab_test_details(lab_test_id=lab_test_id, **kwargs)

        return models.LabTest.from_json(response)

    def lab_test_list(self, **kwargs: Any) -> models.LabTestList:
        """
        Makes an API request and returns list of lab_test details objects.
        See the docs: https://developer.infermedica.com/docs/medical-concepts#lab-tests-and-lab-test-results.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A LabTestList list object with LabTest objects
        """
        response = super().lab_test_list(**kwargs)

        return models.LabTestList.from_json(response)
