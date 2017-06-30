from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseForbidden
from django.utils.decorators import classonlymethod
import json
from ui.auth.mixins import LoginRequiredMixin
from ui.exceptions import HttpUnauthorized
from ui.serializers.json_encoder import UiJSONEncoder

class BaseView(LoginRequiredMixin, object):
    @classonlymethod
    def urlpattern(cls):
        return r'^%s/((change/?)|(create/?))?$' % (cls.__name__.lower())
        #return r'^%s/$' % (cls.__name__.lower())

    @classmethod
    def url_name(cls):
        return cls.__name__.lower()

    @classonlymethod
    def rendered_content(cls, request):
        func_result = cls.as_view()(request)
        if isinstance(func_result, HttpUnauthorized):
            return "<script>window.location='%s?%s=/#%s'</script>" % (func_result.params['login_url'],
                                                               func_result.params['redirect_field_name'],
                                                               func_result.params['full_path'])
        if isinstance(func_result, HttpResponseForbidden):
            return "You don't have permissions."
        return func_result.render().content

    @classmethod
    def get_url(cls):
        return reverse(cls.url_name())

    def serialize(self, data):
        return HttpResponse(json.dumps(data, cls=UiJSONEncoder))

    def deserialize(self, data):
        return json.loads(data)


