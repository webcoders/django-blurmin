'use strict';

var app = angular.module('BlurAdmin', [
    'ngAnimate',
    'ui.bootstrap',
    'ui.sortable',
    'ui.router',
    'ngTouch',
    'toastr',
    'smart-table',
    "xeditable",
    'ui.slimscroll',
    'ngJsTree',
    'angular-progress-button-styles',
    'BlurAdmin.theme',
    'BlurAdmin.pages',
    'ui.tinymce',
    'ng-currency',
    'ui.mask',
    'ui.form',
    'ui.grid',
    'ui.bootstrap.datetimepicker',
    'ui.datepicker',
    'ui.typeahead',
    'mwl.calendar',
    'angular-loading-bar',
    'angularFileUpload',
    'ngWebSocket',
    'frapontillo.bootstrap-switch',
    'ct.ui.router.extras.core',
    'ct.ui.router.extras.sticky',
    'ct.ui.router.extras.statevis',
    'ngCookies'
]).directive('enterPressed', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {
            if (event.which === 13) {
                scope.$apply(function () {
                    scope.$eval(attrs.enterPressed);
                });

                event.preventDefault();
            }
        });
    };
}).factory('ResponseInterceptor', function ($q, $injector, $location) {
    return {
        response: function (response) {
            return response;
        },
        responseError: function (response) {
            if (response.status == 401) {
                try {
                    var data = JSON.parse(response.data);
                    window.location = data.login_url;
                }
                catch (e) {
                }
                window.location = response.data.login_url;
            }
//          There is some things stopped to work, that is the reason to comment out it
            if ( response.status == 404 ) {
                alert("Sorry. The Record you trying to operate no longer exists. \n" + response.config.url)
                return $q.reject(response)
            }
            var modal = $injector.get('$uibModal');
            var modalInstance = modal.open({
                animation: true,
                size: 'lg',
                templateUrl: '/static/ui/templates/error.html',
            })
            modalInstance.rendered.then(function () {
                document.getElementById('response_error_message').contentWindow.document.write(response.data);
            });
            var _response = {};
            _response.data = []
            return _response
        }
    };

}).factory('RequestInterceptor', function ($q, $injector, $location, $rootScope, $cookies) {
    return {
        request:function(config){
            if ($rootScope.mySessionID != $cookies.get('movingauthority')){
                window.location = '/dashboard/ui/loginview/'
                $rootScope.mySessionID = $cookies.get('movingauthority')
                return $q.reject(config);
            }
            return config;
        }
    }
}).config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$').endSymbol('$}');
}).config(function ($httpProvider) {
    $httpProvider.interceptors.push('RequestInterceptor');
    $httpProvider.interceptors.push('ResponseInterceptor');
}).config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    cfpLoadingBarProvider.includeSpinner = false;
}]).config( function($stickyStateProvider){
     $stickyStateProvider.enableDebug(true);
}).config(function ($httpProvider) {
    $httpProvider.defaults.withCredentials = true;
}).run(['$rootScope','$cookies','$cookieStore', function( $rootScope, $cookies,$cookieStore  ) {
    $rootScope.mySessionID = $cookies.get('movingauthority');
}]);



