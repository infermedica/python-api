# -*- coding: utf-8 -*-

"""
infermedica_api.models.risk_factor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains risk factor models for data returned from api.
"""
from .base import BaseModel, BaseModelList


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
