/**
 * Created by archi on 26.10.16.
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.sticky',
      ['ui.bootstrap',
      'ngAnimate',
      'ngSanitize',
    'ct.ui.router.extras.core',
    'ct.ui.router.extras.sticky',
    'ct.ui.router.extras.statevis',
    'ct.ui.router.extras.dsr'
      ])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider,$stickyStateProvider,$urlRouterProvider) {
  $urlRouterProvider.when('/st', '/st/tabs');
    $stateProvider
        .state('st', {
          url: '/st',
          templateUrl: '/app/pages/sticky/sticky.html',
          title: 'Sticky Example',
          data: { view_mode:'list'},
          controller: function($rootScope,$scope,$stateParams,$state){
            // $rootScope.stateSharedData = {view_mode:'list'}
              $rootScope.$state = $state;
              $rootScope.$on('$stateChangeStart',
                function(event, toState, toParams, fromState, fromParams){
                    // event.currentScope.stateSharedData.view_mode=toState.data.view_mode;
                })
          },
          // sidebarMeta: {
          //   order: 1,
          // },
        })

  $stateProvider.state('st.tabs', {
      url: '/tabs',
      templateUrl: 'tab-viewport.html',
  });

  $stateProvider.state('st.tabs.account', {
      url: '/account',
      sticky: true,
      dsr: true,
      params: {saved: null},
      views: {
          'account': {
              templateUrl: 'account.html'
          }
      },
  });

  $stateProvider.state('st.tabs.account.stuff', {
      url: '/stuff',
      params: {savedStuff: null},
      template: "<h3>Here's my stuff:</h3><ul><li>stuff 1</li><li>stuff 2</li><li>stuff 3</li><li><input type='text' /></li></ul>"
  });

  $stateProvider.state('st.tabs.account.things', {
      url: '/things',
      template: "<h3>Here are my things:</h3><ul><li>thing a</li><li>thing b</li><li>thing c</li></ul>"
  });



  $stateProvider.state('st.tabs.survey', {
      url: '/survey',
      sticky: true,
      dsr: true,
      params: {saved: null},
      views: {
          'survey': {
              templateUrl: 'survey.html'
          }
      }
  });


  $stickyStateProvider.enableDebug(true);

  }

})();