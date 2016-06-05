Python client for Infermedica API 
=================================

Infermedica Python client provides access to a medical diagnostic API created by [Infermedica](http://infermedica.com).
The API documentation can be found at [Infermedica Developer Portal](https://developer.infermedica.com).


## Install

Install using `pip`:

```bash
$ pip install infermedica-api
```

or using `easy_install`:

```bash
$ easy_install infermedica-api
```


## Configuration

First of all register for a developer account and obtain your app_id and app_key at [Infermedica Developer Portal](https://developer.infermedica.com).

#### Option one
Configure a global API object to easily use it everywhere:

```python
import infermedica_api

infermedica_api.configure(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')
```

... and then in any module just import infermedica module and get configured API object:

```python
import infermedica_api

api = infermedica_api.get_api()
```

#### Option two
Configure through a non-global API object:

```python
import infermedica_api
api = infermedica_api.API(app_id='YOUR_APP_ID', app_key='YOUR_APP_KEY')

print(api.info())
```

### Api version
Both of the above options to configure API object take an optional parameter `api_version`, which determines the version of Infermedica API to be used. For the current version the default API version is set automatically to `v2` and this is the recommended version to use.

## Usage

Here is an example of how to use the API to get a list of patient's likely diagnoses.

```python
import infermedica_api

api = infermedica_api.get_api()

# Create diagnosis object with initial patient information.
# Note that time argument is optional here as well as in the add_symptom function
request = infermedica_api.Diagnosis(sex='male', age=35)

request.add_symptom('s_21', 'present')
request.add_symptom('s_98', 'present')
request.add_symptom('s_107', 'absent')

request.set_pursued_conditions(['c_33', 'c_49'])  # Optional

# call diagnosis
request = api.diagnosis(request)

# Access question asked by API
print(request.question)
print(request.question.text)  # actual text of the question
print(request.question.items)  # list of related evidences with possible answers
print(request.question.items[0]['id'])
print(request.question.items[0]['name'])
print(request.question.items[0]['choices'])  # list of possible answers
print(request.question.items[0]['choices'][0]['id'])  # answer id
print(request.question.items[0]['choices'][0]['label'])  # answer label

# Access list of conditions with probabilities
print(request.conditions)
print(request.conditions[0]['id'])
print(request.conditions[0]['name'])
print(request.conditions[0]['probability'])

# Next update the request and get next question:
# Just example, the id and answer shall be taken from the real user answer
request.add_symptom(request.question.items[0]['id'], request.question.items[0]['choices'][1]['id'])

# call diagnosis method again
request = api.diagnosis(request)

# ... and so on, until you decide to stop the diagnostic interview.
```

Note that after each diagnosis call, the request object gets updated and you can obtain a diagnostic question to ask.
You can also update the request object with new observations or risk factors to get even more precise diagnostic insights and new questions to verify. 

For more take a look at provided examples.

## Examples

To easily run examples edit `examples/config.py` file and enter your account credentials.
Then go to `examples` folder and just run the following:

 ```bash
$ python search.py
```
 
```bash
$ python symptoms.py
```

```bash
$ python risk_factors.py
```

```bash
$ python conditions.py
```

```bash
$ python lab_tests.py
```

```bash
$ python diagnosis.py
```

```bash
$ python explain.py
```

### Contributing ###

Arkadiusz Szydełko ([akszydelko](https://github.com/akszydelko)) and Paweł Iwaszko ([iwaszko](https://github.com/iwaszko)) are the creators and current maintainers of the Infermedica API Python client. 

Pull requests are always welcome. Before submitting a pull request, please ensure that your coding style follows PEP 8 and rules form `.editorconfig` file.

### Legal ###

Copyright 2016 by [Infermedica](http://infermedica.com).

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
