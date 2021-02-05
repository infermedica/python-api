from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 28
    age_unit = "year"

    print("Symptoms list:")
    print(api.symptom_list(age=age, age_unit=age_unit), end="\n\n")

    print("Symptom details:")
    print(api.symptom_details("s_56", age=age, age_unit=age_unit), end="\n\n")

    print("Symptom details (with children):")
    print(api.symptom_details("s_551", age=age, age_unit=age_unit), end="\n\n")

    print("Non-existent symptom details:")
    print(api.symptom_details("fail_test", age=age, age_unit=age_unit))
