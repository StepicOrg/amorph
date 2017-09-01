import requests
from schema import Schema, Use, SchemaError

from amorph.models import Patch
from amorph.exceptions import InvalidApiResponseException


def PositiveInt():
    return Use(int, lambda x: x > 0)

raw_patches_schema = Schema([
    {
        'type': 'delete',
        'start': PositiveInt(),
        'stop': PositiveInt()
    }, {
        'type': 'insert',
        'pos': PositiveInt(),
        'text': Use(str)
    }, {
        'type': 'update',
        'start': PositiveInt(),
        'stop': PositiveInt(),
        'text': Use(str),
    }
])


def get_patches(source: str, target: str, api_endpoint: str = 'http://localhost:4567/api/diff'):
    result = requests.post(api_endpoint, {
        'src': source,
        'dst': target
    })

    if result.status_code != 200:
        raise InvalidApiResponseException('Http code {}. Response: "{}"'.format(
            result.status_code,
            result.text
        ))

    try:
        raw_patches = result.json()
    except ValueError:
        raise InvalidApiResponseException('Invalid JSON given')

    try:
        raw_patches = raw_patches_schema.validate(raw_patches)
    except SchemaError:
        raise InvalidApiResponseException('Invalid raw patches schema')

    try:
        return [Patch.from_dict(patch) for patch in raw_patches]
    except Exception:
        raise InvalidApiResponseException('Invalid raw patches')
