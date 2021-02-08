# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.v2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes for API v2 version.
"""

from typing import Optional, List, Dict, Any, Union

from .basic import BasicAPIv2Connector
from ..common import (
    SearchConceptType,
    EvidenceList,
    ExtrasDict,
)
from ... import exceptions


# Types
DiagnosticDict = Dict[str, Union[str, int, EvidenceList, ExtrasDict]]


class APIv2Connector(BasicAPIv2Connector):
    def get_diagnostic_data_dict(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        extras: Optional[ExtrasDict] = None,
    ) -> DiagnosticDict:
        data = {"sex": sex, "age": age, "evidence": evidence}

        if extras:
            data["extras"] = extras

        return data

    def search(
        self,
        phrase: str,
        sex: Optional[str] = None,
        max_results: Optional[int] = 8,
        types: Optional[List[Union[SearchConceptType, str]]] = None,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param phrase: Phrase to look for
        :param sex: (optional) Sex of the patient 'female' or 'male' to narrow results
        :param max_results: (optional) Maximum number of results to return, default is 8
        :param types: (optional) List of search filters (enums SearchConceptType or str) to narrow the response
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv2Connector` method

        :returns: A List of dicts with 'id' and 'label' keys

        :raises: :class:`infermedica_api.exceptions.InvalidSearchConceptType`
        """
        params = kwargs.pop("params", {})
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

            params["type"] = types_as_str_list

        return super().search(params=params, **kwargs)

    def parse(
        self,
        text: str,
        include_tokens: Optional[bool] = False,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.
        See the docs: https://developer.infermedica.com/docs/nlp.

        :param text: Text to parse
        :param include_tokens: (optional) Switch to manipulate the include_tokens parameter
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        params = kwargs.pop("params", None)

        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = kwargs.pop("data", {})
        data.update({"text": text, "include_tokens": include_tokens})

        return super().parse(data=data, params=params, headers=headers)

    def suggest(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        extras: Optional[ExtrasDict] = None,
        max_results: Optional[int] = 8,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.
        See the docs: https://developer.infermedica.com/docs/suggest-related-concepts.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param extras: (optional) Dict with API extras
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
            evidence=evidence, sex=sex, age=age, extras=extras
        )

        return super().suggest(data=data, params=params, headers=headers)

    def red_flags(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        extras: Optional[ExtrasDict] = None,
        max_results: Optional[int] = 8,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.
        See the docs: https://developer.infermedica.com/docs/red-flags.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param extras: (optional) Dict with API extras
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
            evidence=evidence, sex=sex, age=age, extras=extras
        )

        return super().red_flags(data=data, params=params, headers=headers)

    def diagnosis(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict:
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.
        See the docs: https://developer.infermedica.com/docs/diagnosis.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, extras=extras
        )

        return super().diagnosis(data=data, headers=headers, **kwargs)

    def rationale(
        self,
        evidence: EvidenceList,
        sex: str,
        age: int,
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict:
        """
        Makes an API request with provided diagnosis data and returns
        an explanation of why the given question has been selected by
        the reasoning engine.
        See the docs: https://developer.infermedica.com/docs/rationale.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, extras=extras
        )

        return super().rationale(data=data, headers=headers, **kwargs)

    def explain(
        self,
        target_id: str,
        evidence: EvidenceList,
        sex: str,
        age: Union[int, str],
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidence.
        See the docs: https://developer.infermedica.com/docs/explain.

        :param target_id: Condition id for which explain shall be calculated
        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with api response
        """

        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, extras=extras
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
        age: Union[int, str],
        extras: Optional[ExtrasDict] = None,
        interview_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict:
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/triage.

        :param evidence: Diagnostic evidence list
        :param sex: Biological sex value, one of values 'female' or 'male'
        :param age: Age value
        :param extras: (optional) Dict with API extras
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BasicAPIv3Connector` method

        :returns: A dict object with api response
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.get_interview_id_headers(interview_id=interview_id))

        data = self.get_diagnostic_data_dict(
            evidence=evidence, sex=sex, age=age, extras=extras
        )

        return super().triage(data=data, headers=headers, **kwargs)
