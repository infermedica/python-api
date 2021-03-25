from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 52

    print("Laboratory tests list:")
    print(api.lab_test_list(age=age), end="\n\n")

    print("\n\nLaboratory test details:")
    print(api.lab_test_details("lt_81", age=age), end="\n\n")

    print("Non-existent laboratory test details:")
    print(api.lab_test_details("fail_test", age=age))
