from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    print("Symptoms list:")
    print(api.symptom_list(), end="\n\n")

    print("Symptom details:")
    print(api.symptom_details("s_56"), end="\n\n")

    print("Symptom details (with children):")
    print(api.symptom_details("s_551"), end="\n\n")

    print("Non-existent symptom details:")
    print(api.symptom_details("fail_test"))
