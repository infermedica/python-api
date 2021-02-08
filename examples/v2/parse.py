from .. import config

config.setup_examples()
import infermedica_api


if __name__ == "__main__":
    api: infermedica_api.ModelAPIv2Connector = infermedica_api.get_api("v2")

    print("Parse simple text:")
    response = api.parse("i feel stomach pain but no coughing today")
    print(response, end="\n\n")

    print("Parse simple text and include tokens information:")
    response = api.parse(
        "i feel stomach pain but no coughing today", include_tokens=True
    )
    print(response, end="\n\n")
