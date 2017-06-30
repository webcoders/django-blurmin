NG_MODEL_PREFIX = 'form.fields.'


class Widget(object):
    def render(self, name, value, attrs=None):
        self.ng_obj = NG_MODEL_PREFIX + name
        self.attrs['ng-model'] = '%s.value' % self.ng_obj
        return super(Widget, self).render(name, value, attrs=attrs)


class BootstrapWidget(Widget):
    def render(self, name, value, attrs=None):
        rendered_field = super(BootstrapWidget, self).render(name, value, attrs=attrs)

        if self.is_required:
            self.attrs['required'] = ""
        is_required = ""
        div_position = ""
        if self.is_required == True:
            is_required = "!True"
        if 'label_position' in self.attrs:
            label = label_position = self.attrs['label_position']
        else:
            label = "vertical"
        if 'div_position' in self.attrs:
            div_position = self.attrs['div_position']

        if label == "horizontal":
            if self.label:
                label_position = "col-sm-2 label-pos-h1"
                div_position = (div_position if div_position else "col-sm-10")
            else:
                label_position = "label-pos-h"
                div_position = (div_position if div_position else "col-sm-12")

        if label == "vertical":
            label_position = "col-md-12 label-pos-v"
            div_position = (div_position if div_position else "col-sm-12 ")

        return """
                    <div class="form-group" ng-class="{'has-error':%(ng_obj)s.error,'has-success':(bound && !%(ng_obj)s.error)}">
                        <div class="row">
                            <div class="%(label_position)s">%(label)s<span ng-show="%(is_required)s"  style="color:#e85656"> *</span></div>
                            <div class="%(div_position)s">
                                <span ng-show="!%(ng_obj)s.is_readonly">
                                %(field)s
                                </span>
                                <span ng-show="%(ng_obj)s.is_readonly" ng-bind-html="%(ng_obj)s.readonly_value" class="readonly"></span>
                                <span ng-bind-html="%(ng_obj)s.help_text_and_error" ng-show="%(ng_obj)s.help_text_and_error" class="help-block"></span>
                            </div>
                        </div>
                    </div>
                    """ % {
            "ng_obj": self.ng_obj,
            "field": rendered_field,
            "label": self.label,
            "is_required": is_required,
            "label_position": label_position,
            "div_position": div_position
        }


def invert_color(color):
    color = color.replace('#', '')
    r, g, b = tuple(ord(c) for c in color.decode('hex'))
    if (r * 0.299 + g * 0.587 + b * 0.114) > 150:
        return 'rgba(0, 0, 0, 0.75)'
    else:
        return '#ffffff'
