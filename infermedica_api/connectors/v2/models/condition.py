# -*- coding: utf-8 -*-

"""
infermedica_api.models.condition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains condition models for data returned from api.
"""
from .base import BaseModel, BaseModelList


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
