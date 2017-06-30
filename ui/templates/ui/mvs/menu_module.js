(function () {
  'use strict';

  angular.module('BlurAdmin.pages.{{ state_name }}',
      ['ui.bootstrap',
      'ngAnimate',
      'ngSanitize',
      ])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider,$urlRouterProvider) {
    $urlRouterProvider.when('/{{ state_name }}', '/{{ state_name }}/list/');
    $stateProvider
        .state('{{ parent_state }}{{ state_name }}', {
          url: '/{{ state_name }}',
          templateUrl: '{{ state_url }}',
          title: '{{ title }}',
          controller: function($rootScope,$scope,$stateParams){
            $rootScope.stateSharedData = {view_mode:'list'}
              $rootScope.$on('$stateChangeStart',
                function(event, toState, toParams, fromState, fromParams){
                    if ( toState.data && toState.data.view_mode ) {
                        event.currentScope.stateSharedData.view_mode = toState.data.view_mode;
                    }
                })
          },
          sidebarMeta: {
            icon: '{{ item.icon }}',
            order: 100,
          },
        }).state('{{ parent_state }}{{ state_name }}.list', {
// {id:[0-9A-Z]{6}}
            url: "/list",
            data: { view_mode:'list'},
            views: {'list': { templateUrl: '{{ list_url }}',
                    controller: function($rootScope,$scope,$stateParams) {
                        $rootScope.stateSharedData = {view_mode:'list'}
                    }
            }}
        }).state('{{ parent_state }}{{ state_name }}.change', {
// {id:[0-9A-Z]{6}}
            url: "/change/{id:{%if row_id_field_name != 'slug' %}[0-9]{0,10}{% else %}[0-9A-Z]{0,6}{% endif %} }",
            data: { view_mode:'change'},
            views: {'change': { templateUrl: '{{ change_url }}',
                    controller: function($rootScope,$scope,$stateParams) {
                        $rootScope.stateSharedData = {view_mode:'change'}
                        if ( $stateParams.id ) {
                            if ($scope.editable) {
                                $scope.editable.record_id = $stateParams['id'];
                            } else {
                                $scope.editable = {record_id :$stateParams['id']};
                            }
                        }
                        // $scope.editable.view_mode = 'record';
                    }
            }}
        });
  }

})();