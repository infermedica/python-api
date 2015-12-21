from __future__ import print_function
import config

config.setup_examples()
import infermedica_api


if __name__ == '__main__':
    api = infermedica_api.get_api()

    request = infermedica_api.Diagnosis(sex='male', age=35, time='2015-02-09T08:30:00+05:00')

    request.add_symptom('s_102', 'present', time='2015-02-09T08:00:00+05:00')
    request.add_symptom('s_21', 'present', time='2015-02-09')
    request.add_symptom('s_98', 'absent')

    request.set_pursued_conditions(['c_76', 'c_9'])

    # call diagnosis
    request = api.diagnosis(request)

    print(request)

    # ask patient the questions returned by diagnosis and update request with patient answers
    request.add_symptom('s_23', 'present')
    request.add_symptom('s_25', 'present')
    request.add_symptom('s_604', 'absent')
    request.add_symptom('s_1193', 'unknown')

    # call diagnosis again with updated request
    request = api.diagnosis(request)

    # repeat the process
    print('\n\n', request)
