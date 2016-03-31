# -*- coding: utf-8 -*-

"""
infermedica_api.models.observation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains observation models for data returned from api.
"""
import warnings

from .base import BaseModel, BaseModelList


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
        warnings.warn("Class Observation is deprecated, please use Symptom.",
                      category=DeprecationWarning)
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
        warnings.warn("Class ObservationList is deprecated, please use SymptomList.",
                      category=DeprecationWarning)
        mapping = {}
        for i, item in enumerate(json):
            item = Observation(**item)
            mapping[item.id] = i
        return ObservationList(json, mapping=mapping)

    def get_observation_details(self, _id):
        return self._get_details(_id)
