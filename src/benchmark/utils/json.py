import json


def date_hook(values):
    # We are storing our datetime in a dict most frequently
    if not isinstance(values, dict):
        return values

    for (key, value) in values.items():
        try:
            if not is_int(value):
                values[key] = parser.parse(value)
        except:
            pass

    return values


def json_loads(data):
    return json.loads(data, object_hook=date_hook)
