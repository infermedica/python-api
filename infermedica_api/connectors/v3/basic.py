# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.v3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes for API v3 version.
"""

from typing import Optional, List, Dict, Any

from ..common import (
    ConceptDetails,
    BaseAPIConnector,
    BasicAPICommonMethodsMixin,
)


class BasicAPIv3Connector(BasicAPICommonMethodsMixin, BaseAPIConnector):
    def __init__(self, *args, api_version="v3", **kwargs: Any):
        """
        Initialize API connector.

        :param args: (optional) Arguments passed to lower level parent :class:`BaseAPIConnector` method
        :param api_version: (optional) API version, default is 'v3'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BaseAPIConnector` method

        Usage::
            >>> import infermedica_api
            >>> api = infermedica_api.BasicAPIv3Connector(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
        """
        super().__init__(*args, api_version=api_version, **kwargs)

    def specialist_recommender(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict:
        """
        Makes a specialist recommendation API request with provided diagnosis data.
        See the docs: https://developer.infermedica.com/docs/v3/specialist-recommender.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with api response
        """
        method = self._get_method("specialist_recommender")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )

    def concept_details(
        self,
        concept_id: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> ConceptDetails:
        """
        Makes an API request and returns concept details object.
        See the docs: https://developer.infermedica.com/docs/v3/concepts.

        :param concept_id: Concept id
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A dict object with concept details
        """
        method = self._get_method("concept_details")
        method = method.format(**{"id": concept_id})

        return self.call_api_get(method=method, params=params, headers=headers)

    def concept_list(
        self, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[ConceptDetails]:
        """
        Makes an API request and returns list of concept details objects.
        See the docs: https://developer.infermedica.com/docs/v3/concepts.

        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dict objects with concept details
        """
        method = self._get_method("concepts")

        return self.call_api_get(method=method, params=params, headers=headers)
