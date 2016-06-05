from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    # Prepare diagnosis request it need to have sufficient amount of evidences
    # The most appropriate way to get a request way for explain method is to
    # use the one which has been created while interacting with diagnosis.
    # For the example purpose a new one is created.
    request = infermedica_api.Diagnosis(sex='female', age=35)

    request.add_symptom('s_10', 'present')
    request.add_symptom('s_608', 'present')
    request.add_symptom('s_1394', 'absent')
    request.add_symptom('s_216', 'present')
    request.add_symptom('s_9', 'present')
    request.add_symptom('s_188', 'present')

    # call the explain method
    request = api.explain(request, target_id='c_371')

    # and see the results
    print('\n\n', request)
