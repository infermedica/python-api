from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 38

    print("Parse simple text:")
    response = api.parse("i feel stomach pain but no coughing today", age=age)
    print(response, end="\n\n")

    print("Parse simple text and include tokens information:")
    response = api.parse(
        "i feel stomach pain but no coughing today", age=age, include_tokens=True
    )
    print(response, end="\n\n")
