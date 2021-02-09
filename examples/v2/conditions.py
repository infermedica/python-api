from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    print("Conditions list:")
    print(api.condition_list(), end="\n\n")

    print("Condition details:")
    print(api.condition_details("c_221"), end="\n\n")

    print("Non-existent condition details:")
    print(api.condition_details("fail_test"))
