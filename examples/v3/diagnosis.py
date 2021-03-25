from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    # Prepare the diagnosis request object
    request = config.get_example_request_data()

    # call diagnosis
    request = api.diagnosis(**request)

    print(request)
