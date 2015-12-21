from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    print('Look for observations containing phrase headache:')
    print(api.search('headache'), end="\n\n")

    print('Look for observations containing phrase breast, only for female specific observations:')
    print(api.search('breast', sex='female'), end="\n\n")

    print('Look for observations containing phrase breast, only for female specific observations, with the limit of 5 results:')
    print(api.search('breast', sex='female', max_results=5), end="\n\n")
