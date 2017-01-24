from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    print('Parse simple text:')
    response = api.parse('i feel smoach pain but no couoghing today')
    print(response, end="\n\n")

    print('Parse simple text and include tokens information:')
    response = api.parse('i feel smoach pain but no couoghing today', include_tokens=True)
    print(response, end="\n\n")
