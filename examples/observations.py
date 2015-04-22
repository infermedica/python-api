from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    print('Observations list:')
    print(api.observations_list(), end="\n\n")

    print('Observation details:')
    print(api.observation_details('s_56'), end="\n\n")

    print('Observation details (with children):')
    print(api.observation_details('s_551'), end="\n\n")

    # Children usage example
    # api.observation_details('s_551').children.get('severity', [])

    print('Non-existent observation details:')
    print(api.observation_details('fail_test'))
