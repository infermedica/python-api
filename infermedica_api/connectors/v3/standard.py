# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.v3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes for API v3 version.
"""

from enum import Enum
from typing import Optional, List, Dict, Union, Any

from .basic import BasicAPIv3Connector
from ..common import (
    SearchConceptType,
    ConceptDetails,
    ConditionDetails,
    SymptomDetails,
    RiskFactorDetails,
    LabTestDetails,
    EvidenceList,
    ExtrasDict,
)
from ... import exceptions


# Types
AgeDict = Dict[str, Union[int, str]]
DiagnosticDict = Dict[str, Union[str, AgeDict, EvidenceList, ExtrasDict]]


class ConceptType(Enum):
    """Enum to hold search filter constants."""

    CONDITION = "condition"
    SYMPTOM = "symptom"
    RISK_FACTOR = "risk_factor"
    LAB_TEST = "lab_test"

    @staticmethod
    def has_value(val: Union["ConceptType", str]) -> bool:
        try:
            return val in ConceptType
        except TypeError:
            return val in (item.value for item in ConceptType)


class APIv3Connector(BasicAPIv3Connector):
    """
    Intermediate level class which handles requests to the Infermedica API,
    provides methods with detailed parameters, but still works on simple data structures.
    """

    def get_age_object(self, age: int, age_unit: Optional[str] = None) -> AgeDict:
        """
        Prepare age object to sent in API request URL query.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'

        :returns: A dict object with age object accepted by the API

        :raises: :class:`infermedica_api.exceptions.InvalidAgeUnit`
        """
        age_obj = {"value": age}

        if age_unit in (
            "year",
            "month",
        ):
            age_obj["unit"] = age_unit
        elif age_unit is not None:
            raise exceptions.InvalidAgeUnit(age_unit)

        return age_obj

    def get_age_query_params(
        self, age: int, age_unit: Optional[str] = None
    ) -> Dict[str, Union[int, str]]:
        """
        Prepare age object to sent in API request URL query.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'

        :returns: A dict object with age URL query params accepted by the API

        :raises: :class:`infermedica_api.exceptions.InvalidAgeUnit`
        """
        age_obj = self.get_age_object(age=age, age_unit=age_unit)

        return {f"age.{key}": value for key, value in age_obj.items()}

    def get_diagnostic_data_dict(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
    ) -> DiagnosticDict:
        data = {
            "sex": sex,
            "age": self.get_age_object(age=age, age_unit=age_unit),
            "evidence": evidence,
        }

        if extras:
            data["extras"] = extras

        return data

    def search(
        self,
        phrase: str,
        age: int,
        age_unit: Optional[str] = None,
        sex: Optional[str] = None,
        max_results: Optional[int] = 8,
        types: Optional[List[Union[SearchConceptType, str]]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param phrase: Phrase to look for
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param sex: (optional) Sex of the patient 'female' or 'male' to narrow results
        :param max_results: (optional) Maximum number of results to return, default is 8
        :param types: (optional) List of search concept types (enums SearchConceptType or str) to narrow the response
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A List of dicts with 'id' and 'label' keys

        :raises: :class:`infermedica_api.exceptions.InvalidSearchConceptType`
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))
        params.update({"phrase": phrase, "max_results": max_results})

        if sex:
            params["sex"] = sex

        if types:
            types_as_str_list = [
                SearchConceptType.get_value(concept_type) for concept_type in types
            ]

            for concept_type in types_as_str_list:
                if not SearchConceptType.has_value(concept_type):
                    raise exceptions.InvalidSearchConceptType(concept_type)

            params["types"] = ",".join(types_as_str_list)

        return super().search(params=params, **kwargs)

    def parse(
        self,
        text: str,
        age: int,
        age_unit: Optional[str] = None,
        include_tokens: Optional[bool] = False,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.
        See the docs: https://developer.infermedica.com/docs/v3/nlp.

        :param text: Text to parse
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param include_tokens: (optional) Switch to manipulate the include_tokens parameter
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = {
            "text": text,
            "age": self.get_age_object(age=age, age_unit=age_unit),
            "include_tokens": include_tokens,
        }

        return super().parse(data=data, headers=headers, **kwargs)

    def suggest(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
        suggest_method: Optional[str] = "symptoms",
        max_results: Optional[int] = 8,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.
        See the docs: https://developer.infermedica.com/docs/v3/suggest-related-concepts.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param extras: (optional) Dict with API extras
        :param suggest_method: (optional) Suggest method to be used,
                               one of values 'symptoms' (default), 'risk_factors', 'red_flags'
        :param max_results: (optional) Maximum number of results to return, default is 8
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        params = kwargs.pop("params", {})
        params.update({"max_results": max_results})

        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, age_unit=age_unit, extras=extras
        )
        if suggest_method:
            data["suggest_method"] = suggest_method

        return super().suggest(data=data, params=params, headers=headers)

    def diagnosis(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.
        See the docs: https://developer.infermedica.com/docs/v3/diagnosis.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, age_unit=age_unit, extras=extras
        )

        return super().diagnosis(data=data, headers=headers, **kwargs)

    def rationale(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Makes an API request with provided diagnosis data and returns
        an explanation of why the given question has been selected by
        the reasoning engine.
        See the docs: https://developer.infermedica.com/docs/v3/rationale.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, age_unit=age_unit, extras=extras
        )

        return super().rationale(data=data, headers=headers, **kwargs)

    def explain(
        self,
        target_id: str,
        evidence: EvidenceList,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidence.
        See the docs: https://developer.infermedica.com/docs/v3/explain.

        :param target_id: Condition id for which explain shall be calculated
        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with api response
        """

        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, age_unit=age_unit, extras=extras
        )
        data["target"] = target_id

        return super().explain(
            data=data,
            headers=headers,
            **kwargs,
        )

    def triage(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/v3/triage.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, age_unit=age_unit, extras=extras
        )

        return super().triage(data=data, headers=headers, **kwargs)

    def specialist_recommender(
        self,
        evidence: List,
        sex: str,
        age: int,
        age_unit: Optional[str] = None,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Makes a specialist recommendation API request with provided diagnosis data.
        See the docs: https://developer.infermedica.com/docs/v3/specialist-recommender.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = kwargs.pop("data", {})
        data.update(
            self.get_diagnostic_data_dict(
                evidence=evidence, sex=sex, age=age, age_unit=age_unit, extras=extras
            )
        )

        return super().specialist_recommender(data=data, headers=headers, **kwargs)

    def condition_details(
        self, condition_id: str, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> ConditionDetails:
        """
        Makes an API request and returns condition details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#conditions.

        :param condition_id: Condition id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with condition details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().condition_details(
            condition_id=condition_id, params=params, **kwargs
        )

    def condition_list(
        self, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> List[ConditionDetails]:
        """
        Makes an API request and returns list of condition details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#conditions.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A list of dict objects with condition details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().condition_list(params=params, **kwargs)

    def symptom_details(
        self, symptom_id: str, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> SymptomDetails:
        """
        Makes an API request and returns symptom details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#symptoms.

        :param symptom_id: Symptom id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with symptom details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().symptom_details(symptom_id=symptom_id, params=params, **kwargs)

    def symptom_list(
        self, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> List[SymptomDetails]:
        """
        Makes an API request and returns list of symptom details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#symptoms.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A list of dict objects with symptom details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().symptom_list(params=params, **kwargs)

    def risk_factor_details(
        self, risk_factor_id: str, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> RiskFactorDetails:
        """
        Makes an API request and returns risk factor details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#risk-factors.

        :param risk_factor_id: risk factor id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with risk factor details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().risk_factor_details(
            risk_factor_id=risk_factor_id, params=params, **kwargs
        )

    def risk_factor_list(
        self, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> List[RiskFactorDetails]:
        """
        Makes an API request and returns list of risk factors details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#risk-factors.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A list of dict objects with risk factor details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().risk_factor_list(params=params, **kwargs)

    def lab_test_details(
        self, lab_test_id: str, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> LabTestDetails:
        """
        Makes an API request and returns lab_test details object.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#lab-tests-and-lab-test-results.

        :param lab_test_id: LabTest id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with lab test details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().lab_test_details(
            lab_test_id=lab_test_id, params=params, **kwargs
        )

    def lab_test_list(
        self, age: int, age_unit: Optional[str] = None, **kwargs
    ) -> List[LabTestDetails]:
        """
        Makes an API request and returns list of lab test details objects.
        See the docs: https://developer.infermedica.com/docs/v3/medical-concepts#lab-tests-and-lab-test-results.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A list of dict objects with lab test details
        """
        params = kwargs.pop("params", {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().lab_test_list(params=params, **kwargs)

    def concept_details(self, concept_id: str, **kwargs) -> ConceptDetails:
        """
        Makes an API request and returns concept details object.
        See the docs: https://developer.infermedica.com/docs/v3/concepts.

        :param concept_id: Concept id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with concept details
        """
        return super().concept_details(concept_id=concept_id, **kwargs)

    def concept_list(
        self,
        ids: Optional[List[str]] = None,
        types: Optional[List[Union[ConceptType, str]]] = None,
        **kwargs,
    ) -> List[ConceptDetails]:
        """
        Makes an API request and returns list of concept details objects.
        See the docs: https://developer.infermedica.com/docs/v3/concepts.

        :param ids: (optional) List of concept ids to fetch data only for selected ids
        :param types: (optional) List of concept types (enums ConceptType or str) to narrow the response
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A list of dict objects with concept details
        """
        params = kwargs.pop("params", {})

        if ids:
            params["ids"] = ",".join(ids)

        if types:
            types_as_str_list = [
                concept_type.value
                if isinstance(concept_type, ConceptType)
                else concept_type
                for concept_type in types
            ]
            for concept_type in types_as_str_list:
                if not ConceptType.has_value(concept_type):
                    raise exceptions.InvalidConceptType(concept_type)
            params["types"] = ",".join(types_as_str_list)

        return super().concept_list(params=params, **kwargs)
