from .. import config

config.setup_examples()
import infermedica_api

if __name__ == '__main__':
    api: infermedica_api.APIv3Connector = infermedica_api.get_api()

    age = 35

    print('Concepts list:')
    print(api.concept_list(age=age), end="\n\n")

    print('Condition and risk factor concepts list:')
    print(api.concept_list(age=age, types=[infermedica_api.ConceptType.CONDITION,
                                           infermedica_api.ConceptType.RISK_FACTOR]), end="\n\n")

    print('Concepts details:')
    print(api.concept_details('s_13', age=age), end="\n\n")

    print('Non-existent concepts details:')
    print(api.concept_details('fail_test', age=age))
