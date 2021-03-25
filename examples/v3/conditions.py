from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 35

    print("Conditions list:")
    print(api.condition_list(age=age), end="\n\n")

    print("Condition details:")
    print(api.condition_details("c_221", age=age), end="\n\n")

    print("Non-existent condition details:")
    print(api.condition_details("fail_test", age=age))
