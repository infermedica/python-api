# -*- coding: utf-8 -*-

"""
Infermedica Python API client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Infermedica Python API client provides access to powerful medical diagnostic API created by Infermedica.
Basic usage:

   >>> import infermedica_api
   >>> api = infermedica_api.API(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
   >>> print(api.info())
   {
     "updated_at": "2015-03-12T00:39:34+01:00",
     "conditions_count": 385,
     "observations_count": 875
   }

... you can also configure API object globally and use it without initialization in any module.
First configure the API:

   >>> import infermedica_api
   >>> infermedica_api.configure(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')

... and then in any module just import infermedica module and get configured API object:

   >>> import infermedica_api
   >>> api = infermedica_api.get_api()

The other requests are presented in `examples` and are described in our documentation. Full documentation
is available at <https://developer.infermedica.com>.

:copyright: (c) 2017 by Infermedica.
:license: Apache 2.0, see LICENSE for more details.

"""

__title__ = 'Infermedica API'
__version__ = '0.1.1'
__author__ = 'Arkadiusz Szydelko'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2020 Infermedica'

DEFAULT_API_VERSION = 'v2'
DEFAULT_API_ENDPOINT = 'https://api.infermedica.com/'

API_CONFIG = {
    'v1': {
        'methods': {
            'info': '/info',
            'lookup': '/lookup',
            'diagnosis': '/diagnosis',
            'observations': '/observations',
            'observation_details': '/observations/{id}',
            'conditions': '/conditions',
            'condition_details': '/conditions/{id}',
            'risk_factors': '/risk_factors',
            'risk_factor_details': '/risk_factors/{id}'
        }
    },
    'v2': {
        'methods': {
            'info': '/info',
            'search': '/search',
            'lookup': '/lookup',
            'suggest': '/suggest',
            'parse': '/parse',
            'diagnosis': '/diagnosis',
            'explain': '/explain',
            'triage': '/triage',
            'conditions': '/conditions',
            'condition_details': '/conditions/{id}',
            'symptoms': '/symptoms',
            'symptom_details': '/symptoms/{id}',
            'lab_tests': '/lab_tests',
            'lab_test_details': '/lab_tests/{id}',
            'risk_factors': '/risk_factors',
            'risk_factor_details': '/risk_factors/{id}',
            'red_flags': '/red_flags',
            'rationale': '/rationale',
        },
    },
}

from .models.condition import Condition, ConditionList
from .models.diagnosis import Diagnosis, DiagnosisQuestion, ConditionResult, ConditionResultList
from .models.lab_test import LabTest, LabTestList
from .models.observation import Observation, ObservationList
from .models.rationale import RationaleResult
from .models.red_flag import RedFlagList
from .models.risk_factor import RiskFactor, RiskFactorList
from .models.symptom import Symptom, SymptomList
from .webservice import configure, get_api, API, SEARCH_FILTERS
