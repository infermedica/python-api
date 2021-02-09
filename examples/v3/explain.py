from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    # Prepare the diagnosis request object
    request = config.get_example_request_data()

    # call the explain method
    request = api.explain(**request, target_id="c_49")

    # and see the results
    print("\n\n", request)
