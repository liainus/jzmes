/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_PlanManager.json';
    var urlPrefix = '/allPlanManagers/';
    var idPrefix = 'PlanManagerClass';
    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";
    var titleText = "生产批次管理";

    function createKeyIDObj(keyID){
    return {
        ID:keyID
    }}
    

     $('input[name="iPlanManagerName"]').change(function () {
         var sPlanManagerName = $('input[name="iPlanManagerName"]').val();
        if(Bee.StringUtils.isNotEmpty(sPlanManagerName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iPlanManagerCode"]').change(function () {
        //  var sPlanManagerCode = $('input[name="iPlanManagerCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sPlanManagerCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iPlanManagerSeq"]').change(function () {
        //  var sPlanManagerSeq = $('input[name="iPlanManagerSeq"]').val();
        // if(Bee.StringUtils.isInteger(sPlanManagerSeq)){
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
                align: 'center'
            },
            {
                field: 'ID',
                title: 'ID',
                align: 'center',
                width: 100
            },
            {
                field: 'SchedulePlanID',
                title: '单位编码',
                align: 'center',
                width: 100
            },
            {
                field: 'BatchID',
                title: '批次号',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandID',
                title: '品名',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandName',
                title: '品名名称',
                align: 'center',
                width: 100
            },
            {
                field: 'PlanQuantity',
                title: '计划重量',
                align: 'center',
                width: 100
            },
            {
                field: 'Unit',
                title: '单位',
                align: 'center',
                width: 100
            },
            {
                field: 'Seq',
                title: '顺序号',
                align: 'center',
                width: 100
            },
            {
                field: 'PlanBeginTime',
                title: '计划开始时间',
                align: 'center',
                width: 100
            },
            {
                field: 'Type',
                title: '类型',
                align: 'center',
                width: 100
            },
            {
                field: 'LineID',
                title: '生产线',
                align: 'center',
                width: 100
            },
            {
                field: 'LineName',
                title: '生产线名称',
                align: 'center',
                width: 100
            },
        ]]
    });


    PlanManagerClassToolbar = {
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
                url: '/allPlanManagers/Search',
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
            $('input[name="iSchedulePlanID"]').val();
            $('input[name="iBatchID"]').val();
            $('input[name="iBrandID"]').val();
            $('input[name="iBrandName"]').val();
            $('input[name="iPlanQuantity"]').val();
            $('input[name="iUnit"]').val();
            $('input[name="iSeq"]').val();
            $('input[name="iPlanBeginTime"]').val();
            $('input[name="iType"]').val();
             $('input[name="iLineID"]').val();
              $('input[name="iLineName"]').val();

            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#PlanManagerClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#PlanManagerClassCombobox').combobox('showPanel');
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
                    $('input[name="iSchedulePlanID"]').val(row.SchedulePlanID);
                    $('input[name="iBatchID"]').val(row.BatchID);
                    $('input[name="iBrandID"]').val(row.BrandID);
                    $('input[name="iBrandName"]').val(row.BrandName);
                    $('input[name="iPlanQuantity"]').val(row.PlanQuantity);
                    $('input[name="iUnit"]').val(row.Unit);
                    $('input[name="iSeq"]').val(row.Seq);
                    $('input[name="iPlanBeginTime"]').val(row.PlanBeginTime);
                    $('input[name="iType"]').val(row.Type);
                    $('input[name="iLineID"]').val(row.LineID);
                    $('input[name="iLineName"]').val(row.LineName);

                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象  
                    if (row.IsEnable == '禁用') {

                        $("[switchbuttonName='IsEnable']").switchbutton("uncheck");
                    }else {
                        $("[switchbuttonName='IsEnable']").switchbutton("check");
                    }
                    $('input[name="iPlanManagerName"]').focus();
                    // $('#PlanManagerClassCombobox').combobox('setValue',row['PlanManagerClass'].id);
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
                            url: '/allPlanManagers/Delete',
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
            var stmp = $('input[name="iPlanManagerCode"]').val();

            stmp = $('input[name="iSeq"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iSeq"]').val("");
                alert('Warning：组织机构顺序输入错误,请输入数字！');
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
                    SchedulePlanID:$('input[name="iSchedulePlanID"]').val(),
                    BatchID:$('input[name="iBatchID"]').val(),
                    BrandID:$('input[name="iBrandID"]').val(),
                    BrandName:$('input[name="iBrandName"]').val(),
                    PlanQuantity:$('input[name="iPlanQuantity"]').val(),
                    Unit:$('input[name="iUnit"]').val(),
                    Seq:$('input[name="iSeq"]').val(),
                    PlanBeginTime:$('input[name="iPlanBeginTime"]').val(),
                    Type:$('input[name="iType"]').val(),
                    LineID:$('input[name="iLineID"]').val(),
                    LineName:$('input[name="iLineName"]').val()
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allPlanManagers/Create',
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
                            $(tableId).datagrid('reload',{ url: "/allPlanManagers/Find?_t=" + new Date().getTime() });
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
                field: 'SchedulePlanID',
                title: '单位编码',
                align: 'center',
                width: 100
            },
            {
                field: 'BatchID',
                title: '批次号',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandID',
                title: '品名',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandName',
                title: '品名名称',
                align: 'center',
                width: 100
            },
            {
                field: 'PlanQuantity',
                title: '计划重量',
                align: 'center',
                width: 100
            },
            {
                field: 'Unit',
                title: '单位',
                align: 'center',
                width: 100
            },
            {
                field: 'Seq',
                title: '顺序号',
                align: 'center',
                width: 100
            },
            {
                field: 'PlanBeginTime',
                title: '计划开始时间',
                align: 'center',
                width: 100
            },
            {
                field: 'Type',
                title: '类型',
                align: 'center',
                width: 100
            },
            {
                field: 'LineID',
                title: '生产线ID',
                align: 'center',
                width: 100
            },
            {
                field: 'LineName',
                title: '生产线名称',
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
