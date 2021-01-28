from typing import Optional, List, Dict

from .common import APISharedConnector
from .. import models


class APIv2Connector(APISharedConnector):
    """
    Intermediate level class which handles requests to the Infermedica API,
    provides methods with detailed parameters, but still works on simple data structures.
    """

    def __init__(self, *args, api_version='v2', **kwargs: Dict):
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


class APIv2ModelConnector(APIv2Connector):
    """
    High level class which handles requests to the Infermedica API,
    provides methods that operates on data models.
    """

    def suggest(self, diagnosis_request: models.Diagnosis, max_results: Optional[int] = 8,
                interview_id: Optional[str] = None, **kwargs: Dict) -> List[Dict[str, str]]:
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param diagnosis_request: Diagnosis request object
        :param max_results: (optional) Maximum number of result to return, default is 8
        :param interview_id: (optional) Unique interview id for diagnosis session
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A list of suggestions, dicts with 'id', 'name' and 'common_name' keys
        """
        data = diagnosis_request.get_api_request()

        response = super().suggest(
            data=data,
            max_results=max_results,
            interview_id=interview_id
        )

        return response  # TODO: Pack response into model class

    def red_flags(self, diagnosis_request: models.Diagnosis, max_results: Optional[int] = 8,
                  **kwargs: Dict) -> models.RedFlagList:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.

        :param diagnosis_request: Diagnosis request object
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A list of RedFlag objects
        """
        data = diagnosis_request.get_api_request()

        response = super().red_flags(
            data=data,
            max_results=max_results,
            interview_id=diagnosis_request.interview_id
        )

        return models.RedFlagList.from_json(response)

    def parse(self, text: str, include_tokens: Optional[bool] = False, interview_id: Optional[str] = None,
              **kwargs: Dict) -> models.ParseResults:
        """
        Makes an parse API request with provided text and include_tokens parameter.
        Returns parse results with detailed list of mentions found in the text.

        :param phrase: Text to parse
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

    def diagnosis(self, diagnosis_request: models.Diagnosis, **kwargs: Dict) -> models.Diagnosis:
        """
        Makes a diagnosis API request with provided diagnosis data
        and returns diagnosis question with possible conditions.

        :param diagnosis_request: Diagnosis request object
        :param interview_id: Unique interview id for diagnosis
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A Diagnosis object with api response
        """
        data = diagnosis_request.get_api_request()

        response = super().diagnosis(
            data=data,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )
        diagnosis_request.update_from_api(response)

        return diagnosis_request

    def rationale(self, diagnosis_request: models.Diagnosis, **kwargs: Dict) -> models.RationaleResult:
        """
        Makes an API request with provided diagnosis data and returns
        an explanation of why the given question has been selected by
        the reasoning engine.

        :param diagnosis_request: Diagnosis request object
        :param interview_id: Unique interview id for diagnosis
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: An instance of the RationaleResult
        """
        data = diagnosis_request.get_api_request()

        response = super().rationale(
            data=data,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )

        return models.RationaleResult.from_json(response)

    def explain(self, diagnosis_request: models.Diagnosis, target_id, **kwargs: Dict) -> models.ExplainResults:
        """
        Makes an explain API request with provided diagnosis data and target condition.
        Returns explain results with supporting and conflicting evidences.

        :param diagnosis_request: Diagnosis request object
        :param target_id: Condition id for which explain shall be calculated
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A Diagnosis object with api response
        """
        data = diagnosis_request.get_api_request()

        response = super().explain(
            data=data,
            target_id=target_id,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )

        return models.ExplainResults.from_json(response)

    def triage(self, diagnosis_request: models.Diagnosis, **kwargs: Dict) -> Dict:
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
            data=data,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )

        return response  # TODO:  Pack response into model class

    def condition_details(self, condition_id: str, **kwargs: Dict) -> models.Condition:
        """
        Makes an API request and returns condition details object.

        :param condition_id: Condition id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns:A Condition object
        """
        response = super().condition_details(
            condition_id=condition_id,
            **kwargs
        )

        return models.Condition.from_json(response)

    def conditions_list(self, **kwargs: Dict) -> models.ConditionList:
        """
        Makes an API request and returns list of condition details objects.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A ConditionList list object with Condition objects
        """
        response = super().conditions_list(**kwargs)

        return models.ConditionList.from_json(response)

    def symptom_details(self, symptom_id: str, **kwargs: Dict) -> models.Symptom:
        """
        Makes an API request and returns symptom details object.

        :param symptom_id: Symptom id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A Symptom object
        """
        response = super().symptom_details(
            symptom_id=symptom_id,
            **kwargs
        )

        return models.Symptom.from_json(response)

    def symptoms_list(self, **kwargs: Dict) -> models.SymptomList:
        """
        Makes an API request and returns list of symptom details objects.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A SymptomList list object with Symptom objects
        """
        response = super().symptoms_list(**kwargs)

        return models.SymptomList.from_json(response)

    def risk_factor_details(self, risk_factor_id: str, **kwargs: Dict) -> models.RiskFactor:
        """
        Makes an API request and returns risk factor details object.

        :param risk_factor_id: Risk factor id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A RiskFactor object
        """
        response = super().risk_factor_details(
            risk_factor_id=risk_factor_id,
            **kwargs
        )

        return models.RiskFactor.from_json(response)

    def risk_factors_list(self, **kwargs: Dict) -> models.RiskFactorList:
        """
        Makes an API request and returns list of risk factors details objects.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A RiskFactorList list object with RiskFactor objects
        """
        response = super().risk_factors_list(**kwargs)

        return models.RiskFactorList.from_json(response)

    def lab_test_details(self, lab_test_id: str, **kwargs: Dict) -> models.LabTest:
        """
        Makes an API request and returns lab_test details object.

        :param lab_test_id: Lab test id
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A LabTest object
        """
        response = super().lab_test_details(
            lab_test_id=lab_test_id,
            **kwargs
        )

        return models.LabTest.from_json(response)

    def lab_tests_list(self, **kwargs: Dict) -> models.LabTestList:
        """
        Makes an API request and returns list of lab_test details objects.

        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`APIv2Connector` method

        :returns: A LabTestList list object with LabTest objects
        """
        response = super().lab_tests_list(**kwargs)

        return models.LabTestList.from_json(response)
