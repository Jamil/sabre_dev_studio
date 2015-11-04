Sabre Dev Studio -- Python Wrapper
==================================

# Introduction

This is designed as a thin wrapper around Sabre's APIs, documentation for which can be found at #{ sabre API location }. The class handles authentication, request generation, and object conversion - instead of returning a dictionary, it can serialize the dictionary into a Named Tuple, with Pythonic naming conventions for the attributes.

I'm not affiliated with Sabre -- this is just a small tool that I found useful when writing Python scripts which use Sabre Dev Studio, and thought I'd share it. It's licensed under the MIT license (terms in LICENSE).

# Usage

The SabreDevStudio class can be initialized with no parameters, i.e.

```
sds = SabreDevStudio()
```

By default, this selects the test environment. To use the production server, initialize the class like so:

```
sds = SabreDevStudio(environment='prod')
```

To configure whether `request` will return a dictionary or an object, initialize the class with the parameter return_obj

```
sds1 = SabreDevStudio(return_obj=True)   # Will return a NamedTuple
sds2 = SabreDevStudio(return_obj=False)  # Will return a Dictionary
```

The class must first be configured with your client ID and client secret, and then authenticated (which issues the token get request and saves the token to the class' internal state):

```
sds.set_credentials('MYCLIENTID', 'MYCLIENTSECRET')
sds.authenticate()
```

After this, you should be ready to start issuing requests. Just call one of the supported methods, like instaflights(), or issue a request manually with a relative endpoint using request(method, endpoint, payload), where payload is either the data (in the case of PUT, POST, or PATCH, or the query params (in the case of GET).

```
options = {
    'origin': 'JFK',
    'destination': 'LAX',
    'departuredate': '01-01-2016',
    'returndate': '01-02-2016'
}

result = sds.instaflights(options)
```

# Testing

There are tests in the tests/ folder. In order for these to run properly, a `config.json` file must be included, with contents of the form:

```
{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}
```

Don't worry, the test suite won't make too many requests. `base_test` makes four requests (excluding authentication), and each tester for the unit should only make one test to the endpoint its testing (e.g. `instaflights_test.py` will only make one request)
