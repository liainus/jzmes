/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_Equipment.json';
    var urlPrefix = '/allEquipments/';
    var idPrefix = 'EquipmentClass';
    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";
    var titleText = "设备";

    function createKeyIDObj(keyID){
    return {
        ID:keyID
    }}
    

     $('input[name="iEquipmentName"]').change(function () {
         var sEquipmentName = $('input[name="iEquipmentName"]').val();
        if(Bee.StringUtils.isNotEmpty(sEquipmentName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iEquipmentCode"]').change(function () {
        //  var sEquipmentCode = $('input[name="iEquipmentCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sEquipmentCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iEquipmentSeq"]').change(function () {
        //  var sEquipmentSeq = $('input[name="iEquipmentSeq"]').val();
        // if(Bee.StringUtils.isInteger(sEquipmentSeq)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('序号要为整数！:');
        //    return true;
        // }})

 });

    $(tableId).datagrid({
        url: urlPrefix + 'Find', // urlPrefix + 'findAll',
        queryParams: {
            EQPName: ''
        },
        method: 'get',
        rownumbers: true,
        singleSelect: false,
        autoRowHeight: false,
        fit: false,
        pagination: true,
        fitColumns: true,
        striped: true,
        checkOnSelect: true,
        selectOnCheck: true,
        collapsible: true,
        toolbar: toolbarId,
        pageSize: 10,
        pagelist:[10,20,30,40,50],
        idField: 'ID',
        columns: [[
            {
                field: 'ck',
                width: 100,
                checkbox: true,
                align: 'center',
            },
            {
                field: 'EQPCode',
                title: '设备编码',
                align: 'center',
                width: 100
            },
            {
                field: 'EQPName',
                title: '设备名称',
                align: 'center',
                width: 100
            },
             {
                field: 'SupplierName',
                title: '供应商',
                align: 'center',
                width: 100
            },
            {
                field: 'Equipment_State',
                title: '设备状态',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Model',
                title: '基本参数',
                width: 100,
                align: 'center'
            },
            {
                field: 'CostAttach',
                title: '成本归属',
                width: 100,
                align: 'center'
            },
            {
                field: 'Procurement_Date',
                title: '采购日期',
                width: 100,
                align: 'center'
            } ,
            {
                field: 'Desc',
                title: '备注说明',
                width: 100,
                align: 'center'
            }
        ]]
    });


    EquipmentClassToolbar = {
        message: "",
        search: function () {
            a = $('input[name="search"]').val();
            $(tableId).datagrid('load',{
                EQPName:a
            })
        },
        create: function () {
            $(dialogId).dialog('open').dialog('setTitle', '新增' + titleText);
            $(formTitleId).text(titleText);
            $('input[name="iID"]').attr("disabled", "disabled");
            $('input[name="iID"]').val("");
            $('input[name="EQPCode"]').val("");
            $('input[name="EQPName"]').val("");
            $('input[name="SupplierName"]').val("");
            $('input[name="Equipment_Model"]').val("");
            $('#PUID option:contains("请选择")').prop("selected", 'selected');
            $('#Equipment_State option:contains("请选择")').prop("selected", 'selected');
            $('#CostAttach option:contains("请选择")').prop("selected", 'selected');
            $('#Procurement_Date').datetimebox({value: ""});
            $('input[name="Desc"]').val("");

            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#EquipmentClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#EquipmentClassCombobox').combobox('showPanel');
            // });
        },
        update: function () {
            var rows = $(tableId).datagrid('getSelections');
            if (rows.length > 1) {
                $.messager.alert('警告操作！', '编辑记录只能选定一条数据！', 'warning');
            } else if (rows.length == 1) {
                var row = $(tableId).datagrid('getSelected');
                if (row) {
                    $(dialogId).dialog('open').dialog('setTitle', '编辑' + titleText);
                    $(formTitleId).text(titleText);
                    //$(formId).form('load', row);
                    $('input[name="iID"]').attr("disabled", "disabled");
                    $('input[name="iID"]').val(row.ID);
                    $('input[name="EQPCode"]').val(row.EQPCode);
                    $('input[name="EQPName"]').val(row.EQPName);
                    $('input[name="SupplierName"]').val(row.SupplierName);
                    $('input[name="Equipment_Model"]').val(row.Equipment_Model);
                    $('#PUID option:contains('+row.PUID+')').prop("selected", 'selected');
                    $('#Equipment_State option:contains('+row.Equipment_State+')').prop("selected", 'selected');
                    $('#CostAttach option:contains('+row.CostAttach+')').prop("selected", 'selected');
                    $('#Procurement_Date').datebox("setValue",row.Procurement_Date);
                    $('input[name="Desc"]').val(row.Desc);
                    message = '编辑' + titleText;

                };
            } else if (rows.length == 0) {
                $.messager.alert('警告操作！', '请至少选定一条数据进行编辑！', 'warning');
            }
        },
        delete: function () {
            var rows = $(tableId).datagrid('getSelections');
            if (rows.length > 0) {
                var jsonarray=[];
                $.messager.confirm('确定操作', '您正在删除所选的记录吗？', function (flag) {
                    if (flag) {
                        var PrimaryKey = "ID";
                        var a = "";
                        for (var i = 0; i < rows.length; i++) {
                            // ids.push(parseInt((rows[i].id)));
                            var obj=createKeyIDObj(parseInt(rows[i].ID));
                            jsonarray.push(obj);
                        }
                        // a = JSON.stringify([{"ID":9},{"ID":10}])
                        a = JSON.stringify(jsonarray);
                        $.ajax({
                            url: '/allEquipments/Delete',
                            method: 'POST',
                            traditional: true,
                            // data: JSON.stringify(ids),
                            data: a,
                            dataType: 'json',
                            success: function (data) {
                                $.messager.progress('close');

                                if (data) {
                                    $(tableId).datagrid('loaded');
                                    $(tableId).datagrid('load');
                                    $(tableId).datagrid('unselectAll');
                                    $.messager.show({
                                        title: '提示',
                                        timeout:1000,
                                        msg: '删除' + titleText + '成功',
                                        style: {
                                            right: '',
                                            top: document.body.scrollTop + document.documentElement.scrollTop,
                                            bottom: ''
                                        }
                                    });
                                }
                            }
                        });
                    }
                });
            } else {
                $.messager.alert('提示', '请选择要删除的记录！', 'info');
            }
        },
        save: function () {
            var validate=$(formId).form('validate');
            var strID = $('input[name="iID"]').val();
            var msg = ""
            var urlAddr = ""
            var stmp = $('input[name="EQPCode"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：设备编码不能为空！');
               return false;
            }
            stmp = $('input[name="EQPName"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：设备名称不能为空！');
               return false;
            }

            if (strID.length >= 1){
                urlAddr = urlPrefix + 'Update'
                hintinfo = "更新数据"
            }
            else {
                urlAddr = urlPrefix + 'Create'
                hintinfo = "新增数据"
            }
                var entity = {
                    ID:$('input[name="iID"]').val(),
                    EQPCode:$('input[name="EQPCode"]').val(),
                    EQPName:$('input[name="EQPName"]').val(),
                    SupplierName:$('input[name="SupplierName"]').val(),
                    Equipment_Model:$('input[name="Equipment_Model"]').val(),
                    PUID:$('#PUID').find("option:selected").val(),
                    Equipment_State:$('#Equipment_State').find("option:selected").val(),
                    CostAttach:$('#CostAttach').find("option:selected").val(),
                    Procurement_Date:$('#Procurement_Date').datebox('getValue'),
                    Desc:$('input[name="Desc"]').val(),
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allEquipments/Create',
                    method: 'POST',
                    traditional: true,
                    data: entity,
                    dataType: 'json',
                    cache: false,
                    error: function(data){
                           console.log(data.responseText)
                           alert(hintinfo+ "异常，请刷新后重试...");
                             },
                    success: function (data,response,status) {
                        $.messager.progress('close');
                        if(data == "OK"){
                            $.messager.show({
                                title: '提示',
                                msg: message + hintinfo  + '成功',
                                timeout:1000,
                                style: {
                                    right: '',
                                    top: document.body.scrollTop + document.documentElement.scrollTop,
                                    bottom: ''
                                }
                            });

                            $(formId).form('reset');
                            $(dialogId).dialog('close');
                            $(tableId).datagrid('reload');
                            //$(tableid).datagrid('clearSelections');
                        } else {
                            $.messager.alert('失败！', '未知错误导致失败，请重试！', 'warning');
                        }
                    }
                });
            // }
        },
        refresh: function () {
            $(tableId).datagrid({
            url: urlPrefix + 'Find', // urlPrefix + 'findAll',
            method: 'get',
            rownumbers: true,
            singleSelect: false,
            autoRowHeight: false,
            fit: false,
            pagination: true,
            fitColumns: true,
            striped: true,
            checkOnSelect: true,
            selectOnCheck: true,
            collapsible: true,
            toolbar: toolbarId,
            pageSize: 10,
            pagelist:[10,20,30,40,50],
            idField: 'ID',
            columns: [[
                {
                    field: 'ck',
                    width: 100,
                    checkbox: true,
                    align: 'center',
                },
                {
                    field: 'EQPCode',
                    title: '设备编码',
                    align: 'center',
                    width: 100
                },
                {
                    field: 'EQPName',
                    title: '设备名称',
                    align: 'center',
                    width: 100
                },
                 {
                    field: 'SupplierName',
                    title: '供应商',
                    align: 'center',
                    width: 100
                },
                {
                    field: 'Equipment_State',
                    title: '设备状态',
                    width: 100,
                    align: 'center'
                },
                {
                    field: 'Equipment_Model',
                    title: '基本参数',
                    width: 100,
                    align: 'center'
                },
                {
                    field: 'CostAttach',
                    title: '成本归属',
                    width: 100,
                    align: 'center'
                },
                {
                    field: 'Procurement_Date',
                    title: '采购日期',
                    width: 100,
                    align: 'center'
                } ,
                {
                    field: 'Desc',
                    title: '备注说明',
                    width: 100,
                    align: 'center'
                }
            ]]
        });
            $(tableId).datagrid('reload');
            $(tableId).datagrid('clearSelections');
           
        }

    }

    //datagrid表格右键操作
    $(tableId).datagrid({
        onRowContextMenu: function (e, rowIndex, rowData) { //右键时触发事件
            //三个参数：e里面的内容很多，真心不明白，rowIndex就是当前点击时所在行的索引，rowData当前行的数据
            e.preventDefault(); //阻止浏览器捕获右键事件
            $(this).datagrid("clearSelections"); //取消所有选中项
            $(this).datagrid("selectRow", rowIndex); //根据索引选中该行
            $('#contextmenu').menu('show', {
                //显示右键菜单
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
            e.preventDefault();  //阻止浏览器自带的右键菜单弹出
        }
    });

});
