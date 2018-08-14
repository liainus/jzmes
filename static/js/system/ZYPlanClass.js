/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_ZYPlan.json';
    var urlPrefix = '/allZYPlans/';
    var idPrefix = 'ZYPlanClass';
    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";
    var titleText = "计划信息";

    function createKeyIDObj(keyID){
    return {
        ID:keyID
    }}
    

     $('input[name="iZYPlanName"]').change(function () {
         var sZYPlanName = $('input[name="iZYPlanName"]').val();
        if(Bee.StringUtils.isNotEmpty(sZYPlanName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iZYPlanCode"]').change(function () {
        //  var sZYPlanCode = $('input[name="iZYPlanCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sZYPlanCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iZYPlanSeq"]').change(function () {
        //  var sZYPlanSeq = $('input[name="iZYPlanSeq"]').val();
        // if(Bee.StringUtils.isInteger(sZYPlanSeq)){
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
                field: 'PlanNo',
                title: '计划单号',
                align: 'center',
                width: 200
            },
            {
                field: 'BatchID',
                title: '批次号',
                align: 'center',
                width: 200
            },
            {
                field: 'PlanType',
                title: '计划类型',
                align: 'center',
                width: 150
            },
            {
                field: 'BrandName',
                title: '品牌名称',
                align: 'center',
                width: 200
            },
            {
                field: 'ERPOrderNo',
                title: 'ERP订单号',
                align: 'center',
                width: 200
            },
            {
                field: 'PlanQuantity',
                title: '计划数量',
                align: 'center',
                width: 100
            },
            {
                field: 'ActQuantity',
                title: '实际数量',
                align: 'center',
                width: 100
            },
            {
                field: 'TaskStatus',
                title: '任务状态',
                align: 'center',
                width: 100
            }
        ]]
    });


    ZYPlanClassToolbar = {
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
                url: '/allZYPlans/Search',
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
            $('#iPlanDate').datetimebox({value: ""});
            $('input[name="iPlanNo"]').val();
            $('input[name="iBatchID"]').val();
            $('input[name="iPlanSeq"]').val();
            $('#iPUID option:contains("请选择")').prop("selected", 'selected');
            $('input[name="iPlanType"]').val();
            $('input[name="iBrandCode"]').val();
            $('#iBrandName option:contains("请选择")').prop("selected", 'selected');
            $('input[name="iERPOrderNo"]').val();
            $('input[name="iPlanQuantity"]').val();
            $('input[name="iActQuantity"]').val();
            $('#iUnit option:contains("请选择")').prop("selected", 'selected');
            $('#iPlanBeginTime').datetimebox({value: ""});
            $('#iPlanEndTime').datetimebox({value: ""});
            $('#iActBeginTime').datetimebox({value: ""});
            $('#iActEndTime').datetimebox({value: ""});
            $('input[name="iTaskStatus"]').val();
            $('input[name="iLockStatus"]').val();
            $('input[name="iINFStatus"]').val();
            $('input[name="iWMSStatus"]').val();
            // $('input[name="iZYPlanSeq"]').onChange()
            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#ZYPlanClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#ZYPlanClassCombobox').combobox('showPanel');
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
                    $("#iPlanDate").datebox("setValue",row.PlanDate)
                    $('input[name="iPlanNo"]').val(row.PlanNo);
                    $('input[name="iBatchID"]').val(row.BatchID);
                    $('input[name="iPlanSeq"]').val(row.PlanSeq);
                    $('#iPUID option:contains('+row.PUID+')').prop("selected", 'selected');
                    $('input[name="iPlanType"]').val(row.PlanType);
                    $('#iBrandName option:contains('+row.BrandName+')').prop("selected", 'selected');
                    $('input[name="iERPOrderNo"]').val(row.ERPOrderNo);
                    $('input[name="iPlanQuantity"]').val(row.PlanQuantity);
                    $('input[name="iActQuantity"]').val(row.ActQuantity);
                    $('#iUnit option:contains('+row.Unit+')').prop("selected", 'selected');
                    //$('input[name="iEnterTime"]').val(row.EnterTime);
                    $('#iPlanBeginTime').datetimebox("setValue",row.PlanBeginTime);
                    $('#iPlanEndTime').datetimebox("setValue",row.PlanEndTime);
                    $('#iActBeginTime').datetimebox("setValue",row.ActBeginTime);
                    $('#iActEndTime').datetimebox("setValue",row.ActEndTime);
                    $('input[name="iTaskStatus"]').val(row.TaskStatus);
                    $('input[name="iLockStatus"]').val(row.LockStatus);
                    $('input[name="iINFStatus"]').val(row.INFStatus);
                    $('input[name="iWMSStatus"]').val(row.WMSStatus);

                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象  
                    if (row.IsEnable == '禁用') {

                        $("[switchbuttonName='IsEnable']").switchbutton("uncheck");
                    }else {
                        $("[switchbuttonName='IsEnable']").switchbutton("check");
                    }
                    $('input[name="iZYPlanName"]').focus();
                    // $('#ZYPlanClassCombobox').combobox('setValue',row['ZYPlanClass'].id);
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
                            url: '/allZYPlans/Delete',
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
        send:function(){
            var rows = $(tableId).datagrid('getSelections');
            if (rows.length > 0) {
                var jsonarray=[];
                $.messager.confirm('确定操作', '确定要下发所选的记录吗？', function (flag) {
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
                            url: '/ZYPlanXF/zYPlanXF',
                            method: 'GET',
                            traditional: true,
                            // data: JSON.stringify(ids),
                            data: a,
                            dataType: 'json',
                            success: function (data) {
                                $.messager.progress('close')
                                if (data) {
                                    $(tableId).datagrid('loaded');
                                    $(tableId).datagrid('load');
                                    $(tableId).datagrid('unselectAll');
                                    $.messager.show({
                                        title: '提示',
                                        timeout:1000,
                                        msg: '下发' + titleText + '成功',
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
            var stmp = $('#iPlanDate').datetimebox('getValue');
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：生产日期不能为空！');
               return false;
            }
            stmp = $('input[name="iPlanNo"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：计划单号不能为空！');
               return false;
            }
            stmp = $('input[name="iBatchID"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：批次号不能为空！');
               return false;
            }
            stmp = $('#iBrandName').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：品牌名称不能为空！');
               return false;
            }
            stmp = $('#iPUID').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺段编号不能为空！');
               return false;
            }
            stmp = $('input[name="iPlanType"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：计划类型不能为空！');
               return false;
            }
             stmp = $('input[name="iPlanSeq"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPlanSeq"]').val("");
                alert('Warning：计划顺序号输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iERPOrderNo"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：ERP订单号不能为空！');
               return false;
            }
            stmp = $('input[name="iPlanQuantity"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPlanQuantity"]').val("");
                alert('Warning：计划数量输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iActQuantity"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iActQuantity"]').val("");
                alert('Warning：实际数量输入错误,请输入数字！');
                return false;
            }
            stmp = $('#iUnit').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：单位不能为空！');
               return false;
            }
            stmp = $('#iPlanBeginTime').datetimebox('getValue');
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：计划开始时间不能为空！');
               return false;
            }
            stmp = $('#iPlanEndTime').datetimebox('getValue');
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：计划结束时间不能为空！');
               return false;
            }
            stmp = $('#iActBeginTime').datetimebox('getValue');
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：实际开始时间不能为空！');
               return false;
            }
            stmp = $('#iActEndTime').datetimebox('getValue');
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：实际结束时间不能为空！');
               return false;
            }
            stmp = $('input[name="iTaskStatus"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：任务状态不能为空！');
               return false;
            }
            stmp = $('input[name="iLockStatus"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：锁定状态不能为空！');
               return false;
            }
            stmp = $('input[name="iINFStatus"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：接口状态不能为空！');
               return false;
            }
            stmp = $('input[name="iWMSStatus"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：投料状态不能为空！');
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
                PlanDate:$('#iPlanDate').datetimebox('getValue'),
                PlanNo:$('input[name="iPlanNo"]').val(),
                BatchID:$('input[name="iBatchID"]').val(),
                PlanSeq:$('input[name="iPlanSeq"]').val(),
                PUID:$('#iPUID').find("option:selected").val(),
                PlanType:$('input[name="iPlanType"]').val(),
                BrandCode:$('#iBrandName').find("option:selected").val(),
                BrandName:$('#iBrandName').find("option:selected").html(),
                ERPOrderNo:$('input[name="iERPOrderNo"]').val(),
                PlanQuantity:$('input[name="iPlanQuantity"]').val(),
                ActQuantity:$('input[name="iActQuantity"]').val(),
                Unit:$('#iUnit').find("option:selected").val(),
                PlanBeginTime:$('#iPlanBeginTime').datetimebox('getValue'),
                PlanEndTime:$('#iPlanEndTime').datetimebox('getValue'),
                ActBeginTime:$('#iActBeginTime').datetimebox('getValue'),
                ActEndTime:$('#iActEndTime').datetimebox('getValue'),
                TaskStatus:$('input[name="iTaskStatus"]').val(),
                LockStatus:$('input[name="iLockStatus"]').val(),
                INFStatus:$('input[name="iINFStatus"]').val(),
                WMSStatus:$('input[name="iWMSStatus"]').val()
            };
             $.ajax({
                url:"/ZYPlanGuid/isBatchNumber",
                data:{ABatchID:$("#iBatchID").val()},
                type:"get",
                success:function(res){
                    console.log(typeof res)
                    if(res == '"NO"'){
                        alert('Warning：批次号重复！');
                        return false
                    }else if(res == '"OK"'){
                        $.ajax({
                            url: urlAddr,
                            //url: '/allZYPlans/Create',
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
                                    $(tableId).datagrid('reload',{ url: "/allZYPlans/Find?_t=" + new Date().getTime() });
                                    //$(tableid).datagrid('clearSelections');
                                } else {
                                    $.messager.alert(obj1[0].status + '失败！', '未知错误导致失败，请重试！', 'warning');
                                }
                            }
                        });
                    }
                },
                error:function(){
                    alert("请求错误，请刷新后重试！")
                }
            })

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
                field: 'PlanNo',
                title: '计划单号',
                align: 'center',
                width: 200
            },
            {
                field: 'BatchID',
                title: '批次号',
                align: 'center',
                width: 200
            },
            {
                field: 'PlanType',
                title: '计划类型',
                align: 'center',
                width: 150
            },
            {
                field: 'BrandName',
                title: '品牌名称',
                align: 'center',
                width: 200
            },
            {
                field: 'ERPOrderNo',
                title: 'ERP订单号',
                align: 'center',
                width: 200
            },
            {
                field: 'PlanQuantity',
                title: '计划数量',
                align: 'center',
                width: 100
            },
            {
                field: 'ActQuantity',
                title: '实际数量',
                align: 'center',
                width: 100
            },
            {
                field: 'TaskStatus',
                title: '任务状态',
                align: 'center',
                width: 100
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
