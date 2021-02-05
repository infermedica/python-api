from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    print("Laboratory tests list:")
    print(api.lab_test_list(), end="\n\n")

    print("\n\nLaboratory test details:")
    print(api.lab_test_details("lt_81"), end="\n\n")

    print("Non-existent laboratory test details:")
    print(api.lab_test_details("fail_test"))
