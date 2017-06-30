from django.forms import widgets

class RichText(widgets.Textarea):
    def render(self, name, value, attrs=None):
        #return super(RichText, self).render(name, value, attrs=attrs)
        self.attrs['ui-tinymce'] = "tinymceOptions"
        return \
        """<div ng-controller="TinyMceController">%s</div>""" % (super(RichText, self).render(name, value, attrs=attrs))