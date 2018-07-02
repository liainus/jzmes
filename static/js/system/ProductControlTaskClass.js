/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_ProductControlTask.json';
    var urlPrefix = '/allProductControlTasks/';
    var idPrefix = 'ProductControlTaskClass';
    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";
    var titleText = "计划物料信息";

    function createKeyIDObj(keyID){
    return {
        ID:keyID
    }}
    

     $('input[name="iProductControlTaskName"]').change(function () {
         var sProductControlTaskName = $('input[name="iProductControlTaskName"]').val();
        if(Bee.StringUtils.isNotEmpty(sProductControlTaskName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iProductControlTaskCode"]').change(function () {
        //  var sProductControlTaskCode = $('input[name="iProductControlTaskCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sProductControlTaskCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iProductControlTaskSeq"]').change(function () {
        //  var sProductControlTaskSeq = $('input[name="iProductControlTaskSeq"]').val();
        // if(Bee.StringUtils.isInteger(sProductControlTaskSeq)){
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
        Width:'700',
        scrollbarSize:'500px',
        columns: [[
            {
                field: 'ck',
                width: 100,
                checkbox: true,
                align: 'center'
            },
            {
                field: 'ID',
                title: 'ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PDCtrlTaskCode',
                title: '产品段任务编号',
                align: 'center',
                width: 100
            },
            {
                field: 'PDCtrlTaskName',
                title: '产品段任务名称',
                align: 'center',
                width: 100
            },
            {
                field: 'Desc',
                title: '说明',
                align: 'center',
                width: 100
            },
            {
                field: 'LowLimit',
                title: '设定低限',
                align: 'center',
                width: 100
            },
            {
                field: 'HighLimit',
                title: '设定高限',
                align: 'center',
                width: 100
            },
            {
                field: 'RelateTaskCount',
                title: '相关任务次数',
                align: 'center',
                width: 100
            },
            {
                field: 'ProductRuleID',
                title: '产品定义ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PUID',
                title: '工艺段ID',
                align: 'center',
                width: 100
            },
            {
                field: 'Seq',
                title: '顺序',
                align: 'center',
                width: 100
            }
        ]]
    });


    ProductControlTaskClassToolbar = {
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
                url: '/allProductControlTasks/Search',
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
            $('input[name="Name"]').focus();
            $('input[name="iID"]').attr("disabled", "disabled");
            $('input[name="iID"]').val();
            $('input[name="iPDCtrlTaskCode"]').val();
            $('input[name="iPDCtrlTaskName"]').val();
            $('input[name="iDesc"]').val();
            $('input[name="iLowLimit"]').val();
            $('input[name="iHighLimit"]').val();
            $('input[name="iRelateTaskCount"]').val();
            $('input[name="iProductRuleID"]').val();
            $('input[name="iPUID"]').val();
            $('input[name="iSeq"]').val();         // $('input[name="iProductControlTaskSeq"]').onChange()
            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#ProductControlTaskClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#ProductControlTaskClassCombobox').combobox('showPanel');
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
                    $('input[name="iPDCtrlTaskCode"]').val(row.PDCtrlTaskCode);
                    $('input[name="iPDCtrlTaskName"]').val(row.PDCtrlTaskName);
                    $('input[name="iDesc"]').val(row.Desc);
                    $('input[name="iLowLimit"]').val(row.LowLimit);
                    $('input[name="iHighLimit"]').val(row.HighLimit);
                    $('input[name="iRelateTaskCount"]').val(row.RelateTaskCount);
                    $('input[name="iProductRuleID"]').val(row.ProductRuleID);
                    $('input[name="iPUID"]').val(row.PUID);
                    $('input[name="iSeq"]').val(row.Seq);
                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象  
                    if (row.IsEnable == '禁用') {

                        $("[switchbuttonName='IsEnable']").switchbutton("uncheck");
                    }else {
                        $("[switchbuttonName='IsEnable']").switchbutton("check");
                    }
                    $('input[name="iProductControlTaskName"]').focus();
                    // $('#ProductControlTaskClassCombobox').combobox('setValue',row['ProductControlTaskClass'].id);
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
                            url: '/allProductControlTasks/Delete',
                            method: 'POST',
                            traditional: true,
                            // data: JSON.stringify(ids),
                            data: a,
                            dataType: 'json',
                            beforeSend: function () {
                                $.messager.progress({
                                    text: '正在删除中...'
                                });
                            },
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
           
            stmp = $('input[name="iSeq"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iSeq"]').val("");
                alert('Warning：计划顺序号输入错误,请输入数字！');
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
                    PDCtrlTaskCode:$('input[name="iPDCtrlTaskCode"]').val(),
                    PDCtrlTaskName:$('input[name="iPDCtrlTaskName"]').val(),
                    Desc:$('input[name="iDesc"]').val(),
                    LowLimit:$('input[name="iLowLimit"]').val(),
                    HighLimit:$('input[name="iHighLimit"]').val(),
                    RelateTaskCount:$('input[name="iRelateTaskCount"]').val(),
                    ProductRuleID:$('input[name="iProductRuleID"]').val(),
                    PUID:$('input[name="iPUID"]').val(),
                    Seq:$('input[name="iSeq"]').val()
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allProductControlTasks/Create',
                    method: 'POST',
                    traditional: true,
                    data: entity,
                    dataType: 'json',
                    cache: false,

                    // beforeSend: function () {
                    //
                    //     $.messager.progress({
                    //         text: '正在' + message + '中...'
                    //     });
                    // },
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
                            $(tableId).datagrid('reload',{ url: "/allProductControlTasks/Find?_t=" + new Date().getTime() });
                            $(tableid).datagrid('clearSelections');
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
        Width:'700',
        scrollbarSize:'500px',
        columns: [[
            {
                field: 'ck',
                width: 100,
                checkbox: true,
                align: 'center'
            },
            {
                field: 'ID',
                title: 'ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PDCtrlTaskCode',
                title: '产品段任务编号',
                align: 'center',
                width: 100
            },
            {
                field: 'PDCtrlTaskName',
                title: '产品段任务名称',
                align: 'center',
                width: 100
            },
            {
                field: 'Desc',
                title: '说明',
                align: 'center',
                width: 100
            },
            {
                field: 'LowLimit',
                title: '设定低限',
                align: 'center',
                width: 100
            },
            {
                field: 'HighLimit',
                title: '设定高限',
                align: 'center',
                width: 100
            },
            {
                field: 'RelateTaskCount',
                title: '相关任务次数',
                align: 'center',
                width: 100
            },
            {
                field: 'ProductRuleID',
                title: '产品定义ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PUID',
                title: '工艺段ID',
                align: 'center',
                width: 100
            },
            {
                field: 'Seq',
                title: '顺序',
                align: 'center',
                width: 100
            }
        ]]
    });
            $(tableId).datagrid('reload');
            $(tableid).datagrid('clearSelections');
           
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
