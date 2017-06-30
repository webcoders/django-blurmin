from django.http.response import HttpResponse


class HttpUnauthorized(HttpResponse):
    status_code = 401


class AlreadyRegistered(Exception):
    pass

class ObjectIdentifierIsNotDefined(Exception):
    pass