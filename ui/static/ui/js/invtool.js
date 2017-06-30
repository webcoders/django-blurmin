function show_part(name, group_id) {
    var _sel = "#cont_group_" + String(group_id);
    $(_sel).hide('fade', function () {
        if (name == 'm') {
            $("#group_" + String(group_id) + " .r-part").hide()
            $("#group_" + String(group_id) + " .l-part").addClass("col-md-12")
            $("#group_" + String(group_id) + " .l-part").removeClass("col-md-6")
            $("#group_" + String(group_id) + " .l-part").show()
        } else if (name == 'i') {
            $("#group_" + String(group_id) + " .l-part").hide()
            $("#group_" + String(group_id) + " .r-part").addClass("col-md-12")
            $("#group_" + String(group_id) + " .r-part").removeClass("col-md-6")
            $("#group_" + String(group_id) + " .r-part").show()
        } else {
            $("#group_" + String(group_id) + " .l-part").removeClass("col-md-12")
            $("#group_" + String(group_id) + " .l-part").addClass("col-md-6")
            $("#group_" + String(group_id) + " .r-part").removeClass("col-md-12")
            $("#group_" + String(group_id) + " .r-part").addClass("col-md-6")
            $("#group_" + String(group_id) + " .r-part").show()
            $("#group_" + String(group_id) + " .l-part").show()
        }
        $(_sel).show('fade')
    })
}

function set_group_items_count(group, add) {
    var count = $('#inventory #group_items_count_' + group)[0].textContent * 1;
    count += add;
    if (count <= 0) {
        $('#inventory #group_items_count_' + group)[0].textContent = '';
    } else {
        $('#inventory #group_items_count_' + group)[0].textContent = count;
    }
}


function InventoryItem(id) {
    var item_input = $('#inventory input#' + id);
    if (item_input.length > 0) {
// we skip if item is not from estimate preset!!!
        var item_count = item_input.val() * 1;
        var group = item_input.attr('category');
        var group_item_count = $('#inventory #group_items_count_' + group)[0].textContent * 1;
    }
    this.add = function (count) {
        if (item_input.length == 0) return
        if (item_count == 0) {
            var clon = item_input.parent().parent().parent('li').clone()
            $("#inventory #item_list_" + $(item_input[0]).attr('category')).append(clon[0].outerHTML);
            $('#inventory div[data-item-id=' + id + ']').addClass('selected-item');
            if ($('#cont_group_'+item_input.attr('category')+' #hide-selected')[0].checked) {
                $('ul.items div[data-item-id=' + id + ']').parent().hide();
            }
        }
        item_count += count
        $('#inventory input#' + id).val(item_count);
        this.set_group_item(count);
//        set_group_items_count($(item_input[0]).attr('category'),true);
    }
    this.get_group_item_count = function (){
        return group_item_count;
    }

    this.set_group_item = function (add) {
        if (item_input.length == 0) return
        group_item_count += add;
        if (group_item_count <= 0) {
            $('#inventory #group_items_count_' + group)[0].textContent = '';
        } else {
            $('#inventory #group_items_count_' + group)[0].textContent = group_item_count;
//            $('#inventory #group_items_count_' + group).val(group_item_count);
        }
        InventoryCalc(0);
    }

    this.remove = function (count) {
        if (item_input.length == 0) return
        if (item_count > 0) {
            item_count -= count;
            if (item_count == 0) {
                $('#inventory input#' + id).val("");
                $('#inventory div[data-item-id=' + id + ']').removeClass('selected-item');
                $('#inventory .item_list div[data-item-id=' + id + ']').parent().remove()
                if ($('#cont_group_'+item_input.attr('category')+' #hide-selected')[0].checked) {
                    $('ul.items div[data-item-id=' + id + ']').parent().show();
                }

            } else {
                $('#inventory input#' + id).val(item_count);
            }
            this.set_group_item(-count);
        }
        InventoryCalc(0);
    }

    return this;
}


function UserInventory(items) {
    $('#inventory input').val("");
    $('#inventory div').removeClass('selected-item');
    $('#inventory .item_list div').parent().remove()
    $('#inventory .group_items_count').text('');
    InventoryCalc(0);
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (item.category == 'custom') {
            AddCustomItem(item);
            continue;
        }
        InventoryItem(item.id).add(item.quants);
    }
};

function on_focus_item(){
    $(this).attr('old_value',$(this).val() * 1);
}

function on_change_item_counter() {
        var my_val = $(this).val() * 1;
        var old_val = $(this).attr('old_value') * 1;
        $(this).val(old_val);
        if ( !isNaN(my_val) && my_val > 0){
            if ( $(this).attr('id') == "custom" ){
                if (old_val > my_val) {
                    set_group_items_count("custom", -(old_val - my_val));
                } else {
                    set_group_items_count("custom", my_val - old_val);
                }
                InventoryCalc(0);
            } else {
                if (old_val > my_val) {
                    InventoryItem($(this)[0].id).remove(old_val - my_val);
                } else {
                    InventoryItem($(this)[0].id).add(my_val - old_val)
                }
            }

        } else {
            my_val = 0;
        }
        if ( my_val <= 0 ) {
            my_val = "";
        }
        $(this).val(my_val);
    }

function disableSubmitOnEnter(e) {
    // if (this.event.which == 13) // Enter key = keycode 13 , this is for pure javascript without jQuery
    if (e.which == 13)
    {
        $(this).next().focus();  //Use whatever selector necessary to focus the 'next' input
        on_change_item_counter.call(e.target)
        return false;
    }
}



function Inventory() {

    $('#QuoteForm').on("keypress",disableSubmitOnEnter);


    $("#inventory input.extch").on("click", function () {
        if ($(this).prop("checked") == true) {
            $(this).next(".extra").show("blind");
        } else {
            $(this).next(".extra").hide("blind");
        }
    });
    $("#inventory div.tab-content #all_items").show();



/*    $("div#inventory input.item-counter").on("focus", function () {
         $(this).attr('old_value',$(this).val() * 1);
    });

    $("div#inventory input.item-counter").on("change", function () {
        var my_val = $(this).val() * 1;
        var old_val = $(this).attr('old_value') * 1;
        $(this).val(old_val);
        if ( !isNaN(my_val)){
            if ( $(this).attr('id') == "custom" ){
                if (old_val > my_val) {
                    set_group_items_count("custom", -(old_val - my_val));
                } else {
                    set_group_items_count("custom", my_val - old_val);
                }
                InventoryCalc(0);
            } else {
                if (old_val > my_val) {
                    InventoryItem($(this)[0].id).remove(old_val - my_val);
                } else {
                    InventoryItem($(this)[0].id).add(my_val - old_val)
                }
            }

        } else {
            my_val = 0;
        }
        if ( my_val <= 0 ) {
            my_val = "";
        }
        $(this).val(my_val);
    }); */

};
// mark



function AddCustomItem(item) {
    if (!item) {
        item = {name: 'Custom Item', quants: 1, length: 1, width: 1, height: 1}
        item = {name: '', quants: '', length: '', width: '', height: ''}
        var error = false;
        for (var name in item) {
            var inp = $("#citemForm").find("input[name=citem_" + name + "]")
            var val = $("#citemForm").find("input[name=citem_" + name + "]").val();
            item[name] = val ? val : item[name];
            if (item[name].length == 0){
                $(inp).attr('style','border-style:solid !important;border-color:red; !important;')
                error = true
            } else {
                $(inp).removeAttr('style');
            }
        }
        if ( error ){
            return
        }
    }
    var citem_cubes = item['length'] * item['width'] * item['height'];
    var existing = $('#inventory ul.items.custom input[item="' + item['name'] + '"][width="'+item['width']+'"][length="'+item['length']+'"][height="'+item['height']+'"]')
    if (existing.length > 0) {
        var count = existing.val() * 1 + (item['quants'] * 1);
        existing.val(count);
        set_group_items_count("custom", item['quants'] * 1);
        InventoryCalc(0);
// Not finished
        return;
    }
    var newitem = $("#custom_template").clone();
    newitem.find('input').val(item['quants']);
    newitem.find('input').attr("cubes", citem_cubes);
    newitem.find('input').attr("item", item['name']);
    newitem.find('input').attr("length", item['length']);
    newitem.find('input').attr("width", item['width']);
    newitem.find('input').attr("height", item['height']);
    newitem.find('input').attr("weight", item['weight']);
    newitem.find('div').append(item['name'] + '<br>' + item['length'] + 'x' + item['width'] + 'x' + item['height']);
    newitem.removeAttr('style');
    newitem.removeAttr('id');
    $("#inventory ul.items.custom").append(newitem)
    set_group_items_count("custom", item['quants'] * 1);
    InventoryCalc(0);
    return false
}

// mark
function InventoryCalc(max) {
    if (max == 1) {
        var TotalItems = 1;
        var TotalCubes = $("input[name=MaxCubes]").val();
        $("#inventory ul.user-items input.inventories").val(0);
    } else {
        var TotalItems = 0;
        var TotalCubes = 0;
        $("#inventory ul.user-items input.inventories").each(function () {
            if ($(this).val() > "0") {
                TotalItems = TotalItems + $(this).val() * 1;
                TotalCubes = TotalCubes + ($(this).attr("cubes") * 1) * ($(this).val() * 1);
            }
        });
    }

    $("#inventory .total-cubes").html(TotalCubes);
    var scope = angular.element('#estimateCtrl').scope();
    scope.form.fields.original_cu_ft.value = parseInt(TotalCubes);
    scope.original_lbs = 7 * scope.original_cu_ft;
    scope.getTotal();
    $("#inventory .total-items").html(TotalItems);



}
// TODO: fix change view on all tabs now it affects only current tab, edit existing custom items,

function inventoryPlus(elem) {
    var u = $(elem).parent("span").find("input").val() * 1;
    var input_id = $(elem).parent("span").find("input")[0].id;
    InventoryItem(input_id).add(1);
    update_model()
}

function inventoryMinus(elem) {
    InventoryItem($(elem).parent("span").find("input")[0].id).remove(1);
    update_model()
}

function inventorySummaryPlus(elem) {
    var u = $(elem).next("input").val() * 1;
    var input_id = $(elem).next("input")[0].id
    InventoryItem(input_id).add(1);
    InventoryCalc(0);
}

function inventorySummaryMinus(elem) {
    InventoryItem($(this).prev("input")[0].id).remove(1);
}

function hideInventory(elem) {
        if (elem.checked) {
            $(elem).parent().parent().parent().find("li .selected-item").parent().hide()
//            $("ul.items > li .selected-item").parent().hide()
            return
        }
        if ($(elem).parent().parent().parent().parent().find('.finder').val().length > 0) {
            $(elem).parent().parent().parent().find("li.matched .selected-item").parent().show()
//            $("ul.items > li.matched .selected-item").parent().show()
            return
        }
        $(elem).parent().parent().parent().find("li .selected-item").parent().show()
//        $("ul.items > li .selected-item").parent().show()
};

function finderKeyUp(elem) {
        var find = $(elem).val().toLowerCase();
        var hide_selected = $(elem).parent("ul").find('#hide-selected')[0].checked
        $(elem).parent("ul").find("li").each(function () {
            $(this).removeClass("matched");
            if (find > "") {
                var val = $(this).find("span.itemname").html().toLowerCase().indexOf(find);
                if (val > -1) {
                    if ((hide_selected && !$(this).find(".selected-item").length) || !hide_selected) {
                        $(this).show();
                    }
                    $(this).addClass("matched");
                    return;

                } else {
                    $(this).hide();
                    return
                }
            }
            if ((hide_selected && !$(this).find(".selected-item").length) || !hide_selected) {
                $(this).show()
            }
        });
};


function customItemAdd() {
    AddCustomItem(null);
    update_model()
};



function customItemDelete(elem)  {
        var u = $(elem).parent().find("input").val() * 1;
        $(elem).parent("div").parent("li").remove();
        set_group_items_count("custom", -u);
        InventoryCalc(0);
        update_model()
};



function customItemPlus(elem) {
        var u = $(elem).parent("span").find("input").val() * 1;
        $(elem).parent("span").find("input").val(u + 1);
        set_group_items_count("custom", 1);
        InventoryCalc(0);
        update_model()
};

function customItemMinus(elem) {
        var input = $(elem).parent("span").find("input")
        var u = input.val() * 1;
        if (u >= 1) {
            input.val(u - 1);
        }
        if (input.val() == 0) {
            input.val("");
            $(elem).parent().parent().parent().remove();
        }
        set_group_items_count("custom", -1);
        InventoryCalc(0);
        update_model()
}

function update_model() {
    var my_items = [];

    $("#inventory ul.user-items input.inventories").each(function () {
        if ($(this).val() > "0") {
            var inv = {};
            if ($(this).attr("id") == 'custom') {
                inv = {
                    'category': 'custom',
                    'name': $(this).attr("item"),
                    'quants': parseInt($(this).val()),
                    'height': parseInt($(this).attr("height")),
                    'width': parseInt($(this).attr("width")),
                    'length': parseInt($(this).attr("length")),
//                     'ft': parseInt($(this).attr("cubes")),
                }
            } else {
                inv = {
                    'category': parseInt($(this).attr("category")),
                    'id': parseInt($(this).attr("id")),
                    // 'ft': parseInt($(this).attr("cubes")),
                    'quants': parseInt($(this).val()),
                    // 'name': $(this).attr("item")
                }
            }
            my_items.push(inv)
        }
//        $(this).remove();
    });
    if ($("input[name=inventories]").length) {
        var ex_items = $("input[name=inventories]");
        var sorted_items = [];
        var new_items = my_items;
        for (var e = 0; e < ex_items.length; e++) {
            for (var i = 0; i < my_items.length; i++) {
                if (my_items[i].id == ex_items[e].id) {
                    sorted_items.push(my_items[i])
                    new_items.splice(i, 1);
                    break;
                }
            }
        }
        sorted_items = sorted_items.concat(new_items);
        var val = JSON.stringify(sorted_items);
        $("input[name=inventories]").val(val)
        var scope = $("input[name=inventories]").scope();
        scope.form.fields.inventories.value  = val;
        scope.$apply();
    }
    ;

    return null;
}
