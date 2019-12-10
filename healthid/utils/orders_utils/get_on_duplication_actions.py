import json


def get_on_duplication_actions(on_duplication):
    try:
        on_duplication = json.loads(on_duplication)
        for key in on_duplication:
            value = on_duplication[key]
            del on_duplication[key]
            on_duplication[key.lower()] = value
    except Exception:
        on_duplication = {}
    return on_duplication
