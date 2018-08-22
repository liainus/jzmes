/**
 * Created by zcx on 2018/8/21.
 */
$(function () {
    var urlPrefix = '/equipmentModel/';
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
    $(tableId).datagrid({
        url: urlPrefix + 'pequipmentFind', // urlPrefix + 'findAll',
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
                field: 'PUID',
                title: '工艺段ID',
                width: 100,
                align: 'center'
            },
            {
                field: 'Desc',
                title: '描述',
                width: 100,
                align: 'center'
            }
        ]]
    });
    EquipmentClassToolbar = {
        message: "",
        search: function () {
            a = $.trim($('input[name="search"]').val());
            if  (Bee.StringUtils.isEmpty(a)){
                return false;
            }
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
            $('#PUID option:contains("请选择")').prop("selected", 'selected');
            $('input[name="Desc"]').val("");
            message = '新增' + titleText;
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
                    $('input[name="iID"]').attr("disabled", "disabled");
                    $('input[name="iID"]').val(row.ID);
                    $('input[name="EQPCode"]').val(row.EQPCode);
                    $('input[name="EQPName"]').val(row.EQPName);
                    $('#PUID option:contains('+row.PUID+')').prop("selected", 'selected');
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
                            var obj=createKeyIDObj(parseInt(rows[i].ID));
                            jsonarray.push(obj);
                        }
                        a = JSON.stringify(jsonarray);
                        $.ajax({
                            url: '/equipmentModel/pequipmentDelete',
                            method: 'get',
                            traditional: true,
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
            stmp = $('#PUID').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺段名称不能为空！');
               return false;
            }
            if (strID.length >= 1){
                urlAddr = urlPrefix + 'pequipmentUpdate'
                hintinfo = "更新数据"
            }
            else {
                urlAddr = urlPrefix + 'pequipmentCreate'
                hintinfo = "新增数据"
            }
                var entity = {
                    ID:$('input[name="iID"]').val(),
                    EQPCode:$('input[name="EQPCode"]').val(),
                    EQPName:$('input[name="EQPName"]').val(),
                    PUID:$('#PUID').find("option:selected").val(),
                    Desc:$('input[name="Desc"]').val()
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
                        } else {
                            $.messager.alert(obj1[0].status + '失败！', '未知错误导致失败，请重试！', 'warning');
                        }
                    }
                });
        },
        refresh: function () {
            $(tableId).datagrid({
        url: urlPrefix + 'pequipmentFind', // urlPrefix + 'findAll',
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
                field: 'PUID',
                title: '工艺段ID',
                width: 100,
                align: 'center'
            },
            {
                field: 'Desc',
                title: '描述',
                width: 100,
                align: 'center'
            }
        ]]
    });
            $(tableId).datagrid('reload');
            $(tableId).datagrid('clearSelections');
           
        }

    }
    $(tableId).datagrid({
        onRowContextMenu: function (e, rowIndex, rowData) { //右键时触发事件
            e.preventDefault(); //阻止浏览器捕获右键事件
            $(this).datagrid("clearSelections"); //取消所有选中项
            $(this).datagrid("selectRow", rowIndex); //根据索引选中该行
            $('#contextmenu').menu('show', {
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
            e.preventDefault();  //阻止浏览器自带的右键菜单弹出
        }
    });
});