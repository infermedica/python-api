Python client for Infermedica API 
=================================

Infermedica Python client provides pragmatical access to a medical diagnostic API created by [Infermedica](http://infermedica.com).
Before using the library one must register for a developer account and obtain App-Id and App-Key at [Infermedica Developer Portal](https://developer.infermedica.com). All the API documentation is also available there.


# Installation

Install using `pip`:

```bash
pip install infermedica-api
```

### Quick start

A Quick verification if all works fine:

```python
import infermedica_api

api = infermedica_api.APIv3Connector(app_id="YOUR_APP_ID", app_key="YOUR_APP_KEY")
print(api.info())
```

# Configuration

## API Connectors
The library provides several "API Connectors", that can be used for communication with the Infermedica API. Depending on the required API version and programmatic integration level, a different API Connector should be used. The connectors can be distinguished by two factors. The first factor is the Infermedica API version. The API version is indicated by the connector class name e.g. `APIv3Connector` or `APIv2Connector`. The second factor is the programmatic integration level.  There are three levels available.

Here is a list of currently available API Connectors:
* `BasicAPIv3Connector` - API version: "v3", Integration level: "Basic"
* `APIv3Connector` - API version: "v3", Integration level: "Standard" _(default, recommended)_
* `BasicAPIv2Connector` - API version: "v2", Integration level: "Basic"
* `APIv2Connector` - API version: "v2", Integration level: "Standard"
* `ModelAPIv2Connector` - API version: "v2", Integration level: "Model"

### Basic Connectors
Provides all Infermedica API capabilities as methods, but all methods expose low level HTTP parameters e.g. query params, data or headers. This type of connector should be used if one needs to have full control over the underlying HTTP request content. Each basic connector class is prefixed with "Basic" keyword, e.g. `BasicAPIv3Connector` or `BasicAPIv2Connector`.

Here is an example to illustrate the basic connector method signature:
```python
def diagnosis(data, params=None, headers=None) -> Dict: ...
```

### Standard Connectors
_(default, recommended)_

Standard Connectors are based on Basic Connectors, but provide methods with more detailed attribute signatures. At the same time they operate on basic Python data types like `dict`, `list` or `string`. Therefore, it is easier to understand what is required for each method, and they take care of constructing proper a request to Infermedica API. The standard API connectors do not have s prefix in the class name e.g. `APIv3Connector` or `APIv2Connector`. It is the default and recommended level of integration.

Here is an example to illustrate standard connector method signature:
```python
def diagnosis(evidence, sex, age, age_unit=None, extras=None, interview_id=None) -> Dict: ...
```

### Model Connectors

Model Connectors are even higher level connectors, that are based on Standard Connectors. They expose methods that operate on predefined model classes as their inputs and outputs. Each model connector class is prefixed with the "Model" keyword, e.g. `ModelAPIv2Connector`.

Here is an example to illustrate model connector method signature:
```python
def diagnosis(diagnosis_request: Diagnosis) -> Diagnosis: ...
```


## Configuration types
There are two options to configure the API module, one may choose the most suitable option for related project.

### Local Configuration
Single local API Connector.

```python
import infermedica_api

api = infermedica_api.APIv3Connector(app_id="YOUR_APP_ID", app_key="YOUR_APP_KEY")

print(api.info())
```

Each API Connector constructor takes several configuration parameters, among others:
* `app_id` & `app_key` - Infermedica API credentials, the only two mandatory arguments.
* `model` - Infermedica API language model to be used, [see the docs](https://developer.infermedica.com/docs/v3/basics#models).
* `dev_mode` - Flag that indicates if requests are made on local or testing environment and are not real medical cases.


### Global Configuration
Configuration of one or many global API Connectors, that are easily available everywhere. For this purpose the `configure` function has to be used, to register global configurations. The configuration should be done in a place of the project that is executed on project startup, e.g. in some `__init__.py` file.

The `configure` function takes exactly the same parameters as each API Connector class constructor, but expect few additional optional parameters:
* `alias` - A unique string identifier of the configuration, if not provided configuration is registered as default.
* `default` - In case `alias` is provided, this flag determinate if the configuration should be also registered as the default one. There may be only one default.
* `api_connector` - API connector class to be used for the configuration or just a string with API Connector name, e.g. `"APIv3Connector"` _(default)_

To define a single global connector:

```python
import infermedica_api

infermedica_api.configure(app_id="YOUR_APP_ID", app_key="YOUR_APP_KEY")
```

To define multiple global connectors:

```python
import infermedica_api

# Aliased, default configuration with English language
infermedica_api.configure(
    alias="en",
    default=True,
    app_id="YOUR_APP_ID",
    app_key="YOUR_APP_KEY",
    model="infermedica-en"
)

# Configuration with Polish language
infermedica_api.configure(
    alias="pl",
    app_id="YOUR_APP_ID",
    app_key="YOUR_APP_KEY",
    model="infermedica-pl"
)

# Configuration with English language based on non-default connector
infermedica_api.configure(
    alias="basic-en",
    app_id="YOUR_APP_ID",
    app_key="YOUR_APP_KEY",
    model="infermedica-en",
    api_connector=infermedica_api.BasicAPIv3Connector
)
```

... and then at any place in the project just import the infermedica module and get an already configured API connector through `get_api` function:

```python
import infermedica_api

api = infermedica_api.get_api()  # Get default connector
print(api.info())

api = infermedica_api.get_api("pl")  # Get connector by alias
print(api.info())
```

# Usage

Here is an example of how to use the API to get a list of patient's likely conditions.

```python
import infermedica_api

api = infermedica_api.APIv3Connector(app_id="YOUR_APP_ID", app_key="YOUR_APP_KEY")

# Prepare initial patients diagnostic information.
sex = "female"
age = 32
evidence = [
    {"id": "s_21", "choice_id": "present", "source": "initial"},
    {"id": "s_98", "choice_id": "present", "source": "initial"},
    {"id": "s_107", "choice_id": "present"}
]

# call diagnosis
response = api.diagnosis(evidence=evidence, sex=sex, age=age)

# Access question asked by API
print(response["question"])
print(response["question"]["text"])  # actual text of the question
print(response["question"]["items"])  # list of related evidence with possible answers
print(response["question"]["items"][0]["id"])
print(response["question"]["items"][0]["name"])
print(response["question"]["items"][0]["choices"])  # list of possible answers
print(response["question"]["items"][0]["choices"][0]["id"])  # answer id
print(response["question"]["items"][0]["choices"][0]["label"])  # answer label

# Check the "should_stop" flag
print(response["should_stop"])

# Next update the request and get next question:
evidence.append({
    "id": response["question"]["items"][0]["id"],
    "choice_id": response["question"]["items"][0]["choices"][0]["id"]  # Just example, the choice_id shall be taken from the real user answer
})

# call diagnosis method again
response = api.diagnosis(evidence=evidence, sex=sex, age=age)

# ... and so on, continue the interview and watch for the "should_stop" flag. 
# Once the API returns a "should_stop" flag with the value set to true, the interview questions should stop and you can present the condition results:

# Access list of conditions with probabilities
print(response["conditions"])
print(response["conditions"][0]["id"])
print(response["conditions"][0]["name"])
print(response["conditions"][0]["probability"])
```


## Examples

To see more use cases on how to use the library look at the examples provided. One can easily check out and run examples, first define environmental variables with credentials then run the selected example:

 ```bash
export APP_ID=<YOUR_APP_ID>
export APP_KEY=<YOUR_APP_KEY>

python -m examples.v3.search
python -m examples.v3.parse
python -m examples.v3.symptoms
python -m examples.v3.risk_factors
python -m examples.v3.conditions
python -m examples.v3.lab_tests
python -m examples.v3.concepts
python -m examples.v3.diagnosis
python -m examples.v3.explain
python -m examples.v3.triage
python -m examples.v3.suggest
python -m examples.v3.specialist_recommender
```

## Exceptions

The library provides its own set of exceptions. Here is a list of exceptions, that are related to network communication and account permissions, which can be raised on any of the API Connector method calls:

```
infermedica_api.exceptions.BadRequest
infermedica_api.exceptions.UnauthorizedAccess
infermedica_api.exceptions.ForbiddenAccess
infermedica_api.exceptions.ResourceNotFound
infermedica_api.exceptions.MethodNotAllowed
infermedica_api.exceptions.ServerError
infermedica_api.exceptions.ConnectionError
```

There are also few additional exception that may occur:

* `MissingConfiguration` is raised during the `get_api` call if the API configuration for a given alias was not registered. Or the default API has not been configured, while calling `get_api` without the alias parameter.
* `MethodNotAvailableInAPIVersion` is raised if one tries to use a method from different API version.
* `InvalidSearchConceptType` is raised when the wrong filters are provided to the `search` method.
* `InvalidConceptType` is raised when the wrong concept types are provided to the `concepts` method.
* `InvalidAgeUnit` is raised when the wrong age unit is provided in API v3 Connectors.


# Contributing

Arkadiusz Szydełko ([akszydelko](https://github.com/akszydelko)) and Paweł Iwaszko ([iwaszko](https://github.com/iwaszko)) are the creators and current maintainers of the Infermedica API Python client. 

Pull requests are always welcome. Before submitting a pull request, please ensure that your coding style follows PEP 8 and rules form `.editorconfig` file. Also note that the library if formatted according to `black` rules so please apply them.

# Legal

Copyright 2024 by [Infermedica](http://infermedica.com).

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
