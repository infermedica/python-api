from typing import Optional, List, Dict

from .common import APIConnector, SEARCH_FILTERS
from .. import exceptions


class APIv3Connector(APIConnector):
    """
    Intermediate level class which handles requests to the Infermedica API,
    provides methods with detailed parameters, but still works on simple data structures.
    """

    def __init__(self, *args, api_version='v3', **kwargs: Dict):
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

    def search(self, phrase: str, age: int, age_unit: Optional[str] = None, sex: Optional[str] = None,
               max_results: Optional[int] = 8, filters: Optional[List] = None,
               **kwargs: Dict) -> List[Dict[str, str]]:
        """
        Makes an API search request and returns list of dicts containing keys: 'id', 'label' and 'type'.
        Each dict represent an evidence (symptom, lab test or risk factor).
        By default only symptoms are returned, to include other evidence types use filters.

        :param phrase: Phrase to look for
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
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
        params.update(self.get_age_query_params(age=age, age_unit=age_unit))

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

    def parse(self, text: str, age: int, age_unit: Optional[str] = None, include_tokens: Optional[bool] = False,
              interview_id: Optional[str] = None, **kwargs: Dict) -> Dict:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.

        :param phrase: Text to parse
        :param age: Age value
        :param age_unit: (optional) Age unit, one of values 'year' or 'month'
        :param include_tokens: (optional) Switch to manipulate the include_tokens parameter
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIConnector` method

        :returns: A dict object with api response
        """
        params = kwargs.pop('params', {})
        data = {
            'text': text,
            'age': self.get_age_object(age=age, age_unit=age_unit),
            'include_tokens': include_tokens
        }

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
        data['suggest_method'] = 'red_flags'

        return self.suggest(
            data=data,
            max_results=max_results,
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

    def condition_details(self, condition_id: str, age: int, age_unit: Optional[str] = None, **kwargs) -> Dict:
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

    def conditions_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List[Dict]:
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

    def symptom_details(self, symptom_id: str, age: int, age_unit: Optional[str] = None, **kwargs) -> Dict:
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

    def symptoms_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List[Dict]:
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

    def risk_factor_details(self, risk_factor_id: str, age: int, age_unit: Optional[str] = None, **kwargs) -> Dict:
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

    def risk_factors_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List:
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

    def lab_test_details(self, lab_test_id: str, age: int, age_unit: Optional[str] = None, **kwargs) -> Dict:
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

    def lab_tests_list(self, age: int, age_unit: Optional[str] = None, **kwargs) -> List:
        """
        Makes an API request and returns list of lab_test details objects.

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
