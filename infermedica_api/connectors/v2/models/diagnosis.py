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

    def __init__(self, sex, age, interview_id=None, **kwargs):
        """
        Initialize diagnosis object with basic information about patient.

        :param sex: Patient's sex ("female" or "male")
        :type sex: str
        :param age: Patient's age
        :type age: int
        :param interview_id: Unique interview id for diagnosis
        :type interview_id: str
        """
        self.patient_sex = sex
        self.patient_age = age

        self.symptoms = []
        self.lab_tests = []
        self.risk_factors = []

        self.pursued = []

        self.question = None
        self.conditions = ConditionResultList()
        self.should_stop = None
        self.extras = {}
        self.extras_permanent = {}

        self.interview_id = interview_id

    def __add_evidence(self, collection, _id, state, source=None):
        """Helper function to update evidence list."""
        evidence = {"id": _id, "choice_id": state}
        if source:
            evidence["source"] = source

        collection.append(evidence)

    def add_symptom(self, _id, state, source=None):
        """
        Adds symptom with given presence to evidence list.

        :param _id: Symptom id
        :type _id: str
        :param state: Symptom presence, one of three values ("present", "absent" or "unknown")
        :type state: str
        :param source: (optional) Symptom source,
                       one of values: ("initial", "suggest", "predefined", "red_flags")
        :type source: str
        """
        self.__add_evidence(self.symptoms, _id, state, source=source)

    def add_lab_test(self, _id, state, source=None):
        """
        Adds laboratory test with given presence to evidence list.

        :param _id: Laboratory test id
        :type _id: str
        :param state: Laboratory test presence, one of three values ("present", "absent" or "unknown")
        :type state: str
        :param source: (optional) Laboratory test source,
                       one of values: ("initial", "suggest", "predefined", "red_flags")
        :type source: str
        """
        self.__add_evidence(self.lab_tests, _id, state, source=source)

    def add_risk_factor(self, _id, state, source=None):
        """
        Adds risk factor with given presence to evidence list.

        :param _id: Risk factor id
        :type _id: str
        :param state: Risk factor presence,
        one of three values ("present", "absent" or "unknown")
        :type state: str
        :param source: (optional) Risk factor source,
                       one of values: ("initial", "suggest", "predefined", "red_flags")
        :type source: str
        """
        self.__add_evidence(self.risk_factors, _id, state, source=source)

    def add_evidence(self, _id, state, source=None):
        """
        Adds evidence with given presence to evidence list.

        :param _id: Evidence id
        :type _id: str
        :param state: Evidence presence,
        one of three values ("present", "absent" or "unknown")
        :type state: str
        :param source: (optional) Evidence source,
                       one of values: ("initial", "suggest", "predefined", "red_flags")
        :type source: str
        """
        evidence_list = self.symptoms

        if _id.startswith(("p_", "rf_")):
            evidence_list = self.risk_factors
        elif _id.startswith("lt_"):
            evidence_list = self.lab_tests

        self.__add_evidence(evidence_list, _id, state, source=source)

    def set_pursued_conditions(self, pursued):
        """
        Sets conditions for pursued diagnosis.

        :param pursued: List of condition ids
        :type pursued: list of strings
        """
        self.pursued = pursued

    def set_interview_id(self, value):
        """
        Sets interview id for diagnosis.

        :param value: Unique interview id for diagnosis
        :type value: str
        """
        self.interview_id = value

    def set_extras(self, attribute, value, permanent=False):
        """
        Sets extras attributes to be sent with the diagnosis requests.

        :param attribute: String with the attribute name
        :type attribute: str
        :param value: Value to set for the attribute
        :type value: bool | str | number
        :param permanent: Conditions if the attribute shall be sent only in the next diagnosis request
        or should persists through multiple diagnosis calls.
        :type permanent: bool
        """
        if permanent:
            self.extras_permanent[attribute] = value
        else:
            self.extras[attribute] = value

    def update_from_api(self, json):
        """
        Updates current object by diagnosis response from the API.

        :param json: Dict obtained from the API diagnosis response
        :type json: dict
        """
        if "question" in json and isinstance(json["question"], dict):
            self.question = DiagnosisQuestion.from_json(json["question"])
        else:
            self.question = None

        self.conditions = ConditionResultList.from_json(
            json.get("conditions", []) or []
        )
        self.should_stop = json.get("should_stop", None)
        self.extras = json.get("extras", {}) or {}

    def get_evidence(self):
        return self.symptoms + self.lab_tests + self.risk_factors

    def get_api_request(self):
        """
        Based on current Diagnosis object construct
        dict object of the format accepted by diagnosis API method.

        :return: Diagnosis API request dict
        :rtype: dict
        """
        request = {
            "sex": self.patient_sex,
            "age": self.patient_age,
            "evidence": self.get_evidence(),
            "extras": dict(self.extras_permanent, **self.extras),
        }

        if self.pursued:
            request["pursued"] = self.pursued

        return request

    def to_dict(self):
        """
        Transform object to dict.

        :return: Diagnosis object as dict.
        :rtype: dict
        """
        return dict(
            self.get_api_request(),
            **{
                "question": self.question.to_dict()
                if hasattr(self.question, "to_dict")
                else None,
                "conditions": self.conditions.to_dict()
                if hasattr(self.conditions, "to_dict")
                else None,
                "should_stop": self.should_stop,
            }
        )
