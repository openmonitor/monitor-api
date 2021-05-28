import json
import typing


def load_body(req) -> typing.Union[None, dict]:
    try:
        return json.loads(req.stream.read())
    except json.decoder.JSONDecodeError:
        return None


def body_contains_requirements(
    body: dict,
    *args,
) -> bool:
    for arg in args:
        if not body.get(arg):
            return False
    return True
