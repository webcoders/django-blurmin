/**
 * Created by archi on 18.10.16.
 */
var ui_form = angular.module('ui.form', [])

// http://stackoverflow.com/questions/23813413/how-to-programmatically-submit-a-form-with-angularjs
/*ui_form.directive('form', function() {
    return {
        require: 'form',
        restrict: 'E',
        link: function(scope, elem, attrs, form) {
            form.$submit = function() {
                form.$setSubmitted();
                scope.$eval(attrs.ngSubmit);
            };
        }
    };
});*/
// http://stackoverflow.com/questions/27690230/how-to-trigger-form-submit-programmatically-in-angularjs


ui_form.factory('forms', ['$filter', '$http', '$httpParamSerializerJQLike','$uibModal','$q', function ($filter, $http, $httpParamSerializerJQLike, $uibModal,$q) {
    return {
        addHelpTextAndErrors: function (fields_binding) {
            var is_valid = true;
            for (var field in fields_binding) {
                if (fields_binding.hasOwnProperty(field)) {
                    fields_binding[field].help_text_and_error = ((fields_binding[field].help_text ? fields_binding[field].help_text : '') +
                    (fields_binding[field].error ? fields_binding[field].error : ''))
                    if (fields_binding[field].error) {
                        is_valid = false;
                    }
                }
            }
            return is_valid;
        },
        prepareValues: function (fields_binding, out) {
            for (var field in fields_binding) {
                fields_binding[field].value = this.prepareValue(field, fields_binding[field], out);
            }
        },
        prepareValue: function (field_name, field, out) {
            var direction = out ? 'out' : 'in';
            if (this.dataTransformers.hasOwnProperty(field.data_type + '_' + direction)) {
                return this.dataTransformers[field.data_type + '_' + direction](field.value);
            }
            if (field.data_type == 'modelchoice_ac' && out != true){
                var data = JSON.parse(field.value)[0]
                var label = data.slice(1).join(' ');
                angular.element('#' + field_name + '_label')[0].innerHTML = label;
                return data[0]
            }
            return field.value;
        },

        dataTransformers: {
            // date_in : function (data_value) {
            //     return new Date(data_value);
            //  },
            // date_out : function (model_value) {
            //     return $filter('date')(model_value,'yyyy-MM-dd');
            // },
            modelchoice_in: function (data_value) {
                return String(data_value);
            }
        },
        harvestFormData: function (form_el, model) {
            var data = {}
            angular.forEach(form_el.find('input'), function (value, key) {
                data[value.name] = model.hasOwnProperty(value.name) ? this.prepareValue(value.name, model[value.name], true) : angular.element(value).val();
            }, this)

            angular.forEach(form_el.find('textarea'), function (value, key) {
                data[value.name] = model.hasOwnProperty(value.name) ? this.prepareValue(value.name, model[value.name], true) : angular.element(value).val();
            }, this)

            angular.forEach(form_el.find('select'), function (value, key) {
                if (model[value.name]!=undefined && model[value.name].data_type == "modelmultiplechoice" && angular.element(value).attr('ui-multiselect-wide')) {
                    data[value.name] = []
                    var options = angular.element(value).find('option');
                    for (var i = 0; i < options.length; i++) {
                        data[value.name].push(options[i].value)
                    }
                    data[value.name] = JSON.stringify(data[value.name])
                }
                else {
                    data[value.name] = model.hasOwnProperty(value.name) ? this.prepareValue(value.name, model[value.name], true) : angular.element(value).val();
                }
            }, this)
            return data;
        },
        post: function (url, data) {
            var fd = new FormData();
            for (var key in data) {
                if (!(data[key] === null)) {
                    fd.append(key, data[key]);
                }
            }

            return $http({
                url: url,
                method: 'POST',
                data: fd,
                headers: { 'Content-Type': undefined},
                transformRequest: angular.identity
            })

/*                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                transformRequest: function(obj) {
                    var str = [];
                    for(var p in obj) {
                        if (!(obj[p] === null)) {
                            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                        }
                    }
                    return str.join("&");
                },*/


            /*            return $http({
                url: url,
                method: 'POST',
                data: $httpParamSerializerJQLike(data),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })*/
        },
        deleteDialog: function (url,id,multi,extra_data) {
            var modal = $uibModal;
            var modalInstance = modal.open({
                animation: true,
                templateUrl: 'delete-confirmation.html',
                controller: 'GridDeleteConfirmCtrl',
                resolve: {
                    param: function () {
                        return {
                            'extra_data': extra_data,
                            'ids': id,
                            'url': url
                        };
                    }
                }
            });
            return modalInstance.result.then(function (value) {
                var value = value;
                if (value == 'Yes') {
//TODO cannot access module functions inside module function!!!
                    return this.post(url + '/delete/' + (multi ? '?multi=1' : id) , {ids: JSON.stringify(id)})
                       .success(function (response) {
                        if (response.message == 'success') {
                            toastr.success('Successfully deleted');
                        } else {
                            toastr.error(response.message);
                        }
                    })
                } else {
                    return $q(function(resolve){
                        resolve(value);
                    })
                }
            });
        }


    }
}])

ui_form.controller('formController', ['$scope', '$attrs', '$http', 'forms', '$state','$uibModal' , 'toastr', function ($scope, $attrs, $http, forms, $state, $uibModal,toastr) {
        var gridform = this;

        $scope.record_id = '';
        $scope.record = null;
        $scope.form = {fields: eval($attrs.uiInitial), errors: ''}
        $scope.for_childs = {};
        $scope.action = 'save';
        var url = $attrs.url;
        if (String(url).endsWith('/')) {
            url = url.slice(0, -1);
        }
        var row_id_field_name = $attrs.rowIdFieldName;
        var type = $attrs.formType ? $attrs.formType : 'standalone';
        $scope.bound = false;
        $scope.rowform = {'visible': false, 'waiting': false};
        var grid_view_name = $attrs.gridViewName;
        var related_grid = null;
        var state_driven = $attrs.stateDriven;

        if ( state_driven ) {
            related_grid = $scope.stateSharedData[grid_view_name].grid;
        } else {
            if (related_grid = $scope[grid_view_name]!=undefined){
                related_grid = $scope[grid_view_name].editable.grid;
            }
        }

        $scope.setAction = function(a){
            $scope.action= a;
        }


        $scope.initForm = function (data) {
            if (data.form) {
                angular.extend($scope.form, data.form);
                forms.addHelpTextAndErrors($scope.form.fields);
            }
            if (data.record) {
                $scope.record = data.record;
                $scope.record_id = data.record[row_id_field_name]
                type = 'grid-row';
                if ( !$scope.record_id ) {
                   $scope.rowform.visible = true;
                }
            }
        }

        $scope.getRecordUrl = function (id) {
            if (type == 'change') {
                return url + "?" + type + '=y&json'
            }
            //TODO remove this 'change/' has or not check, this is added for viewset support !
            var id_param = ''
            if ( id ) {
                id_param = (row_id_field_name == 'slug' ? 'slug=' : 'pk=') + id
            }
            var r = url + ((!String(url).endsWith('change')) ? '/change' : '') + '/?' + (id_param ? id_param + '&' : '') + type + '=y&json';
            return r
        }

        $scope.delete = function () {
            var modal = $uibModal;
            var modalInstance = modal.open({
                animation: true,
                templateUrl: 'delete-confirmation.html',
                controller: 'GridDeleteConfirmCtrl',
                resolve: {
                    param: function () {
                        return {
                            'extra_data': $scope.record_id,
                        };
                    }
                }
            });
            modalInstance.result.then(function (value) {
                var value = value;
                if (value == 'Yes') {
                    var url = (('/change/') ? $attrs.url.replace('/change/','') : '') + '/delete/'
                    if ( $attrs.deleteUrl ){
                      url = $attrs.deleteUrl;
                    }
                    url = url + '?' +  ( row_id_field_name == 'id' ? 'pk' : row_id_field_name ) +'='+$scope.record_id;
                    forms.post(url).success(function (response) {
                        if (response.message == 'success') {
                            toastr.success('Successfully deleted');
                            if ( type == 'grid-row' ) {
                                related_grid.removeRow($scope.record.$$hashKey);
                            } else {
                                related_grid.getData(1);
                            }
                            if ( state_driven ){
                                $state.go($state.$current.parent);
                            }
                        } else {
                            toastr.error(response.message);
                        }
                    })
                }
            });
        }

        $scope.getRecordData = function (id) {
            $http.get($scope.getRecordUrl(id)).success(function (response) {
                    $scope.form = response;
                    $scope.record_id = id;
                    if (type == 'grid-change') {
                        if ( state_driven ) {
                            $scope.record = related_grid.getRecord($scope.record_id);
                        } else {
                            $scope.record = $scope[grid_view_name].editable.record;
                        }
                    }
                    forms.addHelpTextAndErrors($scope.form.fields);
                    forms.prepareValues($scope.form.fields);
                    $scope.$broadcast('data_received', {'view_name': related_grid.uiViewName, 'data': response});
                }
            )
        }

        $scope.cancelEdit = function() {
            if ( !$scope.record_id ){
                related_grid.removeRow($scope.record.$$hashKey);
            } else {
                angular.forEach($scope.record, function (value, key) {
                    if ($scope.form.fields.hasOwnProperty(key)) {
                        $scope.form.fields[key].value = value;
                    }
                }, this)
            }
            $scope.rowform.visible = false;
        }

        $scope.updateGridRecord = function () {
            var record=null;
            if ($scope.record_id && !$scope.record ) {
                record = related_grid.getRecord($scope.record_id);
                if ( record ) {
                    $scope.record = record;
                }
            } else {
                // for inline grid-row adding row!!!!
                $scope.record_id = $scope.form.record_id;
                $scope.record[row_id_field_name]=$scope.form.record_id;
            }
            if ( $scope.record ) {
                angular.forEach($scope.form.fields, function (value, key) {
                    if ($scope.record.hasOwnProperty(key)) {
                        $scope.record[key] = value.value;
                    }
                }, this)
            }

            $scope.$emit('data_changed', {'view_name': grid_view_name, 'action': 'update', 'rows': related_grid.data.object_list});
            $scope.rowform.visible = false;
        }

        $scope.setRecordData = function () {
            if ( $scope.for_childs.before_submit ){
                if ( !$scope.for_childs.before_submit() ) {
                    return;
                }
            }
            if ($scope.record_id) {
                $scope.send($scope.getRecordUrl($scope.record_id));
                return;
            }
            $scope.send(url + '/?create=');
        }

        $scope.afterSubmit = function (fields_valid){
                if ( $scope.for_childs.after_submit ) {
                    if ( !$scope.for_childs.after_submit(fields_valid,$scope) ) {
                        return;
                    }
                }
                if ($scope.form.errors.length == 0 && fields_valid) {
                  if ( !$scope.record_id ) {
                        toastr.success('Created');
                        if ( type != 'grid-row' ) {
                            if ( $scope.action == 'save_and_continue' ) {
                                $scope.updateGridRecord();
                                $state.go($state.current, {id: $scope.form.record_id})
                                return
                            }
                        }
                    }
                    toastr.success('Saved');
                    $scope.updateGridRecord();
                    if ( type != 'grid-row' && $scope.action != 'save_and_continue' ) {
                        $state.go($state.$current.parent)
                    }
                } else {
                    toastr.error('Please correct the errors');
                }
        }


        $scope.send = function (url) {
            $scope.$broadcast('before_form_save', {'view_name': grid_view_name});
            var data = forms.harvestFormData($attrs.$$element, $scope.form.fields)
            forms.post(url, data).success(function (response) {
                if ( !typeof(response) === "object" ) {
                    toastr.error('Sorry, internal server error');
                    return
                }
                $scope.form = response;
                $scope.bound = true;
                var fields_valid = forms.addHelpTextAndErrors($scope.form.fields);
                forms.prepareValues($scope.form.fields);
                $scope.afterSubmit(fields_valid);
                $scope.$broadcast('data_received', {'view_name': related_grid.uiViewName, 'data': response});

            })
        }

        if (type == 'grid-change') {
            if ( state_driven && $state.params.id ) {
                $scope.getRecordData($state.params.id);
            } else {
                $scope.$watch(grid_view_name + '.editable.record_id', function (newValue, oldValue) {
                    if (newValue) {
                        $scope.getRecordData(newValue);
                    }
                });
            }
        }
        if (type == 'change')
            $scope.getRecordData($attrs.ngId);
    }
    ]
);

var ui_grid = angular.module('ui.grid',[])
    .filter('trust', [
        '$sce',
        function ($sce) {
            return function (value, type) {
                // Defaults to treating trusted text as `html`
                return $sce.trustAs(type || 'html', value);
            }
        }
    ]);


// ui_grid.directive('bindHtmlCompile', ['$compile', function ($compile) {
//         return {
//             restrict: 'A',
//             link: function (scope, element, attrs) {
//                 scope.$watch(function () {
//                     return scope.$eval(attrs.bindHtmlCompile);
//                 }, function (value) {
//                     // In case value is a TrustedValueHolderType, sometimes it
//                     // needs to be explicitly called into a string in order to
//                     // get the HTML string.
//                     element.html(value && value.toString());
//                     // If scope is provided use it, otherwise use parent scope
//                     var compileScope = scope;
//                     if (attrs.bindHtmlScope) {
//                         compileScope = scope.$eval(attrs.bindHtmlScope);
//                     }
//                     $compile(element.contents())(compileScope);
//                 });
//             }
//         };
//     }]);

ui_grid.controller('gridController', ['$scope', '$http', '$attrs', 'forms', '$state','$uibModal','toastr','$cookies', function ($scope, $http, $attrs, forms, $state,$uibModal, toastr, $cookies) {
    var parentScope = $scope.$parent;
    parentScope.child = $scope;
    var data = this;
    data.object_list = [];
    data.list_filter = [];
    data.pagenum = 1;
    data.total_items = 0;
    data.extra_data = {};
    data.page_size = parseInt($attrs.uiPaginatedBy);
    data.sorted_fields = [];
    data.filters = []
    data.row_selector = {all:false,id:{}}
    data.inline_form = {};
    $scope.form = {fields: {}, errors: ''}
    $scope.urls = { url:$attrs.url, base: $attrs.url.endsWith('/list/') ? $attrs.url.replace('/list/','') : '' }
    $scope.uiViewName = $attrs.uiViewName



    var row_id_field_name = $attrs.rowIdFieldName;
    // $scope.view_mode = 'table';
    if ($scope.hasOwnProperty($attrs.uiViewName)) {
        $scope[$attrs.uiViewName].editable.view_mode = 'table';
    } else {
        $scope[$attrs.uiViewName]= {editable :{view_mode: 'table', grid : $scope}};
    }

    if ($scope.stateSharedData.hasOwnProperty($scope.uiViewName)) {
        $scope.stateSharedData[$scope.uiViewName].grid = $scope;
    } else {
        $scope.stateSharedData[$scope.uiViewName] = { grid : $scope };
    }

    data.calcTableHeight = function () {
        document.getElementById($attrs.uiViewName + 'Table').style.height = (document.getElementById($attrs.uiViewName + 'Table').rows[0].offsetHeight * data.page_size).toString() + 'px';
    }

    $scope.initGrid = function(initial_data){
        if (initial_data.inline_form){
            data.inline_form = initial_data.inline_form
        }
    }

    angular.element(document).ready(function () {
        data.calcTableHeight();
    });

    $scope.addRow = function() {
        row = angular.copy(data.inline_form)
//TODO this is not correct because column list may differ from form fields, this is down due to absence of column list in controller !!!!
        for (var k in data.inline_form.__inputs) {
            row[k]='';
        }
        data.object_list.push(row)
        $scope.$emit('data_changed', {'view_name': $scope.uiViewName, 'action': 'add', 'rows': data.object_list});
    }

    $scope.removeRow = function (hashKey) {
         for (var obj in data.object_list){
            if ( data.object_list[obj].$$hashKey == hashKey )  {
                data.object_list.splice(obj,1);
                $scope.$emit('data_changed', {'view_name': $scope.uiViewName, 'action': 'delete', 'rows': data.object_list});
                return;
            }
         }
    }

    data.updateSelected = function (id){
        if (!data.row_selector.id[id]){
            delete data.row_selector.id[id];
            data.row_selector.all = false;
        }
    }
    data.selectAll = function(){
        if ( data.row_selector.all ){
           for (var obj in data.object_list){
               //row_id_field_name
               data.row_selector.id[data.object_list[obj]['slug']] = true;
           }
        } else {
            data.row_selector.id = {}
        }
    }
    data.selectedCount = function(){ c=0; for (i in data.row_selector.id) ++c; return c; }

    data.restoreSelectAll = function(){
           for (var obj in data.object_list){
               if (!data.row_selector.id[data.object_list[obj]['slug']]){
                    data.row_selector.all = false;
                    return
               }
               //row_id_field_name
           }
           data.row_selector.all = true;
    }


    $scope.deleteSelectedDialog = function () {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: 'delete-confirmation.html',
            controller: 'GridDeleteConfirmCtrl',
            resolve: {
                param: function () {
                    return {
                        'extra_data': $scope.data.selectedCount(),
                        'ids': $scope.data.row_selector.id,
                        'url': $scope.urls.base
                    };
                }
            }
        });
        modalInstance.result.then(function (value) {
            var value = value;
            if (value == 'Yes') {
                var url = '';
                if ( $attrs.deleteUrl ){
                  url = $attrs.deleteUrl;
                } else {
                  url = $scope.urls.base + '/delete/'
                }

                forms.post(url + '?multi=1',{ids:JSON.stringify($scope.data.row_selector.id)}).success(function (response) {
                    if (response.message == 'success') {
                        toastr.success('Successfully deleted');
                        $scope.getData(1);
                    } else {
                        toastr.error(response.message);
                    }
                })
            }
        });
    };

    $scope.initFilterFormFields = function (data) {
        forms.addHelpTextAndErrors(data);
        angular.extend($scope.form.fields, data.fields)
    }

    $scope.editRow = function (record) {
        $scope[$attrs.uiViewName].editable.view_mode = 'record';
        $scope[$attrs.uiViewName].editable.record_id = record[row_id_field_name];
        $scope[$attrs.uiViewName].editable.record = record
    }

    $scope.getRecord = function(id){
       for (var value in data.object_list) {
                if (id == data.object_list[value][row_id_field_name]) {
                    return data.object_list[value];
                }
       }
       return null;
    }

    data.sortElemActive = function (field) {
        if (data.sorted_fields.indexOf(field) >= 0)
            return true;
        return false
    }

    data.changeSort = function (field) {
        if (data.sorted_fields.indexOf(field) >= 0)
            data.setSort('-' + field)
        else
            data.setSort(field)
    }

    data.getSortNumber = function (field) {
        i = data.sorted_fields.indexOf(field);
        if (i >= 0) {
            return i + 1;
        }
        i = data.sorted_fields.indexOf('-' + field)
        if (i >= 0) {
            return i + 1;
        }
    }

    data.removeSort = function (field) {
        data.sorted_fields.splice(data.sorted_fields.indexOf(field), 1);
        $scope.getData(data.pagenum, data.page_size)
    }

    data.filterGetFieldList = function () {
        var result = []
        data.list_filter.forEach(function (l_filter) {
            field = l_filter.field;
            var exist = false
            data.filters.forEach(function (filter) {
                if (filter.field != undefined && field == filter.field.field) {
                    exist = true;
                }
            })
            if (!exist) {
                result.push(l_filter)
            }
        })
        return result;
    }

    data.setSort = function (field) {
        if (data.sortElemActive(field)) {
            data.sorted_fields.splice(data.sorted_fields.indexOf(field), 1)
        } else {
            if (field[0] == '-') {
                f = field.substr(1)
                i = data.sorted_fields.indexOf(f)
                if (i >= 0)
                    data.sorted_fields.splice(i, 1)
            } else {
                f = '-' + field
                i = data.sorted_fields.indexOf(f)
                if (i >= 0)
                    data.sorted_fields.splice(i, 1)
            }
            data.sorted_fields.push(field)
        }
        $scope.getData(data.pagenum, data.page_size)
    }

    $scope.getData = function (pagenum, per_page) {
        if (pagenum == '...')
            return
        if (per_page != undefined) {
            data.page_size = per_page
            data.calcTableHeight();

        } else if (pagenum == null /*|| pagenum == data.number*/)
            return

        var to_send = forms.harvestFormData($attrs.$$element, $scope.form.fields)

        to_send.perpage = data.page_size;
        to_send.page = pagenum;
        to_send.json = true;
        to_send.sort = JSON.stringify(data.sorted_fields)
        if (Object.keys(data.extra_data).length > 0)
            to_send.extra = JSON.stringify(data.extra_data)
        data.filters.forEach(function (filter) {
            if (filter.hasOwnProperty('condition') && filter.condition) {
                to_send[filter.field.field + '-condition'] = filter.condition.name
            }
        })

        data.object_list = [];
        document.getElementById($attrs.uiViewName + 'Table').style.visibility = 'hidden'
        // "/dashboard/ui/" + $attrs.uiViewName.toLowerCase() + "/"
        $http.get($attrs.url,
            {
                params: to_send
            }).success(function (response) {
            document.getElementById($attrs.uiViewName + 'Table').style.visibility = 'visible'
            if (response.hasOwnProperty('object_list')) {
                if (response.object_list.length < data.page_size) {
                    document.getElementById($attrs.uiViewName + 'Table').style.height = 'auto';
                }
                else {
                    if (document.getElementById($attrs.uiViewName + 'Table').style.height == 'auto')
                        data.calcTableHeight();
                }
                data.object_list = response.object_list;
                data.total_items = response.total_items;
                data.has_previous = response.has_previous;
                data.next_page_number = response.next_page_number;
                data.previous_page_number = response.previous_page_number;
                data.has_next = response.has_next;
                data.page_size = response.page_size;
                data.page_range = response.page_range;
                data.number = response.number;
                data.per_page_list = response.per_page_list;
                data.list_filter = response.list_filter;
                $scope.$emit('data_received', {'view_name': $scope.uiViewName, 'rows': data.object_list});
                if (data.list_filter.length > 0 && data.filters.length == 0) {
                    data.filters.push({})
                }
                data.restoreSelectAll();
            } else {
                forms.addHelpTextAndErrors(response.fields);
                $scope.form = response;
                $scope.bound = true;
            }
        });
    };
    $scope.getData(data.pagenum);
}]).config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$').endSymbol('$}');
});

app.controller('GridDeleteConfirmCtrl', function ($scope, $uibModalInstance,toastr,forms,param) {
    $scope.record_count = param.extra_data;
    $scope.ok = function (value) {
/*        forms.post(param.url + '/delete/?multi=1',{ids:JSON.stringify(param.ids)}).success(function (response) {
            if ( response.message == 'success'){
                toastr.success('Successfully deleted');
            } else {
                toastr.error(response.message);
            }*/
            $uibModalInstance.close(value);
        //})
    };
    $scope.cancel = function (value) {
        $uibModalInstance.close(value);
    };

})


var ui_datepicker = angular.module('ui.datepicker', [])
ui_datepicker.controller('datepickerController', ['$scope', '$http', '$attrs', function ($scope, $http, $attrs) {
        var that = this;
        this.picker = {
            datepickerOptions: {
                startingDay: 1,
                defaultTime: '00:00:00',
                dateDisabled: function (data) {
                    return (data.mode === 'day' && (new Date().toDateString() == data.date.toDateString()));
                }
            }
        };
        this.openCalendar = function (e, picker) {
            that[picker].open = true;
        };
    }]
);

var ui_typeahead = angular.module('ui.typeahead', [])
ui_typeahead.controller('typeaheadController', ['$scope', '$http', '$attrs', function ($scope, $http, $attrs) {
        var that = this;

        var data = []

        $scope.formatInput = function(model) {
            for (var i=0; i< data.length; i++) {
                 if (model === data[i][0]) {
                     return data[i].slice(1).join(' ');
                 }
            }
        }

        $scope.onSelect = function ($item, $model, $label, field_name) {
            angular.element('#id_' + field_name)[0].setAttribute('data', $item);
        };

        $scope.keyUp = function (field_name) {
            angular.element('#id_' + field_name)[0].setAttribute('data', '');
        };

        this.getAutocompleteResults = function (val, field, url) {
            return $http.get(url, {
                params: {
                    query: val,
                    json: true
                }
            }).then(function (response) {
                data = response.data.data;
                return response.data.data.map(function (item) {
                    return item;
                });
            });
        }
    }]
);

app.controller('selectController', ['$scope', '$http', '$attrs', '$parse', function ($scope, $http, $attrs, $parse) {

    $scope.data = [];
    $scope.selected_title = "";
    $scope.selected_id = "";

    $scope.itemSelect = function (item, model_name) {
        $scope.selected_title = item.slice(1).join(' ');
        $scope.selected_id = item[0].toString();
        $parse(model_name).assign($scope, $scope.selected_id);
    }

    $scope.$watch('search_data', function(newValue, oldValue) {
        if (newValue==undefined || newValue=='')
          return;
        $http.get($attrs.ngUrl, {
                params: {
                    query: newValue,
                    json: true
                }
            }).then(function (response) {
                $scope.data = response.data.data;
        });
    });

}])

var ui_multiselect = angular.module('ui.multiselect', [])
ui_multiselect.controller('multiselectController', ['$scope', '$http', '$attrs', function ($scope, $http, $attrs) {

        var selectedItems = {};
        $scope.extra_params = {};

        this.transfer = function (from, to, index) {
            if (index >= 0) {
                to.push(from[index]);
                from.splice(index, 1);
            } else {
                for (var i = 0; i < from.length; i++) {
                    to.push(from[i]);
                }
                from.length = 0;
            }
        };

        $scope.init = function(){
           $scope.$on('update_'+$scope.scope_id, function (event, data) {
               angular.extend($scope, data);
               if ( $scope.searchTerm ) {
                   $scope.onChange();
               }
           })


           $scope.$watchCollection($scope.ng_model, function (newValue, oldValue) {
               if (newValue == undefined) {
                   return
               }
               selectedItems = {}
                for (var  i= 0; i< newValue.length;i++ ){
                    selectedItems[newValue[i].id]=true;
                }
           })

        }

        $scope.onChange = function () {
            if ($scope.total_count > $scope.data.length) {
                var p = $scope.extra_params;
                angular.extend(p,{
                        query: $scope.searchTerm,
                        json: true
                })
                return $http.get($scope.url, {
                    params: p
                }).then(function (response) {
                    var data = response.data.data;
                    $scope.data = []
                    for (var i in data) {
                        if ( !selectedItems.hasOwnProperty([data[i][0]]) ) {
                            $scope.data.push({id: data[i][0], unicode: data[i].slice(1).join(' ')})
                        }
                    }
                });
            }
        }

    }]
)

app.controller('ModalInstanceCtrl', function ($scope, $uibModalInstance) {
    $scope.ok = function (value) {
        $uibModalInstance.close(value);
    };
});

app.controller('TinyMceController', ['$scope', '$uibModal', function ($scope, $uibModal) {
    var _data = this;

    function custom_file_browser(field_name, url, type, win) {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/filebrowserdialog/',
            controller: 'ModalInstanceCtrl',
            windowClass: 'modal-fit',
        });
        modalInstance.result.then(function (value) {
            win.document.getElementById(field_name).value = value;
        });
    }

    $scope.tinymceOptions = {
        plugins: 'link image code fullscreen media autolink lists layer table save',
        height: '500px',
        file_browser_callback: custom_file_browser,
        relative_urls : false,
        remove_script_host : true,
//        image_prepend_url:'http://devel/'
    };
}]);

app.controller('OperationsCalendarCtrl', ['$scope', '$http', 'moment', function ($scope, $http, moment) {
    var vm = this;

    //These variables MUST be set as a minimum for the calendar to work
    vm.calendarView = 'month';
    vm.viewDate = new Date();

    var actions = [{
        label: '<i class=\'fa fa-truck\'></i>',
        onClick: function (args) {
            //args.calendarEvent
            window.location = args.calendarEvent.action_url;
        }
    }];

    moment.locale('en_gb', {
        week: {
            dow: 1 // Monday is the first day of the week
        }
    });

    vm.events = [];
    $scope.filter_status_value = 'Booked';
    $scope.filter_distance_value = 'Local Moving';

    vm.sendData = function () {
        var params = {}
        params.json = true;
        params.filter_status_value = $scope.filter_status_value;
        params.filter_distance_value = $scope.filter_distance_value;
        $http.get("/dashboard/ui/operationscalendaradminpage/",
            {
                params: params,
            }).success(function (response) {
                vm.events = [];
                for (var i in response) {
                    response[i].startsAt = new Date(response[i].startsAt);
                    response[i].endsAt = new Date(response[i].endsAt);
                    response[i].actions = actions;
                    vm.events.push(response[i]);
                }
            }
        )
    };

    vm.sendData();

    $scope.filterChanged = function () {
        vm.sendData();
    }

    vm.toggle = function ($event, field, event) {
        $event.preventDefault();
        $event.stopPropagation();
        event[field] = !event[field];
    };

    vm.timespanClicked = function (date, cell) {

        if (vm.calendarView === 'month') {
            if ((vm.cellIsOpen && moment(date).startOf('day').isSame(moment(vm.viewDate).startOf('day'))) || cell.events.length === 0 || !cell.inMonth) {
                vm.cellIsOpen = false;
            } else {
                vm.cellIsOpen = true;
                vm.viewDate = date;
            }
        } else if (vm.calendarView === 'year') {
            if ((vm.cellIsOpen && moment(date).startOf('month').isSame(moment(vm.viewDate).startOf('month'))) || cell.events.length === 0) {
                vm.cellIsOpen = false;
            } else {
                vm.cellIsOpen = true;
                vm.viewDate = date;
            }
        }

    };

}])


app.controller('FileUploaderModalInstanceCtrl', function ($scope, $uibModalInstance, param) {
    $scope.dir = param.extra_data['dir']
    $scope.rename_value = param.file_name;
    $scope.file_name = param.file_name;
    $scope.old_value = param.file_name;
    $scope.ok = function (value) {
        $uibModalInstance.close(value);
    };
});


app.controller('FileUploaderObjectToolsController', ['$scope', '$http', '$uibModal', function ($scope, $http, $uibModal) {
    $scope.fileUploadDialog = function () {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/filebrowseruploaddialog/',
            windowClass: 'fb-modal-upload',
            controller: 'FileUploaderModalInstanceCtrl',
            resolve: {
                param: function () {
                    return {'extra_data': $scope.$parent.data.extra_data};
                }
            }
        });
        modalInstance.result.then(function (value) {
            if (value == 'complete') {
                $scope.$parent.getData(1);
            } else {
                alert(value);
            }
        });
    };

    $scope.newFolderDialog = function () {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/filebrowsernewfolderdialog/',
            windowClass: 'fb-modal-upload',
            controller: 'FileUploaderModalInstanceCtrl',
            resolve: {
                param: function () {
                    return {'extra_data': $scope.$parent.data.extra_data};
                }
            }
        });
        modalInstance.result.then(function (value) {
            var value = value.data[0];
            if (value == 'created') {
                $scope.$parent.getData(1);
            } else {
                alert(value);
            }
        });
    };

    $scope.newFolder = function (dir) {
        return $http.get("/dashboard/ui/filebrowsernewfolderdialog/",
            {
                params: {
                    json: true,
                    dir: dir,
                    folder_name: $scope.new_folder_value,
                },
            }).success(function (response) {
            return response.data;
        })
    }

    $scope.renameFileFolderDialog = function (file) {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/filebrowserrenamedialog/',
            windowClass: 'fb-modal-upload',
            controller: 'FileUploaderModalInstanceCtrl',
            resolve: {
                param: function () {
                    return {
                        'extra_data': $scope.$parent.data.extra_data,
                        'file_name': file
                    };
                }
            }
        });
        modalInstance.result.then(function (value) {
            var value = value.data[0];
            if (value == 'renamed') {
                $scope.$parent.getData(1);
            } else {
                alert(value);
            }
        });
    };

    $scope.renameFileDir = function (dir, old_file_name) {
        return $http.get("/dashboard/ui/filebrowserrenamedialog/",
            {
                params: {
                    json: true,
                    dir: dir,
                    new_file_name: $scope.rename_value,
                    old_file_name: old_file_name,

                },
            }).success(function (response) {
            return response.data;
        })
    }

    $scope.removeFileFolderDialog = function (file) {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/filebrowserremovedialog/',
            windowClass: 'fb-modal-upload',
            controller: 'FileUploaderModalInstanceCtrl',
            resolve: {
                param: function () {
                    return {
                        'extra_data': $scope.$parent.data.extra_data,
                        'file_name': file
                    };
                }
            }
        });
        modalInstance.result.then(function (value) {
            var value = value.data[0];
            if (value == 'renamed') {
                $scope.$parent.getData(1);
            } else {
                alert(value);
            }
        });
    };

    $scope.removeFileDir = function (dir, file_name) {
        return $http.get("/dashboard/ui/filebrowserremovedialog/",
            {
                params: {
                    json: true,
                    dir: dir,
                    file_name: $scope.file_name,

                },
            }).success(function (response) {
            return response.data;
        })
    }


}]);

app.controller('UploadController', ['$scope', 'FileUploader', '$attrs', function ($scope, FileUploader, $attrs) {
    var uploader = $scope.uploader = new FileUploader({
        url: '/dashboard/ui/filebrowseruploaddialog/?csrfmiddlewaretoken=' + $attrs.ngCsrftoken + '&dir=' +
        $scope.$parent.dir,
    });
    uploader.onSuccessItem = function (fileItem, response, status, headers) {
        if (response.answer == 'success') {

        } else {
            alert(response.answer);
        }
    };
    uploader.onCompleteAll = function () {
        $scope.ok('complete');
    };

}]).config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$').endSymbol('$}');
})

app.controller('ImageUploadController', ['$scope', '$uibModal', '$parse', function ($scope, $uibModal, $parse) {

    $scope.model_name = null;

    $scope.init = function (media_url) {
        $scope.media_url = media_url;
    }

    $scope.openFileBrowser = function (model_name) {
        $scope.model_name = model_name
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/filebrowserdialog/',
            controller: 'ModalInstanceCtrl',
            windowClass: 'modal-fit',
        });
        modalInstance.result.then(function (value) {
            $parse($scope.model_name).assign($scope, value.replace($scope.media_url, ''));
        });
    }

    $scope.clearModel = function (model_name) {
        if (confirm('Are you sure you want to clear image field?')) {
            $parse(model_name).assign($scope, '');
        }
    }

}]);


app.controller('ProfilePageCtrl', function ($scope, fileReader, $filter, $uibModal) {

})

app.controller('AdminPanelCtrl', function ($scope) {
    $scope.goToTable = function () {
        var scope = angular.element('#grid-container').scope()
        scope[scope.uiViewName].editable.view_mode = 'table';
        angular.element("#admin-panel").scope().title = '';
        $scope.toTableVisible = false;
    }
})

app.controller('StateAdminPanelCtrl',['$scope','$state', function ($scope, $state) {
    $scope.goToTable = function (state_name) {
        angular.element("#admin-panel").scope().panel_title = ''
        $state.go(state_name)
    }
}])


app.controller('TodoCtrl', function ($scope, $http, baConfig) {
    $scope.transparent = baConfig.theme.blur;
    var dashboardColors = baConfig.colors.dashboard;
    var colors = [];
    for (var key in dashboardColors) {
      colors.push(dashboardColors[key]);
    }

    function getRandomColor() {
      var i = Math.floor(Math.random() * (colors.length - 1));
      return colors[i];
    }


    $scope.todoList = [];

    function getData(params) {
        $http.get("/dashboard/ui/todolistview/",
        {
            params: params,
        }).success(function (response) {
                $scope.todoList = response;
                $scope.todoList.forEach(function(item) {
                  item.color = getRandomColor();
                });
        })
    }

    getData({});

    $scope.addToDoItem = function (event, clickPlus) {
      if (clickPlus || event.which === 13) {
          if ($scope.newTodoText){
            getData({'text': $scope.newTodoText});
          }
      }
    };

    $scope.removeTodo = function (item) {
        getData({'delete': item.id});
    }

    $scope.checkTodo = function (item) {
        getData({'check': item.checked, 'id': item.id});
    }

})

