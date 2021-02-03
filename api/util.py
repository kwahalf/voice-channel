import json


def jsonify(value,  **kwargs):
    return json.dumps(value, **kwargs)

def dejsonify(string):
    return json.loads(string)


def sanitize_arguments(args):
    return str(args).decode("utf-8")
