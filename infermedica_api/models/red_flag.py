# -*- coding: utf-8 -*-

"""
infermedica_api.models.red_flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains RedFlag models for data returned from api.
"""
from .base import BaseModel, BaseModelList


class RedFlag(BaseModel):
    """Model class for API RedFlag object."""

    @staticmethod
    def from_json(json):
        """
        Constructs RedFlag object from given dict and returns it.

        :param json: Dict with RedFlag values
        :type json: dict

        :returns: RedFlag details object
        :rtype: :class:`infermedica_api.models.RedFlag`
        """
        return RedFlag(**json)


class RedFlagList(BaseModelList):
    """Model class for API list of RedFlag objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs RedFlagList object from list of dicts and returns it.

        :param json: List with RedFlag details dict values
        :type json: list

        :returns: RedFlags details list object
        :rtype: :class:`infermedica_api.models.RedFlagList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = RedFlag(**item)
            mapping[item.id] = i
        return RedFlagList(json, mapping=mapping)

    def get_RedFlag_details(self, _id):
        return self._get_details(_id)
