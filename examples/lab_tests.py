from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    print('Laboratory tests list:')
    print(api.lab_tests_list(), end="\n\n")

    # print('\n\nLaboratory test details:')
    # print(api.lab_test_details(''), end="\n\n")

    print('Non-existent laboratory test details:')
    print(api.lab_test_details('fail_test'))
