from django import forms
from django.conf import settings

class ImageInput(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        _label = self.label
        self.label = ''
        return """
            <div ng-controller="ImageUploadController" ng-init="init('%(media_url)s')" style="display: inline;">
                <label for="inputFirstName" class="col-sm-3 control-label">%(label)s</label>
                <div class="col-sm-9">
                    <div class="userpic">
                        <div class="userpic-wrapper">
                            <img ng-show="%(model)s!=''" ng-src="%(media_url)s{$%(model)s$}" ng-click="openFileBrowser('%(model)s')">
                        </div>
                        <i class="ion-ios-close-outline" ng-click="clearModel('%(model)s')"
                           ng-if="!noPicture"></i>
                        <a href class="change-userpic" ng-click="openFileBrowser('%(model)s')">Change Picture</a>
                        %(field)s
                    </div>
                </div>
            </div>
        """ % {
                'label': _label,
                'media_url': settings.MEDIA_URL,
                'model': self.attrs['ng-model'],
                'field': super(ImageInput, self).render(name, value, attrs=attrs)
               }
