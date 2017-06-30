from django.forms import widgets


class Autocomplete(widgets.TextInput):
    autocomplete_view = None

    def __init__(self, autocomplete_view=None, *args, **kwargs):
        self.autocomplete_view = autocomplete_view
        super(Autocomplete, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        self.attrs['autocomplete'] = "off"
        self.attrs["typeahead-loading"] = "loading"
        self.attrs["typeahead-no-results"] = "noResults"
        self.attrs["typeahead-min-length"] = 1
        self.attrs["typeahead-editable"] = 1
        self.attrs["typeahead-on-select"] = "onSelect($item, $model, $label, '%s')" % name
        self.attrs["ng-keyup"] = "keyUp('%s')" % name
        # self.attrs["typeahead-input-formatter"] = "formatInput($model)"

        if self.autocomplete_view:
            self.attrs['uib-typeahead'] = \
                "item[0] as item.slice(1).join(' ') for item in data.getAutocompleteResults($viewValue, '%(name)s', '%(url)s')" % \
                {'name': name, 'url': self.autocomplete_view.get_url()}
        return \
            """
            <div ng-controller="typeaheadController as data" >
                 %(input)s
                 <i ng-show="loading" class="glyphicon glyphicon-refresh"></i>
                 <div ng-show="noResults">
                    <i class="glyphicon glyphicon-remove"></i> No Results Found
                 </div>
            </div>
            """ % {'input': super(Autocomplete, self).render(name, value, attrs=attrs), 'name': name,
                   'model': self.attrs['ng-model']}


class SingleSelect(widgets.Select):
    autocomplete_view = None

    def render(self, name, value, attrs=None):
        self.choices = []
        attrs = ''
        if value is None:
            value = ''
        for k, v in self.attrs.items():
            attrs += '%s="%s" ' % (k, v)
        return """
<div id="%(name)s_ctrl" ng-id="id_%(name)s" ng-url="%(url)s" ng-controller="selectController as data" class="btn-group bootstrap-select form-control">
    <button type="button" class="btn dropdown-toggle btn-default" data-toggle="dropdown" title="Click to select">
        <span id="%(name)s_label" class="filter-option pull-left" ng-bind="selected_title"/>&nbsp;<span class="bs-caret"><span class="caret"></span></span>
    </button>
    <input id="id_%(name)s" name="%(name)s" ng-model="%(ng_model)s" type="hidden" value="%(value)s"/>
    <div class="dropdown-menu open" style="max-height: 260px; overflow: hidden;">
        <div class="searchbox">
            <input type="text" placeholder="Type to search" class="form-control" autocomplete="off" ng-model="search_data">
        </div>
        <ul class="dropdown-menu inner" role="menu" style="max-height: 250px; overflow-y: auto;">
            <li ng-repeat="item in data" ng-class="{'active selected': item[0] == selected_id}">
                <a href ng-click="itemSelect(item, '%(ng_model)s')"><span class="text">{$ item.slice(1).join(' ') $}</span></span></a>
            </li>
            <li ng-show="data.length==0 && search_data.length>0" class="no-results" style="display: list-item;">No results matched</li>
        </ul>
    </div>
</div>


        """ % {
            'ng_model': self.attrs['ng-model'],
            'name': name,
            'attrs': attrs,
            'value': value,
            'url': self.autocomplete_view.get_url()}
