from infermedica_api.connectors.v2.models import Diagnosis
from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    # Prepare the diagnosis request object
    request = Diagnosis(sex="male", age=30)
    request.add_symptom("s_1193", "present")
    request.add_symptom("s_488", "present")
    request.add_symptom("s_418", "absent")

    # Alternatively prepare a dict based request object
    # request = {
    #     'sex': 'male',
    #     'age': 30,
    #     'evidence': [
    #         {'id': 's_1193', 'choice_id': 'present'},
    #         {'id': 's_488', 'choice_id': 'present'},
    #         {'id': 's_418', 'choice_id': 'absent'}
    #     ]
    # }

    # call triage method
    request = api.suggest(request)

    # and see the results
    print("\n\n", request)
