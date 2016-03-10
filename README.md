Sabre Dev Studio: Python Wrapper
==================================

## Introduction

This is designed as a thin wrapper around Sabre's APIs, more information for which can be found at their [Developer Center](https://developer.sabre.com/docs/read/Home). The class handles authentication, request generation, and object conversion - instead of returning a dictionary, it can serialize the dictionary into a Named Tuple, with Pythonic naming conventions for the attributes (e.g. `origin_city` instead of `OriginCity`).

I'm not affiliated with Sabre; this is just a small tool that I found useful when writing Python scripts which use Sabre Dev Studio, and thought I'd share it. It's licensed under the MIT license (terms in `LICENSE`).

## Usage

The SabreDevStudio class can be initialized with no parameters, i.e.

```
sds = SabreDevStudio()
```

By default, this selects the test environment. To use the production server, initialize the class like so:

```
sds = SabreDevStudio(environment='prod')
```

To configure whether `request` will return a dictionary or an object, initialize the class with the parameter `return_obj`

```
sds1 = SabreDevStudio(return_obj=True)   # Will return a NamedTuple
sds2 = SabreDevStudio(return_obj=False)  # Will return a Dictionary
```

The class must first be configured with your client ID and client secret, and then authenticated (which issues the token get request and saves the token to the class' internal state):

```
sds.set_credentials('MYCLIENTID', 'MYCLIENTSECRET')
sds.authenticate()
```

After this, you should be ready to start issuing requests. Just call one of the supported methods, like `instaflights()`, or issue a request manually with a relative endpoint using `request(method, endpoint, payload)`, where payload is either the data (in the case of `PUT`, `POST`, or `PATCH`, or the query params (in the case of `GET`).

```
options = {
    'origin': 'JFK',
    'destination': 'LAX',
    'departuredate': '01-01-2016',
    'returndate': '01-02-2016'
}

result = sds.instaflights(options)
```

You'll notice that in this example, the departure and return dates are in a specific (ISO 8601) format. For convenience, a `convert_date` function is included to easily convert Python date objects into this format.

The reason the `instaflights` function does not take individual parameters as arguments into the function, and formats everything accordingly is because there are just too many options in the API; it would be difficult and cumbersome to do this, and fix it whenever any minor change to the API comes out. For the same reason, the NamedTuple response is generated dynamically instead of a Response object being declared.

Functions for other endpoints may have both convenience functions, taking parameters, or just a dictionary, like `instaflights`. See the `flights_to()` function for an example.

## Testing

There are tests in the `tests/` folder. In order for these to run properly, a `config.json` file must be included, with contents of the form:

```
{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}
```

Don't worry, the test suite won't make too many requests, and won't have a huge impact on your request limit. `base_test` makes three requests (excluding authentication), and each tester for the unit should only make at most two requests to the endpoint its testing (e.g. `instaflights_test.py` will only make one request).

## Examples

There are example utilities in the `examples/` directory. For example, the `cheapest_destinations.py` tool finds the cheapest roundtrip airfares to a given airport. Luckily, most domestic (US) airfares are roundtrip, so this effectively works as both a 'Flights To' and 'Flights From' finder.

```
python cheapest-destinations.py SFO
```

Will return something like:

```
PHX  $88.00      F9
DFW  $100.60     AA
LAX  $110.60     UA
SNA  $110.60     UA
ORD  $120.60     AA UA
BUR  $128.60     UA
SAN  $130.60     UA
DEN  $130.60     VX
```

There is also a `seat_maps.py` example, which returns the seat map for a given flight, but the API is *very* buggy, and doesn't work for about 90% of the cases I've tried.

```
python seat-maps.py JFK LAX 05-01-2016 AA 1
```

I find that this only works for American Airlines and perhaps other carriers that use SABRE, but even with AA there are some Internal Server Errors.
