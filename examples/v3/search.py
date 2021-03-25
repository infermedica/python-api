from .. import config

config.setup_examples()
import infermedica_api

if __name__ == "__main__":
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 38

    print("Look for evidence containing the phrase headache:")
    print(api.search("headache", age=age), end="\n\n")

    print("Look for evidence containing the phrase breast, female specific symptoms:")
    print(api.search("breast", age=age, sex="female"), end="\n\n")

    print(
        "Look for evidence containing the phrase breast, female specific symptoms, with a limit of 5 results:"
    )
    print(api.search("breast", age=age, sex="female", max_results=5), end="\n\n")

    print("Look for symptoms and risk factors containing the phrase trauma:")
    print(
        api.search(
            "trauma",
            age=age,
            types=[
                infermedica_api.SearchConceptType.SYMPTOM,
                infermedica_api.SearchConceptType.RISK_FACTOR,
            ],
        ),
        end="\n\n",
    )
