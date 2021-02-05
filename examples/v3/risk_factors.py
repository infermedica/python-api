from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 45

    print("Risk factors list:")
    print(api.risk_factor_list(age=age), end="\n\n")

    print("\n\nRisk factor details:")
    print(api.risk_factor_details("p_37", age=age), end="\n\n")

    print("Non-existent risk factor details:")
    print(api.risk_factor_details("fail_test", age=age))
