from flask import jsonify

class InitError(Exception):
    status_code = 400


class PageNotFound(Exception):
    status_code = 404

    def __init__(self, message, payload=None):
        Exception.__init__(self, message)
        self.message = message
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
