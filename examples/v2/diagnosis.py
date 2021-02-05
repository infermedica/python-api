from infermedica_api.connectors.v2.models import Diagnosis
from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    request = Diagnosis(sex="female", age=35)

    request.add_symptom("s_21", "present", source="initial")
    request.add_symptom("s_98", "present", source="initial")
    request.add_symptom("s_418", "present", source="suggest")
    request.add_symptom("s_18", "present", source="predefined")
    request.add_symptom("s_10", "present", source="red_flags")
    request.add_symptom("s_107", "absent")

    # call diagnosis
    request = api.diagnosis(request)

    print(request)

    # ask patient the questions returned by diagnosis and update request with patient answers
    request.add_symptom("s_99", "present")
    request.add_symptom("s_8", "absent")
    request.add_symptom("s_25", "present")
    # ... and so on until you decided that enough question have been asked
    # or you have sufficient results in request.conditions

    # call diagnosis again with updated request
    request = api.diagnosis(request)

    # repeat the process
    print("\n\n", request)
