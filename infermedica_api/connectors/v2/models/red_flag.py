# -*- coding: utf-8 -*-

"""
infermedica_api.models.red_flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains red flag models for data returned from api.
"""
from .base import BaseModel, BaseModelList


class RedFlag(BaseModel):
    """Model class for API red flag object."""

    @staticmethod
    def from_json(json):
        """
        Constructs RedFlag object from given dict and returns it.

        :param json: Dict with red flag values
        :type json: dict

        :returns: RedFlag details object
        :rtype: :class:`infermedica_api.models.RedFlag`
        """
        return RedFlag(**json)


class RedFlagList(BaseModelList):
    """Model class for API list of red flag objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs RedFlagList object from list of dicts and returns it.

        :param json: List with red flag details dict values
        :type json: list

        :returns: RedFlagList list object
        :rtype: :class:`infermedica_api.models.RedFlagList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = RedFlag(**item)
            mapping[item.id] = i
        return RedFlagList(json, mapping=mapping)

    def get_red_flag_details(self, _id):
        return self._get_details(_id)
