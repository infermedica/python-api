from infermedica_api.connectors.v2.models import Diagnosis
from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    # To prepare a diagnosis request it needs to have a sufficient amount of evidence
    # The most appropriate way to get a request for explain method is to
    # use the one which has been created while interacting with diagnosis.
    # For example purposes, a new one is created.
    request = Diagnosis(sex="female", age=35)

    request.add_symptom("s_10", "present")
    request.add_symptom("s_608", "present")
    request.add_symptom("s_1394", "absent")
    request.add_symptom("s_216", "present")
    request.add_symptom("s_9", "present")
    request.add_symptom("s_188", "present")

    # call the explain method
    request = api.explain(request, target_id="c_62")

    # and see the results
    print("\n\n", request)
