from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    print('Conditions list:')
    print(api.conditions_list(), end="\n\n")

    print('Condition details:')
    print(api.condition_details('c_221'), end="\n\n")

    print('Non-existent condition details:')
    print(api.condition_details('fail_test'))
