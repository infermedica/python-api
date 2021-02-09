# -*- coding: utf-8 -*-

"""
infermedica_api.connectors.v2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes for API v2 version.
"""

from typing import Optional, List, Dict, Any, Union

from ..common import (
    EvidenceList,
    ExtrasDict,
    BaseAPIConnector,
    BasicAPICommonMethodsMixin,
)


# Types
DiagnosticDict = Dict[str, Union[str, int, EvidenceList, ExtrasDict]]


class BasicAPIv2Connector(BasicAPICommonMethodsMixin, BaseAPIConnector):
    def __init__(self, *args, api_version="v2", **kwargs: Any):
        """
        Initialize API connector.

        :param args: (optional) Arguments passed to lower level parent :class:`BaseAPIConnector` method
        :param api_version: (optional) API version, default is 'v2'
        :param kwargs: (optional) Keyword arguments passed to lower level parent :class:`BaseAPIConnector` method

        Usage::
            >>> import infermedica_api
            >>> api = infermedica_api.BasicAPIv2Connector(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
        """
        super().__init__(*args, api_version=api_version, **kwargs)

    def red_flags(
        self, data: Dict, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Makes an API request with provided diagnosis data and returns a list
        of evidence that may be related to potentially life-threatening
        conditions.
        See the docs: https://developer.infermedica.com/docs/red-flags.

        :param data: Request data
        :param params: (optional) URL query params
        :param headers: (optional) HTTP request headers

        :returns: A list of dicts with 'id', 'name' and 'common_name' keys
        """
        method = self._get_method("red_flags")

        return self.call_api_post(
            method=method, data=data, params=params, headers=headers
        )
