# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.v3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes for API v3 version.
"""

from enum import Enum
from typing import Optional, List, Dict, Union, Any

from .common import (
    APISharedConnector,
    ConceptDetails,
    ConditionDetails,
    SymptomDetails,
    RiskFactorDetails,
    LabTestDetails,
)
from .. import exceptions


class ConceptType(Enum):
    """Enum to hold search filter constants."""
    CONDITION = 'condition'
    SYMPTOM = 'symptom'
    RISK_FACTOR = 'risk_factor'
    LAB_TEST = 'lab_test'

    @staticmethod
    def has_value(val: Union['ConceptType', str]) -> bool:
        try:
            return val in ConceptType
        except TypeError:
            return val in (item.value for item in ConceptType)


class APIv3Connector(APISharedConnector):
    """
    Intermediate level class which handles requests to the Infermedica API,
    provides methods with detailed parameters, but still works on simple data structures.
    """

    def __init__(self, *args, api_version='v3', **kwargs: Any):
        """
        Initialize API connector.

        :param args: (optional) Arguments passed to lower level parent :class:`APIConnector` method
        :param api_version: (optional) API version, default is 'v2'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        Usage::
            >>> import infermedica_api
            >>> api = infermedica_api.APIv2Connector(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
        """
        super().__init__(*args, api_version=api_version, **kwargs)

    def get_age_object(self, age: int, age_unit: Optional[str] = None) -> Dict:
        """
        Prepare age object to sent in API request URL query.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'

        :returns: A dict object with age object accepted by the API

        :raises: :class:`infermedica_api.exceptions.InvalidAgeUnit`
        """
        age_obj = {
            'value': age
        }

        if age_unit in ('year', 'month',):
            age_obj['unit'] = age_unit
        elif age_unit is not None:
            raise exceptions.InvalidAgeUnit(age_unit)

        return age_obj

    def get_age_query_params(self, age: int, age_unit: Optional[str] = None) -> Dict:
        """
        Prepare age object to sent in API request URL query.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'

        :returns: A dict object with age URL query params accepted by the API

        :raises: :class:`infermedica_api.exceptions.InvalidAgeUnit`
        """
        age_obj = self.get_age_object(age=age, age_unit=age_unit)

        return {
            f'age.{key}': value
            for key, value in age_obj.items()
        }

    def search(self, phrase: str, age: int, age_unit: Optional[str] = None, **kwargs: Any) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param phrase: Phrase to look for
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APISharedConnector` method

        :returns: A List of dicts with 'id' and 'label' keys

        :raises: :class:`infermedica_api.exceptions.InvalidSearchFilter`
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().search(
            phrase=phrase,
            params=params,
            **kwargs
        )

    def parse(self, text: str, age: int, age_unit: Optional[str] = None, **kwargs: Any) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.

        :param text: Text to parse
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APISharedConnector` method

        :returns: A dict object with api response
        """
        data = kwargs.pop('data', {})
        data.update({
            'age': self.get_age_object(age=age, age_unit=age_unit),
        })

        return super().parse(
            text=text,
            data=data,
            **kwargs
        )

    def red_flags(self, data: Dict, **kwargs: Any) -> List[Dict[str, str]]:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.

        :param data: Diagnosis request data
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APISharedConnector` method

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        data.update({
            'suggest_method': 'suggest_method'
        })

        return self.suggest(
            data=data,
            **kwargs
        )

    def condition_details(self, condition_id: str, age: int, age_unit: Optional[str] = None,
                          **kwargs) -> ConditionDetails:
        """
        Makes an API request and returns condition details object.

        :param condition_id: Condition id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with condition details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().condition_details(
            condition_id=condition_id,
            params=params,
            **kwargs
        )

    def conditions_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List[ConditionDetails]:
        """
        Makes an API request and returns list of condition details objects.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dict objects with condition details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().conditions_list(
            params=params,
            **kwargs
        )

    def symptom_details(self, symptom_id: str, age: int, age_unit: Optional[str] = None, **kwargs) -> SymptomDetails:
        """
        Makes an API request and returns symptom details object.

        :param symptom_id: Symptom id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with symptom details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().symptom_details(
            symptom_id=symptom_id,
            params=params,
            **kwargs
        )

    def symptoms_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List[SymptomDetails]:
        """
        Makes an API request and returns list of symptom details objects.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dict objects with symptom details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().symptoms_list(
            params=params,
            **kwargs
        )

    def risk_factor_details(self, risk_factor_id: str, age: int, age_unit: Optional[str] = None,
                            **kwargs) -> RiskFactorDetails:
        """
        Makes an API request and returns risk factor details object.

        :param risk_factor_id: risk factor id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with risk factor details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().risk_factor_details(
            risk_factor_id=risk_factor_id,
            params=params,
            **kwargs
        )

    def risk_factors_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List[RiskFactorDetails]:
        """
        Makes an API request and returns list of risk factors details objects.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dict objects with risk factor details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().risk_factors_list(
            params=params,
            **kwargs
        )

    def lab_test_details(self, lab_test_id: str, age: int, age_unit: Optional[str] = None,
                         **kwargs) -> LabTestDetails:
        """
        Makes an API request and returns lab_test details object.

        :param lab_test_id: LabTest id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with lab test details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().lab_test_details(
            lab_test_id=lab_test_id,
            params=params,
            **kwargs
        )

    def lab_tests_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List[LabTestDetails]:
        """
        Makes an API request and returns list of lab test details objects.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dict objects with lab test details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().lab_tests_list(
            params=params,
            **kwargs
        )

    def concept_details(self, concept_id: str, age: int, age_unit: Optional[str] = None, **kwargs) -> ConceptDetails:
        """
        Makes an API request and returns lab test details object.

        :param concept_id: Concept id
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with concept details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        return super().concept_details(
            concept_id=concept_id,
            params=params,
            **kwargs
        )

    def concept_list(self, age: int, age_unit: Optional[str] = None, ids: Optional[List[str]] = None,
                     types: Optional[List[Union[ConceptType, str]]] = None, **kwargs) -> List[ConceptDetails]:
        """
        Makes an API request and returns list of concept details objects.

        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param ids: (optional) List of concept ids to fetch data only for selected ids
        :param types: (optional) List of concept types (enums ConceptType or str) to narrow the response
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A list of dict objects with concept details
        """
        params = kwargs.pop('params', {})
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

        if ids:
            params['ids'] = ','.join(ids)

        if types:
            for concept_type in types:
                if not ConceptType.has_value(concept_type):
                    raise exceptions.InvalidConceptType(concept_type)
            params['types'] = ','.join(types)

        return super().concept_list(
            params=params,
            **kwargs
        )
