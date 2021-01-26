from .common import APIConnector, SEARCH_FILTERS
from .. import exceptions, models


class APIv2Connector(APIConnector):
    def __init__(self, api_version='v2', *args, **kwargs):
        super().__init__(api_version=api_version, *args, **kwargs)  # TODO: Will it work?

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

    def suggest(self, data, max_results=8, interview_id=None, **kwargs):
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A list of suggestions, dicts with 'id', 'name' and 'common_name' keys.
        :rtype: list
        """
        params = kwargs.pop('params', {})
        params.update({'max_results': max_results})

        return super().suggest(
            data=data,
            params=params,
            interview_id=interview_id,
            **kwargs
        )

    def red_flags(self, data, max_results=8, interview_id=None, **kwargs):
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
        params = kwargs.pop('params', {})
        params.update({'max_results': max_results})

        return super().red_flags(
            data=data,
            params=params,
            interview_id=interview_id,
            **kwargs
        )

    def parse(self, text, include_tokens=False, interview_id=None, **kwargs):
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
        params = kwargs.pop('params', {})
        data = {
            'text': text,
            'include_tokens': include_tokens
        }

        return super().parse(
            data=data,
            params=params,
            interview_id=interview_id,
            **kwargs
        )

    def explain(self, data, target_id, interview_id=None, **kwargs):
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
        data_with_target = dict(data, **{'target': target_id})

        return super().explain(
            data=data_with_target,
            interview_id=interview_id,
            **kwargs,
        )


class APIv2ModelConnector(APIv2Connector):
    def suggest(self, diagnosis_request, max_results=8, interview_id=None, **kwargs):
        """
        Makes an API suggest request and returns a list of suggested evidence.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A list of suggestions, dicts with 'id', 'name' and 'common_name' keys.
        :rtype: list
        """
        data = diagnosis_request.get_api_request()

        response = super().suggest(
            data=data,
            max_results=max_results,
            interview_id=interview_id
        )

        return response  # TODO: Pack response into model class

    def red_flags(self, diagnosis_request, max_results=8, interview_id=None, **kwargs):
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
        data = diagnosis_request.get_api_request()

        response = super().red_flags(
            data=data,
            max_results=max_results,
            interview_id=interview_id
        )

        return models.RedFlagList.from_json(response)

    def parse(self, text, include_tokens=False, interview_id=None, **kwargs):
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
        response = super().parse(
            text=text,
            include_tokens=include_tokens,
            interview_id=interview_id,
            **kwargs
        )

        return models.ParseResults.from_json(response)

    def diagnosis(self, diagnosis_request, **kwargs):
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
        data = diagnosis_request.get_api_request()

        response = super().diagnosis(
            data=data,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )
        diagnosis_request.update_from_api(response)

        return diagnosis_request

    def rationale(self, diagnosis_request, **kwargs):
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
        data = diagnosis_request.get_api_request()

        response = super().rationale(
            data=data,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )

        return models.RationaleResult.from_json(response)

    def explain(self, diagnosis_request, target_id, **kwargs):
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
        data = diagnosis_request.get_api_request()

        response = super().explain(
            data=data,
            target_id=target_id,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )

        return models.ExplainResults.from_json(response)

    def triage(self, diagnosis_request, **kwargs):
        """
        Makes a triage API request with provided diagnosis data.
        Returns triage results dict.
        See the docs: https://developer.infermedica.com/docs/triage.

        :param diagnosis_request: Diagnosis request object or json request for diagnosis method.
        :type diagnosis_request: :class:`infermedica_api.models.Diagnosis` or dict

        :returns: A dict object with api response
        :rtype: dict
        """
        data = diagnosis_request.get_api_request()

        response = super().triage(
            data=data,
            interview_id=diagnosis_request.interview_id,
            **kwargs
        )

        return response  # TODO:  Pack response into model class

    def condition_details(self, condition_id, **kwargs):
        """
        Makes an API request and returns condition details object.

        :param _id: Condition id
        :type _id: str

        :returns:A Condition object
        :rtype: :class:`infermedica_api.models.Condition`
        """
        response = super().condition_details(
            condition_id=condition_id,
            **kwargs
        )

        return models.Condition.from_json(response)

    def conditions_list(self, **kwargs):
        """
        Makes an API request and returns list of condition details objects.

        :returns: A ConditionList list object with Condition objects
        :rtype: :class:`infermedica_api.models.ConditionList`
        """
        response = super().conditions_list(**kwargs)

        return models.ConditionList.from_json(response)

    def symptom_details(self, symptom_id, **kwargs):
        """
        Makes an API request and returns symptom details object.

        :param _id: Symptom id
        :type _id: str

        :returns: A Symptom object
        :rtype: :class:`infermedica_api.models.Symptom`
        """
        response = super().symptom_details(
            symptom_id=symptom_id,
            **kwargs
        )

        return models.Symptom.from_json(response)

    def symptoms_list(self, **kwargs):
        """
        Makes an API request and returns list of symptom details objects.

        :returns: A SymptomList list object with Symptom objects
        :rtype: :class:`infermedica_api.models.SymptomList`
        """
        response = super().symptoms_list(**kwargs)

        return models.SymptomList.from_json(response)

    def risk_factor_details(self, risk_factor_id, **kwargs):
        """
        Makes an API request and returns risk factor details object.

        :param _id: risk factor id
        :type _id: str

        :returns: A RiskFactor object
        :rtype: :class:`infermedica_api.models.RiskFactor`
        """
        response = super().risk_factor_details(
            risk_factor_id=risk_factor_id,
            **kwargs
        )

        return models.RiskFactor.from_json(response)

    def risk_factors_list(self, **kwargs):
        """
        Makes an API request and returns list of risk factors details objects.

        :returns: A RiskFactorList list object with RiskFactor objects
        :rtype: :class:`infermedica_api.models.RiskFactorList`
        """
        response = super().risk_factors_list(**kwargs)

        return models.RiskFactorList.from_json(response)

    def lab_test_details(self, lab_test_id, **kwargs):
        """
        Makes an API request and returns lab_test details object.

        :param _id: LabTest id
        :type _id: str

        :returns: A LabTest object
        :rtype: :class:`infermedica_api.models.LabTest`
        """
        response = super().lab_test_details(
            lab_test_id=lab_test_id,
            **kwargs
        )

        return models.LabTest.from_json(response)

    def lab_tests_list(self, **kwargs):
        """
        Makes an API request and returns list of lab_test details objects.

        :returns: A LabTestList list object with LabTest objects
        :rtype: :class:`infermedica_api.models.LabTestList`
        """
        response = super().lab_tests_list(**kwargs)

        return models.LabTestList.from_json(response)
