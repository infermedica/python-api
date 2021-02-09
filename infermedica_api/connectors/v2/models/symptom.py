# -*- coding: utf-8 -*-

"""
infermedica_api.models.symptom
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains symptom models for data returned from api.
"""
from .base import BaseModel, BaseModelList


class Symptom(BaseModel):
    """Model class for API symptoms details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs Symptom object from given dict and returns it.

        :param json: Dict with symptom values
        :type json: dict

        :returns: Symptom details object
        :rtype: :class:`infermedica_api.models.Symptom`
        """
        return Symptom(**json)


class SymptomList(BaseModelList):
    """Model class for API list of symptom details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs SymptomList object from list of dicts and returns it.

        :param json: List with symptom details dict values
        :type json: list

        :returns: Symptoms details list object
        :rtype: :class:`infermedica_api.models.SymptomList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = Symptom(**item)
            mapping[item.id] = i
        return SymptomList(json, mapping=mapping)

    def get_symptom_details(self, _id):
        return self._get_details(_id)
