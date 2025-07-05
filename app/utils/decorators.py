from functools import wraps
from flask import request, jsonify
import jsonschema
from ..utils.exceptions import InvalidRequestError


def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                raise InvalidRequestError('Request must be JSON', 400)

            try:
                jsonschema.validate(instance=request.json, schema=schema)
            except jsonschema.ValidationError as e:
                raise InvalidRequestError(f'Invalid request data: {e.message}', 400)

            return f(*args, **kwargs)

        return wrapper

    return decorator