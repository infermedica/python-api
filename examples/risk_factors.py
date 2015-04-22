from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    print('Risk factors list:')
    print(api.risk_factors_list(), end="\n\n")

    # print('\n\nRisk factor details:')
    # print(api.risk_factor_details(''), end="\n\n")

    print('Non-existent risk factor details:')
    print(api.risk_factor_details('fail_test'))
