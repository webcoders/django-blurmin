
class RequestMixin(object):
    def is_ajax(self):
        if 'json' in self.GET or super(RequestMixin, self).is_ajax():
            return True
        return False


class UIMiddleWare(object):
    def process_request(self, request):
        request.__class__ = type('WSGIRequest', (RequestMixin, request.__class__), {})