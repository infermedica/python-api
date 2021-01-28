from .. import config

config.setup_examples()
import infermedica_api

if __name__ == '__main__':
    api = infermedica_api.get_api('v2')

    print('Look for evidences containing phrase headache:')
    print(api.search('headache'), end="\n\n")

    print('Look for evidences containing phrase breast, only for female specific symptoms:')
    print(api.search('breast', sex='female'), end="\n\n")

    print('Look for evidences containing phrase breast, only for female specific symptoms, with the limit of 5 results:')
    print(api.search('breast', sex='female', max_results=5), end="\n\n")

    print('Look for symptoms and risk factors containing phrase trauma:')
    print(api.search('trauma', filters=[
        infermedica_api.SEARCH_FILTERS.SYMPTOMS, infermedica_api.SEARCH_FILTERS.RISK_FACTORS]), end="\n\n")
