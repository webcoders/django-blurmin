/**
 * Created by artem on 10.12.16.
 */

app.controller('editableGridCtrl', function($scope, $controller) {
  $controller('gridController', {$scope: $scope});
});