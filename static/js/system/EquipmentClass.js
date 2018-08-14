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
                field: 'ID',
                title: 'ID',
                align: 'center',
                width: 100
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
                field: 'EnterpriseCode',
                title: '企业编码',
                align: 'center',
                width: 100
            },
            {
                field: 'EnterpriseName',
                title: '企业名称',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Model',
                title: '设备型号',
                width: 100,
                align: 'center'
            } ,
            {
                field: 'Manufactor',
                title: '生产厂家',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_State',
                title: '设备状态',
                width: 100,
                align: 'center'
            },
            {
                field: 'money',
                title: '金额(原值)',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Type',
                title: '设备类型',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Power',
                title: '设备功率(KW/h)',
                width: 100,
                align: 'center'
            },
            {
                field: 'PUID',
                title: '工艺段ID',
                width: 100,
                align: 'center'
            },
            {
                field: 'Manufacture_Date',
                title: '生产日期',
                width: 100,
                align: 'center'
            },
            {
                field: 'Desc',
                title: '描述',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_From',
                title: ' 来源',
                width: 100,
                align: 'center'
            }
        ]]
    });


    EquipmentClassToolbar = {
        message: "",
        search: function () {
            // $(tableId).datagrid('load', {
            //     Name: $.trim($('input[name="search"]').val())
            // });
            a = $.trim($('input[name="search"]').val());
            if  (Bee.StringUtils.isEmpty(a)){
                return false;
            }
            //a = JSON.stringify(a);
            var entity = {
                    condition:a
                };
            $.ajax({
                url: '/allEquipments/Search',
                method: 'POST',
                traditional: true,
                // data: JSON.stringify(ids),
                data: entity,
                dataType: 'json',
                success: function (data) {
                    $.messager.progress('close');

                    if (data) {
                        // $(tableId).datagrid('loaded');
                        // $(tableId).datagrid('load');
                        // $(tableId).datagrid('unselectAll');
                        $(tableId).datagrid('loadData', data);
                        $.messager.show({
                            title: '提示',
                            timeout: 1000,
                            msg: '查询' + titleText + '成功',
                            style: {
                                right: '',
                                top: document.body.scrollTop + document.documentElement.scrollTop,
                                bottom: ''
                            }
                        });
                    }
                }
            })
        },
        create: function () {
            $(dialogId).dialog('open').dialog('setTitle', '新增' + titleText);
            $(formTitleId).text(titleText);
            $('input[name="iID"]').attr("disabled", "disabled");
            $('input[name="iID"]').val("");
            $('input[name="EQPCode"]').val("");
            $('input[name="EQPName"]').val("");
            $('input[name="Equipment_Model"]').val("");
            $('input[name="EnterpriseName"]').val("");
            $('input[name="EnterpriseCode"]').val("");
            $('input[name="Equipment_State"]').val("");
            $('input[name="Equipment_Power"]').val("");
            $('input[name="Equipment_Type"]').val("");
            $('input[name="money"]').val("");
            $('input[name="Manufactor"]').val("");
            $('#PUID option:contains("请选择")').prop("selected", 'selected');
            $('#Manufacture_Date').datebox({value: ""});
            $('input[name="Desc"]').val("");
            $('input[name="Equipment_From"]').val("");

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
                    $('input[name="Equipment_Model"]').val(row.Equipment_Model);
                    $('input[name="EnterpriseName"]').val(row.EnterpriseName);
                    $('input[name="EnterpriseCode"]').val(row.EnterpriseCode);
                    $('input[name="Equipment_State"]').val(row.Equipment_State);
                    $('input[name="Equipment_Power"]').val(row.Equipment_Power);
                    $('input[name="Equipment_Type"]').val(row.Equipment_Type);
                    $('input[name="money"]').val(row.money);
                    $('input[name="Manufactor"]').val(row.Manufactor);
                    $('#PUID option:contains('+row.PUID+')').prop("selected", 'selected');
                    $('#Manufacture_Date').datebox("setValue",row.Manufacture_Date);
                    $('input[name="Desc"]').val(row.Desc);
                    $('input[name="Equipment_From"]').val(row.Equipment_From);

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
                    Equipment_Model:$('input[name="Equipment_Model"]').val(),
                    EnterpriseName:$('input[name="EnterpriseName"]').val(),
                    EnterpriseCode:$('input[name="EnterpriseCode"]').val(),
                    Equipment_State:$('input[name="Equipment_State"]').val(),
                    Equipment_Power:$('input[name="Equipment_Power"]').val(),
                    Equipment_Type:$('input[name="Equipment_Type"]').val(),
                    money:$('input[name="money"]').val(),
                    Manufactor:$('input[name="Manufactor"]').val(),
                    PUID:$('#PUID').find("option:selected").val(),
                    Manufacture_Date:$('#Manufacture_Date').datebox('getValue'),
                    Desc:$('input[name="Desc"]').val(),
                    Equipment_From:$('input[name="Equipment_From"]').val()
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
                        {
                }
                        var obj1 = eval(data);
                        if(obj1[0].status == "OK"){
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
                            $(tableId).datagrid('reload',{ url: "/allEquipments/Find?_t=" + new Date().getTime() });
                            //$(tableid).datagrid('clearSelections');
                        } else {
                            $.messager.alert(obj1[0].status + '失败！', '未知错误导致失败，请重试！', 'warning');
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
                field: 'ID',
                title: 'ID',
                align: 'center',
                width: 100
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
                field: 'EnterpriseCode',
                title: '企业编码',
                align: 'center',
                width: 100
            },
            {
                field: 'EnterpriseName',
                title: '企业名称',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Model',
                title: '设备型号',
                width: 100,
                align: 'center'
            } ,
            {
                field: 'Manufactor',
                title: '生产厂家',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_State',
                title: '设备状态',
                width: 100,
                align: 'center'
            },
            {
                field: 'money',
                title: '金额(原值)',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Type',
                title: '设备类型',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_Power',
                title: '设备功率(KW/h)',
                width: 100,
                align: 'center'
            },
            {
                field: 'PUID',
                title: '工艺段ID',
                width: 100,
                align: 'center'
            },
            {
                field: 'Manufacture_Date',
                title: '生产日期',
                width: 100,
                align: 'center'
            },
            {
                field: 'Desc',
                title: '描述',
                width: 100,
                align: 'center'
            },
            {
                field: 'Equipment_From',
                title: ' 来源',
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
