import json


def get_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=4)