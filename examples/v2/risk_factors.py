from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    print("Risk factors list:")
    print(api.risk_factor_list(), end="\n\n")

    print("\n\nRisk factor details:")
    print(api.risk_factor_details("p_37"), end="\n\n")

    print("Non-existent risk factor details:")
    print(api.risk_factor_details("fail_test"))
