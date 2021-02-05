# -*- coding: utf-8 -*-

"""
infermedica_api.models.lab_test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains laboratory test models for data returned from api.
"""
from .base import BaseModel, BaseModelList


class LabTest(BaseModel):
    """Model class for API laboratory testss details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs LabTest object from given dict and returns it.

        :param json: Dict with laboratory test values
        :type json: dict

        :returns: LabTest details object
        :rtype: :class:`infermedica_api.models.LabTest`
        """
        return LabTest(**json)


class LabTestList(BaseModelList):
    """Model class for API list of laboratory test details objects."""

    @staticmethod
    def from_json(json):
        """
        Constructs LabTestList object from list of dicts and returns it.

        :param json: List with laboratory test details dict values
        :type json: list

        :returns: LabTests details list object
        :rtype: :class:`infermedica_api.models.LabTestList`
        """
        mapping = {}
        for i, item in enumerate(json):
            item = LabTest(**item)
            mapping[item.id] = i
        return LabTestList(json, mapping=mapping)

    def get_lab_test_details(self, _id):
        return self._get_details(_id)
