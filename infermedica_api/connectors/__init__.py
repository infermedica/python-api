# -*- coding: utf-8 -*-

"""
infermedica_api.connectors
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains API Connector classes and related utils.
"""
from typing import Union

from .common import SearchConceptType
from .v2 import BasicAPIv2Connector, APIv2Connector, ModelAPIv2Connector
from .v3 import BasicAPIv3Connector, APIv3Connector, ConceptType

APIConnectorType = Union[
    BasicAPIv2Connector,
    APIv2Connector,
    ModelAPIv2Connector,
    BasicAPIv3Connector,
    APIv3Connector,
]
