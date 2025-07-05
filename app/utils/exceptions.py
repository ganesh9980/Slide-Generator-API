from flask import jsonify
from werkzeug.exceptions import HTTPException


class InvalidRequestError(HTTPException):
    def __init__(self, message, status_code):
        super().__init__()
        self.code = status_code
        self.description = message


def handle_exception(e):
    if isinstance(e, HTTPException):
        response = jsonify({
            'error': e.description,
            'status_code': e.code
        })
        response.status_code = e.code
        return response

    response = jsonify({
        'error': 'Internal server error',
        'status_code': 500
    })
    response.status_code = 500
    return response