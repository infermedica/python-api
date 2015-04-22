# -*- coding: utf-8 -*-

"""
infermedica_api.models
~~~~~~~~~~~~~~~~~~~~~~

This module contains models for data returned from api as well as object to construct api requests.
"""

import json


# Base models

class ModelCommon(object):
    """Abstract class with implementation of commonly used functions."""

    class Meta:
        abstract = True

    def __str__(self):
        """Returns nicely formatted object."""
        return self.to_json(pretty_print=True)

    def to_json(self, pretty_print=False):
        """
        Returns json dumps of the class object.
        If pretty_print argument set to True,
        returned string is nicely formatted.

        :param pretty_print: Boolean which determinants
        if output should be humanly readable formatted
        :type pretty_print: bool

        :returns: String with json data of the object
        :rtype: str
        """
        if pretty_print:
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        return json.dumps(self, default=lambda o: o.__dict__)


class BaseModel(ModelCommon):
    """
    Abstract class of model with init function,
    which generically assign object parameters.
    """

    class Meta:
        abstract = True

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BaseModelList(list, ModelCommon):
    """
    Abstract class of list model with init function, which assign key mapping.
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if 'mapping' in kwargs:
            self.mapping = kwargs.pop('mapping')
        else:
            self.mapping = {}

        super(BaseModelList, self).__init__(*args, **kwargs)

    def _get_details(self, _id):
        """
        Generic function to handle object returns by the object id.

        :param _id: Object id
        :type _id: str

        :returns: Model object with given id
        """
        try:
            return self[self.mapping[_id]]
        except (IndexError, KeyError) as e:
            return None


# Observation models

class Observation(BaseModel):
    """Model class for API observations details objects."""
    # TODO: Children ids
    @staticmethod
    def from_json(json):
        """
        Constructs Observation object from given dict and returns it.

        :param json: Dict with observation values
        :type json: dict

        :returns: Observation details object
        :rtype: :class:`infermedica_api.models.Observation`
        """
        return Observation(**json)


class ObservationList(BaseModelList):
    """Model class for API list of observation details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs ObservationList object from list of dicts and returns it.

        :param json: List with observation details dict values
        :type json: list

        :returns: Observations details list object
        :rtype: :class:`infermedica_api.models.ObservationList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = Observation(**item)
            mapping[item.id] = i
        return ObservationList(json, mapping=mapping)

    def get_observation_details(self, _id):
        return self._get_details(_id)


# Condition models

class Condition(BaseModel):
    """Model class for API condition details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs Condition object from given dict and returns it.

        :param json: Dict with condition values
        :type json: dict

        :returns: Condition details object
        :rtype: :class:`infermedica_api.models.Condition`
        """
        return Condition(**json)


class ConditionList(BaseModelList):
    """Model class for API list of condition details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs ConditionList object from list of dicts and returns it.

        :param json: List with condition details dict values
        :type json: list

        :returns: Conditions details list object
        :rtype: :class:`infermedica_api.models.ConditionList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = Condition(**item)
            mapping[item.id] = i
        return ConditionList(json, mapping=mapping)

    def get_condition_details(self, _id):
        return self._get_details(_id)


# Risk factor models

class RiskFactor(BaseModel):
    """Model class for API risk factor details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs RiskFactor object from given dict and returns it.

        :param json: Dict with risk factor values
        :type json: dict

        :returns: Risk factor details object
        :rtype: :class:`infermedica_api.models.RiskFactor`
        """
        return RiskFactor(**json)


class RiskFactorList(BaseModelList):
    """Model class for API list of risk factor details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs RiskFactorList object from list of dicts and returns it.

        :param json: List with risk factor details dict values
        :type json: list

        :returns: Risk factor details list object
        :rtype: :class:`infermedica_api.models.RiskFactorList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = RiskFactor(**item)
            mapping[item.id] = i
        return RiskFactorList(json, mapping=mapping)

    def get_risk_factor_details(self, _id):
        return self._get_details(_id)


# Diagnosis models

class ConditionResult(BaseModel):
    """Model class for API condition results objects from diagnosis calls."""

    @staticmethod
    def from_json(json):
        """
        Constructs ConditionResult object from given dict and returns it.

        :param json: Dict with condition result values
        :type json: dict

        :returns: Condition result details object
        :rtype: :class:`infermedica_api.models.ConditionResult`
        """
        return ConditionResult(**json)


class ConditionResultList(BaseModelList):
    """Model class for API list of condition result objects from diagnosis calls."""

    @staticmethod
    def from_json(json):
        """
        Constructs ConditionResultList object from list of dicts and returns it.

        :param json: List with condition result details dict values
        :type json: list

        :returns: Condition result details list object
        :rtype: :class:`infermedica_api.models.ConditionResultList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = ConditionResult(**item)
            mapping[item.id] = i
        return ConditionResultList(json, mapping=mapping)

    def get_condition_details(self, _id):
        return self._get_details(_id)


class DiagnosisQuestion(BaseModel):
    """Model class for API question objects from diagnosis calls."""

    @staticmethod
    def from_json(json):
        """
        Constructs DiagnosisQuestion object from given dict and returns it.

        :param json: Dict with diagnosis question values
        :type json: dict

        :returns: Diagnosis question details object
        :rtype: :class:`infermedica_api.models.DiagnosisQuestion`
        """
        return DiagnosisQuestion(**json)


class Diagnosis(ModelCommon):
    """
    Model class for handling diagnosis requests and responses.
    It construct diagnosis request and is updated after next diagnosis calls.
    It will contain diagnosis questions, as well as results.
    """

    def __init__(self, sex, age, time=None):
        """
        Initialize diagnosis object with basic information about patient
        and optionally with examination time.

        :param sex: Patient's sex ("female" or "male")
        :type sex: str
        :param age: Patient's age
        :type age: int
        :param time: (optional) Time of diagnosis evaluation (ISO8601 formatted)
        :type time: str
        """
        self.patient_sex = sex
        self.patient_age = age
        self.evaluation_time = time

        self.observations = []
        self.risk_factors = []

        self.pursued = []

        self.question = None
        self.conditions = ConditionResultList()
        self.extras = {}

    def __add_evidence(self, collection, _id, state, time):
        """Helper function to update evidence list."""
        evidence = {
            "id": _id,
            "choice_id": state
        }

        if time:
            evidence['observed_at'] = time

        collection.append(evidence)

    def add_observation(self, _id, state, time=None):
        """
        Adds observation with given presence to evidence list.

        :param _id: Observation id
        :type _id: str
        :param state: Observation presence, one of three values ("present", "absent" or "unknown")
        :type state: str
        :param time: (optional) Observation occurrence time (ISO8601 formatted)
        :type time: str
        """
        self.__add_evidence(self.observations, _id, state, time)

    def add_risk_factor(self, _id, state, time=None):
        """
        Adds risk factor with given presence to evidence list.

        :param _id: Risk factor id
        :type _id: str
        :param state: Risk factor presence,
        one of three values ("present", "absent" or "unknown")
        :type state: str
        :param time: (optional) Risk factor occurrence time (ISO8601 formatted)
        :type time: str
        """
        self.__add_evidence(self.risk_factors, _id, state, time)

    def set_pursued_conditions(self, pursued):
        """
        Sets conditions for pursued diagnosis.

        :param pursued: List of condition ids
        :type pursued: list of strings
        """
        self.pursued = pursued

    def update_from_api(self, json):
        """
        Updates current object by diagnosis response from the API.

        :param json: Dict obtained from the API diagnosis response
        :type json: dict
        """
        if 'question' in json:
            self.question = DiagnosisQuestion.from_json(json['question'])
        else:
            self.question = None

        self.conditions = ConditionResultList.from_json(json.get('conditions', []))
        self.extras = json.get('extras', {})

    def get_api_request(self):
        """
        Based on current Diagnosis object construct
        dict object of the format accepted by API.

        :return: Diagnosis API request dict
        :rtype: dict
        """
        request = {
            "sex": self.patient_sex,
            "age": self.patient_age,

            "evidence": self.observations + self.risk_factors,

            "extras": self.extras
        }

        if self.pursued:
            request['pursued'] = self.pursued

        if self.evaluation_time:
            request['evaluated_at'] = self.evaluation_time

        return request
