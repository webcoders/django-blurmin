app.filter('greaterThen', function () {
    return function (items, field, value) {
        var filteredItems = []
        angular.forEach(items, function (item) {
            if (item[field] * 1 > value) {
                filteredItems.push(item);
            }
        });
        return filteredItems;
    }
});

app.controller('CompanyInfoPageCtrl', function ($scope) {
    $scope.$watch('form.fields.name.value', function (newValue, oldValue) {
        if (newValue.length > 0) {
            angular.element("#admin-panel").scope().panel_title = 'Company: ' + $scope.form.fields.name.value;
        }
    });
})

app.controller('EstimagePageCtrl', ['$scope', '$uibModal', '$sce','$state', function ($scope, $uibModal, $sce, $state) {


    $scope.packingMaterialIsCollapsed = true;
    $scope.revisedEstimateCollapsed = true;
    $scope.bulkyArticleIsCollapsed = true;
    $scope.booking_fee = 50;
    $scope.packing_material_data = [];
    $scope.packing_materials_price = 0;

    $scope.revised_packing_material_data = [];
    $scope.revised_packing_materials_price = 0;

    $scope.bulky_article_data = [];
    $scope.bulky_articles_price = 0;
    $scope.special_service_data = [];
    $scope.special_services_price = 0;

    $scope.revised_special_service_data = [];
    $scope.revised_special_services_price = 0;

    $scope.additional_lbs = 0;

    $scope.original_lbs = 0;
    $scope.form.fields.original_cu_ft.value = 0;
    $scope.cu_ft_subtotal = 0;
    $scope.others_price = 0;
    $scope.others_price_data = []
    $scope.revised_others_price = 0;
    $scope.revised_others_price_data = []
    $scope.revised_estimate_subtotal = 0

    $scope.$on('data_received', function (event, data) {
        if (data.view_name == 'estimategridview' && data.data.record_id){
            UserInventory(eval($scope.form.fields.inventories.value));
            $scope.packing_materials_price = 0;
            $scope.bulky_articles_price = 0;
            $scope.special_services_price = 0;
            $scope.revised_packing_materials_price = 0;
            $scope.revised_special_services_price = 0;

            $scope.packing_material_data = JSON.parse(data.data.fields.packing_materials.value);
            $scope.bulky_article_data = JSON.parse(data.data.fields.bulky_articles.value);
            $scope.special_service_data = JSON.parse(data.data.fields.special_services.value);

            $scope.revised_packing_material_data = JSON.parse(data.data.fields.revised_packing_materials.value);
            $scope.revised_special_service_data = JSON.parse(data.data.fields.revised_special_services.value);

            for (var i in $scope.packing_material_data) {
                var item = $scope.packing_material_data[i];
                $scope.packing_materials_price += item._total * 1;
            }

            for (var i in $scope.bulky_article_data) {
                var item = $scope.bulky_article_data[i];
                $scope.bulky_articles_price += item._total * 1;
            }

            for (var i in $scope.special_service_data) {
                var item = $scope.special_service_data[i];
                item._total = item.p_total * 1 + item.d_total * 1;
                $scope.special_services_price += item.p_total * 1 + item.d_total * 1;
            }


            for (var i in $scope.revised_packing_material_data) {
                var item = $scope.revised_packing_material_data[i];
                $scope.revised_packing_materials_price += item._total * 1;
            }

            for (var i in $scope.revised_special_service_data) {
                var item = $scope.revised_special_service_data[i];
                item._total = item.p_total * 1 + item.d_total * 1;
                $scope.revised_special_services_price += item.p_total * 1 + item.d_total * 1;
            }
            $scope.cuftChanged();
        }
    })

    $scope.$on('before_form_save', function (event, data) {
        if (data.view_name == "estimategridview"){
            function packing_materials_prepare(data) {
                var _data = [];
                for (var d in data) {
                    var item = data[d];
                    if (item._carton_price > 0) {
                        var p = {};
                        p.id = item.id;
                        p.qty = item._carton_qty;
                        p.price = item._carton_price;
                        p.packing_service_price = item._packing_price;
                        p.packing_service_qty = item._packing_qty;
                        p.unpacking_service_price = item._unpacking_price;
                        p.unpacking_service_qty = item._unpacking_qty;
                        p.total = item._total;
                        _data.push(p);
                    }
                }
                return _data
            }

            $scope.form.fields.packing_materials.value = JSON.stringify(packing_materials_prepare($scope.packing_material_data));
            $scope.form.fields.revised_packing_materials.value = JSON.stringify(packing_materials_prepare($scope.revised_packing_material_data));

            var _data = [];
            for (var d in $scope.bulky_article_data) {
                var item = $scope.bulky_article_data[d];
                if (item._qty > 0) {
                    var p = {};
                    p.id = item.id;
                    p.qty = item._qty;
                    p.price = item._price;
                    p.total = item._total;
                    _data.push(p);
                }
            }
            $scope.form.fields.bulky_articles.value = JSON.stringify(_data);


            function special_services_prepare(data) {
                var _data = [];
                for (var d in data) {
                    var item = data[d];
                    if (item._qty1 > 0) {
                        var p = {};
                        p.id = item.id;
                        p.pickup = item._pickup;
                        p.delivery = item._delivery;
                        p.p_qty1 = item.p_qty1;
                        p.p_qty2 = item.p_qty2;
                        p.d_qty1 = item.d_qty1;
                        p.d_qty2 = item.d_qty2;
                        p.p_price = item._price;
                        p.d_price = item._price;
                        p.p_total_price = item.p_total;
                        p.d_total_price = item.d_total;
                        _data.push(p);
                    }
                }
                return _data;
            }

            $scope.form.fields.special_services.value = JSON.stringify(special_services_prepare($scope.special_service_data));
            $scope.form.fields.revised_special_services.value = JSON.stringify(special_services_prepare($scope.revised_special_service_data));

        }
    });


    $scope.getIframeSrc = function (report_server_url, file_name) {
        if ($state.params.id){
            return $sce.getTrustedResourceUrl(report_server_url + '/reports/' + $state.params.id  + '/' +
                file_name + '#zoom=100&toolbar=1');
        }
        return '';
    };


    $scope.labels_count = 10;

    $scope.labelsUrl = function (report_server_url) {
        return $scope.getIframeSrc(report_server_url, $scope.labels_count + '/labels.pdf');
    };

    $scope.printLabels = function (report_server_url) {
         $scope.labels_count = angular.element('#labels_count').scope().labels_count;
         var e = angular.element('#labels')[0];
         var cln = angular.element('#labels')[0].cloneNode(true);
         cln.src = $scope.labelsUrl(report_server_url)
         e.remove();
         angular.element('#labels-container')[0].appendChild(cln);
    }

    function othersPriceCalc(data) {
        $scope.others_price = 0;
        $scope.others_price_data = data;
        for (var i in data) {
            var item = data[i];
            try {
                $scope.others_price += item.price.replace(',', '') * 1;
            } catch (e) {
                $scope.others_price += item.price * 1;
            }
        }
        $scope.getTotal();
    }

    function revisedOthersPriceCalc(data) {
        $scope.revised_others_price = 0;
        $scope.revised_others_price_data = data;
        for (var i in data) {
            var item = data[i];
            try {
                $scope.revised_others_price += item.price.replace(',', '') * 1;
            } catch (e) {
                $scope.revised_others_price += item.price * 1;
            }
        }
        $scope.getRevisedTotal();
        $scope.getTotal();
    }

    $scope.CommentsSelected = function(event){
        angular.element('#id_comments').scope().getData({'estimate_id': $state.params.id});;
    }



    $scope.$on('data_received', function (event, data) {
        if (data.view_name == 'otherspricegridview') {
            othersPriceCalc(data.rows);
        }
        if (data.view_name == 'revisedotherspricegridview') {
            revisedOthersPriceCalc(data.rows);
        }
    });

    $scope.$on('data_changed', function (event, data) {
        if (data.view_name == 'otherspricegridview') {
            othersPriceCalc(data.rows);
        }
        if (data.view_name == 'revisedotherspricegridview') {
            revisedOthersPriceCalc(data.rows);
        }
    });

    function updateTitle() {
            var scope = angular.element("#admin-panel").scope();
            if ($state.params.id){
                scope.panel_title = 'Estimate #' + $state.params.id;

                if ($scope.form.fields.price.value * 1 > 0){
                    scope.panel_title += '. $' + $scope.form.fields.price.value;
                }
                scope.panel_title += '. ' + angular.element('#company_label').text();
            }
    }

    $scope.$watch('form.fields.company.value', function (newValue, oldValue) {
        updateTitle();
    });

    $scope.$watch('form.fields.price.value', function (newValue, oldValue) {
        if (newValue) {
            updateTitle();
        }
    });

    if ( !$state.params.id ) {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'New Estimate';
    }
    else {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'Estimate #' + $state.params.id;
    }

    $scope.$watch('form.fields.from_zip_code.value', function (newValue, oldValue) {
        if (newValue == undefined || newValue == ''){
            if (angular.element('#id_from_zip_code')[0])
                angular.element('#id_from_zip_code')[0].setAttribute('data', '')
            return;
        }
        var data = angular.element('#id_from_zip_code')[0].getAttribute('data');
        if (data == null)
            return
        data = data.split(',');
        if ($scope.form.fields.from_city.value == undefined || $scope.form.fields.from_city.value.replace(/ /g, '') == '')
            $scope.form.fields.from_city.value = data[2];
        if ($scope.form.fields.from_state.value == undefined || $scope.form.fields.from_state.value.replace(/ /g, '') == '')
            $scope.form.fields.from_state.value = data[3];
    });

    $scope.$watch('form.fields.to_zip_code.value', function (newValue, oldValue) {
        if (newValue == undefined || newValue == '')
            return;
        var data = angular.element('#id_to_zip_code')[0].getAttribute('data');
        if (data == null)
            return
        data = data.split(',');
        console.log(data);
        if ($scope.form.fields.to_city.value == undefined || $scope.form.fields.to_city.value.replace(/ /g, '') == '')
            $scope.form.fields.to_city.value = data[2];
        if ($scope.form.fields.to_state.value == undefined || $scope.form.fields.to_state.value.replace(/ /g, '') == '')
            $scope.form.fields.to_state.value = data[3];
    });

    $scope.$watch('form.fields.inventories.value', function (newValue, oldValue) {
        UserInventory(eval(newValue));
    });


    $scope.cuftChanged = function () {
        if ($scope.form.fields.additional_cu_ft.value) {
             this.additional_lbs = Math.round($scope.form.fields.additional_cu_ft.value *
                $scope.form.fields.cubes_in_lb.value * 100) / 100;
            $scope.add_cu_ft_subtotal = parseFloat($scope.form.fields.additional_cu_ft.value)  * 1 * parseFloat($scope.form.fields.price_per_cf.value);
            $scope.getRevisedTotal()
            $scope.getTotal();
        }
    }

    $scope.lbsChanged = function () {
        $scope.form.fields.additional_cu_ft.value = Math.round(this.additional_lbs /
            $scope.form.fields.cubes_in_lb.value * 100) / 100;
        $scope.getRevisedTotal()
        $scope.getTotal();
    }

    $scope.getTotal = function () {
        var total = 0

        var cu_ft = parseFloat($scope.form.fields.original_cu_ft.value);

        if (this.form.fields.original_cu_ft.value) {
            cu_ft = parseFloat(this.form.fields.original_cu_ft.value);
            $scope.original_lbs = cu_ft * parseFloat($scope.form.fields.cubes_in_lb.value) * 1;
        }

        $scope.cu_ft_subtotal = cu_ft * 1 * parseFloat($scope.form.fields.price_per_cf.value);
        $scope.add_cu_ft_subtotal = parseFloat($scope.form.fields.additional_cu_ft.value)  * 1 * parseFloat($scope.form.fields.price_per_cf.value);


        if ($scope.form.fields.delivery_class.value == 1) {
            total += parseFloat($scope.form.fields.price_first_class.value);
        }
        if ($scope.form.fields.delivery_class.value == 2) {
            total += parseFloat($scope.form.fields.price_business_class.value);
        }
        if ($scope.form.fields.delivery_class.value == 3) {
            total += parseFloat($scope.form.fields.price_economy_class.value);
        }
        total += parseFloat($scope.form.fields.fuel_surcharge.value);
        total += parseFloat($scope.booking_fee);
        total += parseFloat($scope.cu_ft_subtotal);
        total += parseFloat($scope.packing_materials_price);
        total += parseFloat($scope.bulky_articles_price);
        total += parseFloat($scope.special_services_price);
        total += parseFloat($scope.revised_estimate_subtotal);
        total += parseFloat($scope.others_price);


        $scope.form.fields.price.value = Math.round(total * 100) / 100;
        return total;

    }

    $scope.getRevisedTotal = function () {
        $scope.revised_estimate_subtotal = $scope.revised_packing_materials_price +
                $scope.revised_special_services_price + $scope.add_cu_ft_subtotal + $scope.revised_others_price;

    }

    $scope.packingMaterialsDialog = function (revised) {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/packingmaterialsgridview/',
            controller: 'PackingMaterialsCtrl',
            windowClass: 'modal-fit',
            resolve: {
                param: function () {
                    if (revised == true) {
                        return {'data': $scope.revised_packing_material_data};
                    }
                    return {'data': $scope.packing_material_data};
                }
            }
        });
        modalInstance.result.then(function (data) {
            var price = 0

            for (i in data) {
                if (data[i]._carton_price > 0) {
                    item = data[i];
                    price +=
                        item._carton_price * 1 +
                        item._packing_price * 1 +
                        item._unpacking_price * 1
                }
            }

            if (revised==true){
                $scope.revised_packing_materials_price = price
                $scope.revised_packing_material_data = data;
                $scope.getRevisedTotal();
                $scope.getTotal();
            } else {
                $scope.packing_materials_price = price
                $scope.packing_material_data = data;
                $scope.getTotal();
            }

        });
    }

    $scope.calcMaterialsTotal = function (item) {
        var total = item._qty * 1 +
            item.carton_price * 1 +
            item.packing_service_price * 1 +
            item.unpacking_service_price * 1
        return total
    }

    $scope.bulkyArticlesDialog = function () {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/bulkyarticlesgridview/',
            controller: 'BulkyArticlesCtrl',
            windowClass: 'modal-fit',
            resolve: {
                param: function () {
                    return {'data': $scope.bulky_article_data};
                }
            }
        });
        modalInstance.result.then(function (data) {
            $scope.bulky_articles_price = 0;
            for (i in data) {
                if (data[i]._qty > 0) {
                    item = data[i];
                    $scope.bulky_articles_price += item._qty * 1 *
                        item._price;
                }
            }
            $scope.bulky_article_data = data;
            $scope.getTotal();
        });
    }

    $scope.calcBulkyArticleTotal = function (item) {
        var total = item._qty * 1 +
            item.price * 1;
        return total
    }

    $scope.specialServicesDialog = function (revised) {
        var modal = $uibModal;
        var modalInstance = modal.open({
            animation: true,
            templateUrl: '/dashboard/ui/specialservicesview/',
            controller: 'SpecialServicesCtrl',
            windowClass: 'modal-special-services',
            resolve: {
                param: function () {
                    if (revised == true){
                        return {'data': $scope.revised_special_service_data};
                    }
                    return {'data': $scope.special_service_data};
                }
            }
        });
        modalInstance.result.then(function (data) {
            var price = 0;
            for (i in data) {
                if (data[i]._qty1 > 0) {
                    item = data[i];
                    price +=
                        item._total * 1
                }
            }
            if (revised==true){
                $scope.revised_special_services_price = price;
                $scope.revised_special_service_data = data;
                $scope.getRevisedTotal();
                $scope.getTotal();
            } else {
                $scope.special_services_price = price;
                $scope.special_service_data = data;
                $scope.getTotal();
            }

        });
    }

}])

app.controller('PackingMaterialsCtrl', function ($scope, $uibModalInstance, param) {
    $scope.data = []
    $scope.param = param

    $scope.$on('data_received', function (event, data) {
        $scope.data = data.rows;
        for (j in $scope.data) {
            var item = $scope.data[j];
            $scope['m_carton_' + item.id] = '';
            $scope['m_packing_' + item.id] = '';
            $scope['m_unpacking_' + item.id] = '';
            $scope['t_' + item.id] = '0';
        }
        if ($scope.param.data.length > 0) {
            for (i in $scope.param.data) {
                var item = $scope.param.data[i];
                if (item._carton_price * 1 > 0) {
                    $scope['m_carton_' + item.id] = item._carton_qty.toString();
                    $scope['m_packing_' + item.id] = item._packing_qty.toString();
                    $scope['m_unpacking_' + item.id] = item._unpacking_qty.toString();
                    $scope['t_' + item.id] = item._total.toString();
                    for (j in $scope.data) {
                        if ($scope.data[j].id == item.id) {
                            $scope.data[j]._carton_qty = item._carton_qty;
                            $scope.data[j]._packing_qty = item._packing_qty;
                            $scope.data[j]._unpacking_qty = item._unpacking_qty;
                            $scope.data[j]._carton_price = item._carton_price;
                            $scope.data[j]._packing_price = item._packing_price;
                            $scope.data[j]._unpacking_price = item._unpacking_price;
                            $scope.data[j]._total = item._total
                        }
                    }
                }
            }
//            $scope.$apply();
        }
    });

    $scope.qtyUpdated = function (id, carton_price, packing_service_price, unpacking_service_price, model_name, elem) {
        elem.object._carton_qty = elem['m_carton_' + id] * 1;
        elem.object._carton_price = elem.object._carton_qty * carton_price;
        elem.object._packing_qty = elem['m_packing_' + id] * 1;
        elem.object._packing_price = elem.object._packing_qty * packing_service_price;
        elem.object._unpacking_qty = elem['m_unpacking_' + id] * 1
        elem.object._unpacking_price = elem.object._unpacking_qty * unpacking_service_price;
        elem.object._total = elem.object._carton_price + elem.object._packing_price + elem.object._unpacking_price;
        elem['t_' + id] = elem.object._total;
    }

    $scope.ok = function () {
        $uibModalInstance.close($scope.data);
    }
})

app.controller('BulkyArticlesCtrl', function ($scope, $uibModalInstance, param) {
    $scope.data = []
    $scope.param = param

    $scope.$on('data_received', function (event, data) {
        $scope.data = data.rows;
        for (j in $scope.data) {
            var item = $scope.data[j]
            $scope['t_' + item.id] = '0';
        }
        if ($scope.param.data.length > 0) {
            for (i in $scope.param.data) {
                var item = $scope.param.data[i];
                if (item._qty * 1 > 0) {
                    $scope['m' + item.id] = item._qty;
                    $scope['t_' + item.id] = item._total;
                    for (j in $scope.data) {
                        if ($scope.data[j].id == item.id) {
                            $scope.data[j]._qty = item._qty;
                            $scope.data[j]._price = item._price;
                            $scope.data[j]._total = item._total;
                        }
                    }
                }
            }
        }
//        $scope.$apply();
    });

    $scope.qtyUpdated = function (id, model_name, price, elem) {
        elem.object._qty = elem[model_name];
        elem.object._total = elem.object._qty * 1 * price;
        elem.object._price = price;
        elem['t_' + id] = elem.object._total;
    }

    $scope.ok = function () {
        $uibModalInstance.close($scope.data);
    }
})


app.controller('SpecialServicesCtrl', function ($scope, $uibModalInstance, $timeout, param) {
    $scope.data = []
    $scope.param = param

    $scope.tabSelected = function (tab) {
        if (tab == 'pickup'){
            try {
                var position = angular.element('#deliveryTab .horizontal-scroll')[0].scrollTop
                $timeout(function() {
                    angular.element('#pickupTab .horizontal-scroll')[0].scrollTop = position;
                }, 1)
            } catch (e) {
                console.log(e);
            }

        }
        if (tab == 'delivery'){
            try {
                var position = angular.element('#pickupTab .horizontal-scroll')[0].scrollTop;
                $timeout(function() {
                    angular.element('#deliveryTab .horizontal-scroll')[0].scrollTop = position;
                }, 1)
            } catch (e) {
                console.log(e);
            }
        }
    }

    $scope.$on('data_received', function (event, data) {
        $scope.data = data.rows;
        for (j in $scope.data) {
            var item = $scope.data[j];
            $scope['m1_p_' + item.id] = '';
            $scope['t_p_' + item.id] = '0';
            $scope['m1_d_' + item.id] = '';
            $scope['t_d_' + item.id] = '0';
        }
        if ($scope.param.data.length > 0) {
            for (var i in $scope.param.data) {
                var item = $scope.param.data[i];
                if (item.p_qty1 * 1 > 0) {
                    if (item.p_qty1!=undefined){
                        $scope['m1_p_' + item.id] = item.p_qty1.toString();
                    }
                    if (item.p_qty2!=undefined) {
                        $scope['m2_p_' + item.id] = item.p_qty2.toString();
                    }
                    $scope['t_p_' + item.id] = item.p_total.toString();
                    for (j in $scope.data) {
                        if ($scope.data[j].id == item.id) {
                            $scope.data[j].p_qty1 = item.p_qty1;
                            $scope.data[j].p_qty2 = item.p_qty2;
                            $scope.data[j].p_price = item.p_price;
                            $scope.data[j].p_total = item.p_total;
                            $scope.data[j]._pickup = true;
                        }
                    }
                }
                if (item.d_qty1 * 1 > 0) {
                    if (item.d_qty1!=undefined){
                        $scope['m1_d_' + item.id] = item.d_qty1.toString();
                    }
                    if (item.d_qty2!=undefined) {
                        $scope['m2_d_' + item.id] = item.d_qty2.toString();
                    }
                    $scope['t_d_' + item.id] = item.d_total.toString();
                    for (var j in $scope.data) {
                        if ($scope.data[j].id == item.id) {
                            $scope.data[j].d_qty1 = item.d_qty1;
                            $scope.data[j].d_qty2 = item.d_qty2;
                            $scope.data[j].d_price = item.d_price;
                            $scope.data[j].d_total = item.d_total;
                            $scope.data[j]._delivery = true;
                        }
                    }
                }
                for (var j in $scope.data) {
                        var object = $scope.data[j]
                        object._qty1 = (object.p_qty1 || 0) + (object.d_qty1 || 0);
                        object._price = (object.p_price || 0) + (object.d_price || 0);
                        object._total = (object.p_total || 0) + (object.d_total || 0);
                }
            }
        }
    });

    function getObjectByID(id){
        for (var j in $scope.data) {
            if ($scope.data[j].id == id)
                return $scope.data[j];
        }
        return null
    }

    $scope.qtyUpdated = function (id, _id, t, elem) {
        var m1 = elem['m1_' + id];
        var m2 = elem['m2_' + id];

        var object = getObjectByID(_id);

        if (t =='m2' && m1=='' && m2!=''){
            elem['m1_' + id] = '1';
            m1 = 1;
        }
        if (m2=='' && t=='m1' && m1!=''){
            elem['m2_' + id] = '1';
            m2 = 1;
        }

        if (id.startsWith('p_')){
            object.p_qty1 = m1 * 1
            var total = m1 * 1;

            if (m2!=undefined) {
                total = m1 * m2
                object.p_qty2 = m2 * 1
            }
            object.p_price = elem.object.price * 1;
            object.p_total = total * object.p_price;
            elem['t_' + id] = object.p_total;
            object._pickup = true;
        } else {
            object.d_qty1 = m1 * 1
            var total = m1 * 1;

            if (m2!=undefined) {
                total = m1 * m2
                object.d_qty2 = m2 * 1
            }
            object.d_price = elem.object.price * 1;
            object.d_total = total * object.d_price;
            elem['t_' + id] = object.d_total;
            object._delivery = true;
        }
        object._qty1 = (object.p_qty1 || 0) + (object.d_qty1 || 0);
        object._price = (object.p_price || 0) + (object.d_price || 0);
        object._total = (object.p_total || 0) + (object.d_total || 0);
    }

    $scope.ok = function () {
        $uibModalInstance.close($scope.data);
    }
})


app.controller('ServicePageCtrl',['$scope', '$state' ,'$timeout','toastr', function ($scope, $state, $timeout,toastr) {
    $scope.service = {'name':'','price':''};

    if ( !$state.params.id ) {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'New Service Request';
    } else {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'Service Request #' + $state.params.id;
    }

    $scope.service = {'name':'','price':''};
    $scope.$watch('form.fields.service.value', function (newValue, oldValue, $state) {
        if (newValue == undefined) {
            return
        }

        if (newValue.length > 0) {
            var service = $scope.form.services[newValue];
            $scope.lead_rate = service.price;
            $scope.service = service;
        }
    });

    $scope.for_childs.after_submit = function(fields_valid,form_scope) {
               if ($scope.form.errors.length == 0 && fields_valid) {
                    if ( !$scope.record_id ) {
                        toastr.success('Created');
                            if ( !$scope.form.fields.ccard.value ){
                                toastr.success('Please enter ccard infromation to compelte your ' + $scope.service.name+ ' service request.');
                                $state.go('ccardinfo.change');
                                return;
                            }
                            $state.go($state.current, {id: $scope.form.record_id})
                    } else {
                        if ( !$scope.form.fields.ccard.value ){
                            toastr.success('Please enter ccard infromation to compelte your ' + $scope.service.name+ ' service request.');
                            $state.go('ccardinfo.change');
                        }
                        toastr.success('Saved');
                    }
                    $scope.updateGridRecord();
                } else {
                    toastr.error('Please correct the errors');
                }
    }

}]);

app.controller('ServicePageCtrlLeads',['$scope', '$state' ,'$timeout','toastr', function ($scope, $state, $timeout,toastr) {
    $scope.state_enabled = false;
    $scope.cubic_feet_enabled = false;
    $scope.distance_enabled = false;
    $scope.lead_rate = 0;
    $scope.service = {'name':'','price':''};
    $scope.week_days=[false,false,false,false,false,false,false]
    $scope.$watch('form.fields.service.value', function (newValue, oldValue, $state) {
        if (newValue == undefined) {
            return
        }

        if (newValue.length > 0) {
            $scope.state_enabled = false;
            $scope.cubic_feet_enabled = false;
            $scope.distance_enabled = false;
            var service = $scope.form.services[newValue];
            if ( service.name == 'local' ) {
                $scope.distance_enabled = true;
            }

            if ( service.name == 'long' || service.name == 'premium' ){
                $scope.state_enabled = true;
            }

            if ( service.name == 'premium' ) {
                $scope.cubic_feet_enabled = true;
            }
            $scope.lead_rate = service.price;
            $scope.service = service;
        }

    });

    if ( !$state.params.id ) {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'New Service Request';
    } else {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'Service Request #' + $state.params.id;
    }

    var budget_changed = 0;
    var budget_timeout_promise = 0;
    $scope.ch_budget= function(blur){
        $scope.form.fields.total.value = Math.floor($scope.form.fields.total_budget.value / $scope.lead_rate);
        if ( $scope.form.fields.total.value <= 0 ){
            $scope.form.fields.total.value = 1;
        }

        if ( !blur ) {
            if ((new Date().getTime() - budget_changed < 3000) && budget_timeout_promise) {
                $timeout.cancel(budget_timeout_promise);
            }
            budget_timeout_promise = $timeout(function () {
                $scope.form.fields.total_budget.value = $scope.form.fields.total.value * $scope.lead_rate;
            }, 3000);
            budget_changed = new Date().getTime()
        }
        $scope.ch_budgetdays();
    }


    $scope.ch_total = function(){
        $scope.form.fields.total_budget.value = $scope.form.fields.total.value * $scope.lead_rate;
        if  ( $scope.form.fields.per_day.value > $scope.form.fields.total.value ) {
            $scope.ch_budgetdays();
        }
    }

    $scope.$watch('lead_rate', function (newValue, oldValue) {
        if (newValue == undefined) {
            return
        }
        $scope.ch_total();
    });


    $scope.ch_perday= function(){
        if ( $scope.form.fields.per_day.value > $scope.form.fields.total.value ){
            $scope.form.fields.per_day.value = $scope.form.fields.total.value
        }
        $scope.form.fields.budget_days.value = Math.ceil($scope.form.fields.total.value / $scope.form.fields.per_day.value);
    }

    $scope.ch_budgetdays = function(){
        if ( $scope.form.fields.budget_days.value > $scope.form.fields.total.value ){
            $scope.form.fields.budget_days.value = $scope.form.fields.total.value
        }
        $scope.form.fields.per_day.value = Math.ceil($scope.form.fields.total.value / $scope.form.fields.budget_days.value);
    }


    var bypass_perday = false;

    $scope.$watch('form.fields.per_day.value', function (newValue, oldValue) {
        if (newValue == undefined || newValue == "" || bypass_perday) {
            return newValue;
        }

        bypass_perday = true;
    });


    $scope.$watchCollection('week_days', function (newValue, oldValue) {
      if (newValue == undefined || newValue == "" ) {
        return newValue;
      }
      $scope.form.fields.week_days.value = JSON.stringify($scope.week_days)
    })

    $scope.$on('data_received',function (event,data) {
        $scope.week_days = eval($scope.form.fields.week_days.value)
        $scope.ch_perday();

        var val = [];
        for (var i in  $scope.form.fields.cubic_feet.value) {
            val.push(String($scope.form.fields.cubic_feet.value[i]['id']))
        }
        $scope.form.fields.cubic_feet.value = val;
    })

/*    $scope.cubicFeetItems = [
      { label: '50 to 500', value: 1 },
      { label: 'Option 2', value: 2 },
      { label: 'Option 3', value: 3 },
      { label: 'Option 4', value: 4 },
    ];*/

    $scope.for_childs.before_submit = function () {
        switch ($scope.service.name) {
            case 'local':
                if (!$scope.form.fields.from_zip.value.length && !$scope.form.fields.from_anywhere.value) {
                    $scope.fromZipIsCollapsed = true;
                    alert('Please,make choice of the pickup zip codes!')
                    return false;
                }
                break;
            case 'premium':
                if ( !$scope.form.fields.cubic_feet.value.length ){
                    $scope.fromStateIsCollapsed = true;
                    alert('Please, select cubic footages!')
                    return false;
                }
                $scope.form.fields.cubic_feet.value = JSON.stringify($scope.form.fields.cubic_feet.value);

            case 'long':
                if (!$scope.form.fields.from_state.value.length && !$scope.form.fields.from_anywhere.value) {
                    $scope.fromStateIsCollapsed = true;
                    alert('Please, make choice of the pickup states!')
                    return false;
                }
                break;
            default:
                return false;
        }

        for (var i in $scope.week_days) {
            if ($scope.week_days[i]) {
                return true;
            }
        }


        alert('Sorry, pickup week days is mandatory!')
        return false;
    }



    $scope.for_childs.after_submit = function(fields_valid,form_scope) {
               if ($scope.form.errors.length == 0 && fields_valid) {
                    if ( !$scope.record_id ) {
                        toastr.success('Created');
//                        if ( type != 'grid-row' )
                            if ( !$scope.form.fields.ccard.value ){
                                toastr.success('Please enter ccard infromation to compelte your ' + $scope.service.name+ ' leads service request.');
                                $state.go('ccardinfo.change');
                                return;
                            }
                            $state.go($state.current, {id: $scope.form.record_id})
//                        }
                    } else {
                        if ( !$scope.form.fields.ccard.value ){
                            toastr.success('Please enter ccard infromation to compelte your ' + $scope.service.name+ ' leads service request.');
                            $state.go('ccardinfo.change');
                        }
                        toastr.success('Saved');
                    }
                    $scope.updateGridRecord();
                } else {
                    toastr.error('Please correct the errors');
                }
    }



    $scope.$watchCollection('form.fields.from_state.value', function (newValue, oldValue) {
        if (newValue == undefined) {
            return
        }
        var from_states = []
        var old_states=[]
        var removed_states=[]
        for (var val in newValue){
            from_states.push( newValue[val].id)
        }

        for (var val in oldValue){
            old_states.push( oldValue[val].id )
            if ( from_states.indexOf(oldValue[val].id) < 0 ){
                removed_states.push(oldValue[val].id)
            }
        }

//        $scope.$broadcast('update_from_city', { extra_params :{ 'state': from_states.join(',')}});

        if (from_states.length == 0 && removed_states.length > 0) {
            $scope.form.fields.from_city.value = [];
            $scope.$broadcast('update_from_city', { extra_params :{ 'state': from_states.join(',')}});
            return newValue;
        }
        if ( removed_states.length > 0 ) {
           for (var i in $scope.form.fields.from_city.value) {
                if ($scope.form.fields.from_city.value[i].unicode.endsWith(removed_states[0])) {
                    $scope.form.fields.from_city.value.pop(i);
                }
           }
        }
        $scope.$broadcast('update_from_city', { extra_params :{ 'state': from_states.join(',')}});
     });


}])

app.controller('CcardPageCtrl',['$scope', '$state','toastr', function ($scope, $state, toastr) {

    if ( !$state.params.id ) {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'New company card';
        $scope.getRecordData();
    } else {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'Company card #' + $state.params.id;
    }

    $scope.for_childs.after_submit = function(fields_valid,form_scope) {
               if ($scope.form.errors.length == 0 && fields_valid) {
                    if ( !$scope.record_id ) {
                        toastr.success('Created');
                        if ( $scope.form.sr ){
                            $state.go($scope.form.sr.state,{id: $scope.form.sr.slug});
                            return;
                        }
                        $state.go($state.current, {id: $scope.form.record_id})
                    } else {
                        toastr.success('Saved');
                    }
                    $scope.updateGridRecord();
                } else {
                    toastr.error('Please correct the errors');
                }
    }
}])

app.controller('MailPageCtrl',['$scope', '$state' , function ($scope, $state) {

    if ( !$state.params.id ) {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'New company email account';
    } else {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'Company email account #' + $state.params.id;
    }

}])

app.controller('MailTemplatePageCtrl',['$scope', '$state' , function ($scope, $state) {

    if ( !$state.params.id ) {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'New company email template';
    } else {
        var scope = angular.element("#admin-panel").scope();
        scope.panel_title = 'Company email template #' + $state.params.id;
    }

}])

app.controller('EstimateCommentsCtrl', function ($scope, $http, $state, baConfig) {
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


    $scope.commentList = [];

    $scope.getData = function(params) {
        $http.get("/dashboard/ui/estimatecommentlistview/",
        {
            params: params,
        }).success(function (response) {
                $scope.commentList = response;
                $scope.commentList.forEach(function(item) {
                  item.color = getRandomColor();
                });
        })
    }

    $scope.addCommentItem = function (event, clickPlus) {
          if ($scope.newCommentText){
            $scope.getData({
                'text': $scope.newCommentText,
                'estimate_id': $state.params.id,
            });
          }
    };

    $scope.removeCommentItem = function (item) {
        getData({'delete': item.id});
    }

})