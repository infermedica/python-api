from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    # Prepare the diagnosis request object
    request = config.get_example_request_data()

    # call triage method
    response = api.suggest(**request)
    print("\n\n", response)

    # Set different suggest_method
    request["suggest_method"] = "risk_factors"

    # call triage method
    response = api.suggest(**request)
    print("\n\n", response)

    # Set different suggest_method
    request["suggest_method"] = "red_flags"

    # call triage method
    response = api.suggest(**request)
    print("\n\n", response)
