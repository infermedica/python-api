# -*- coding: utf-8 -*-

"""
infermedica_api.models.diagnosis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains models for data returned from api as well as object to construct api requests,
related to /diagnosis method.
"""
from .base import BaseModel, BaseModelList, ModelCommon


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
        self.symptoms = []
        self.lab_tests = []
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

    def add_symptom(self, _id, state, time=None):
        """
        Adds symptom with given presence to evidence list.

        :param _id: Symptom id
        :type _id: str
        :param state: Symptom presence, one of three values ("present", "absent" or "unknown")
        :type state: str
        :param time: (optional) Symptom occurrence time (ISO8601 formatted)
        :type time: str
        """
        self.__add_evidence(self.symptoms, _id, state, time)

    def add_lab_test(self, _id, state, time=None):
        """
        Adds laboratory test with given presence to evidence list.

        :param _id: Laboratory test id
        :type _id: str
        :param state: Laboratory test presence, one of three values ("present", "absent" or "unknown")
        :type state: str
        :param time: (optional) Laboratory test occurrence time (ISO8601 formatted)
        :type time: str
        """
        self.__add_evidence(self.lab_tests, _id, state, time)

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

            "evidence": self.observations + self.symptoms + self.lab_tests + self.risk_factors,

            "extras": self.extras
        }

        if self.pursued:
            request['pursued'] = self.pursued

        if self.evaluation_time:
            request['evaluated_at'] = self.evaluation_time

        return request
