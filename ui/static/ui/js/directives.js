/**
 * Created by artem on 01.12.16.
 */

app.directive('inventory', function () {
    return {
        require: 'ngModel',
        templateUrl: '/ui/inventoryview/',
        link: function (scope, element, attrs, ngModelCtrl) {
            $(function () {


            })
        }
    }
})