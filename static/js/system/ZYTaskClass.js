/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_ZYTask.json';
    var urlPrefix = '/allZYTasks/';
    var idPrefix = 'ZYTaskClass';
    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";
    var titleText = "任务信息";

    function createKeyIDObj(keyID){
        return {
            ID:keyID
        }
    }
    

     $('input[name="iZYTaskName"]').change(function () {
         var sZYTaskName = $('input[name="iZYTaskName"]').val();
        if(Bee.StringUtils.isNotEmpty(sZYTaskName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iZYTaskCode"]').change(function () {
        //  var sZYTaskCode = $('input[name="iZYTaskCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sZYTaskCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iZYTaskSeq"]').change(function () {
        //  var sZYTaskSeq = $('input[name="iZYTaskSeq"]').val();
        // if(Bee.StringUtils.isInteger(sZYTaskSeq)){
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
                field: 'PlanDate',
                title: '生产日期',
                align: 'center',
                width: 100
            },
            {
                field: 'TaskID',
                title: '任务ID',
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
                field: 'PlanSeq',
                title: '顺序号',
                align: 'center',
                width: 100
            },
            {
                field: 'PUID',
                title: '工艺段编号',
                align: 'center',
                width: 100
            },
            {
                field: 'PlanType',
                title: '计划类型',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandID',
                title: '品牌ID',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandName',
                title: '品牌名称',
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
                field: 'ActQuantity',
                title: '实际重量',
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
                field: 'EnterTime',
                title: '录入时间',
                align: 'center',
                width: 100
            },
            {
                field: 'ActBeginTime',
                title: '实际开始时间',
                align: 'center',
                width: 100
            },
            {
                field: 'ActEndTime',
                title: '实际结束时间',
                align: 'center',
                width: 100
            },
            {
                field: 'SetRepeatCount',
                title: '设定重复次数',
                align: 'center',
                width: 100
            },
            {
                field: 'CurretnRepeatCount',
                title: '当前重复次数',
                align: 'center',
                width: 100
            },
            {
                field: 'ActTank',
                title: '实际罐号',
                align: 'center',
                width: 100
            },
            {
                field: 'TaskStatus',
                title: '任务状态',
                align: 'center',
                width: 100,
                formatter: function(value,row,index){
                    if (value == 10){
                        return '新增'
                    }else if(value == 20){
                        return '已下发'
                    }else if(value == 31){
                        return '中控已确认'
                    }else if(value == 32){
                        return '中控已复核'
                    }else if(value == 33){
                        return 'QA已复核'
                    }else if(value == 40){
                        return '已确认，准备生产'
                    }else if(value == 50){
                        return '执行'
                    }else if(value == 60){
                        return '已完成'
                    }else if(value == 70){
                        return '取消'
                    }else if(value == 80){
                        return '暂停'
                    }else if(value == 85){
                        return '故障'
                    }else if(value == 90){
                        return '中止'
                    }
                }
            },
            {
                field: 'LockStatus',
                title: '锁定状态',
                align: 'center',
                width: 100,
                formatter: function(value,row,index){
                    if (value == 0){
                        return "解锁"
                    }else if(value == 10){
                        return "锁定"
                    }
                }
            }
        ]]
    });


    ZYTaskClassToolbar = {
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
                url: '/allZYTasks/Search',
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
            $('input[name="iID"]').val("");
            $('#iPlanDate').datetimebox({value: ""});;
            $('input[name="iTaskID"]').val("");
            $('#iBatchID option:contains("请选择")').prop("selected", 'selected');
            $('input[name="iPlanSeq"]').val("");
            $('#iPUID option:contains("请选择")').prop("selected", 'selected');
            $('input[name="iPlanType"]').val("");
            $('#iBrandName option:contains("请选择")').prop("selected", 'selected');
            $('input[name="iPlanQuantity"]').val("");
            $('input[name="iActQuantity"]').val("");
            $('#iUnit option:contains("请选择")').prop("selected", 'selected');
            $('#iActBeginTime').datetimebox({value: ""});
            $('#iActEndTime').datetimebox({value: ""});
            $('input[name="iSetRepeatCount"]').val("");
            $('input[name="iCurretnRepeatCount"]').val("");
            $('input[name="iActTank"]').val("");
            $('input[name="iTaskStatus"]').val("");
            $('input[name="iLockStatus"]').val("");
            // $('input[name="iZYTaskSeq"]').onChange()
            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#ZYTaskClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#ZYTaskClassCombobox').combobox('showPanel');
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
                    $('input[name="iTaskID"]').val(row.TaskID);
                    $('#iBatchID option:contains('+row.BatchID+')').prop("selected", 'selected');
                    $('input[name="iPlanSeq"]').val(row.PlanSeq);
                    $('#iPUID option:contains('+row.PUID+')').prop("selected", 'selected');
                    $('input[name="iPlanType"]').val(row.PlanType);
                    $('#iBrandName option:contains('+row.BrandName+')').prop("selected", 'selected');
                    $('input[name="iPlanQuantity"]').val(row.PlanQuantity);
                    $('input[name="iActQuantity"]').val(row.ActQuantity);
                    $('#iUnit option:contains('+row.Unit+')').prop("selected", 'selected');
                    $('#iActBeginTime').datetimebox("setValue",row.ActBeginTime);
                    $('#iActEndTime').datetimebox("setValue",row.ActEndTime);
                    $('input[name="iSetRepeatCount"]').val(row.SetRepeatCount);
                    $('input[name="iCurretnRepeatCount"]').val(row.CurretnRepeatCount);
                    $('input[name="iActTank"]').val(row.ActTank);
                    $('input[name="iTaskStatus"]').val(row.TaskStatus);
                    $('input[name="iLockStatus"]').val(row.LockStatus);
                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象
                    // $('#ZYTaskClassCombobox').combobox('setValue',row['ZYTaskClass'].id);
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
                            url: '/allZYTasks/Delete',
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
             var stmp = $('#iPlanDate').datetimebox('getValue');
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：生产日期不能为空！');
               return false;
            }
            stmp = $('input[name="iTaskID"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iTaskID"]').val("");
                alert('Warning：任务ID输入错误,请输入数字！');
                return false;
            }
            stmp = $('#iBatchID').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：批次号不能为空！');
               return false;
            }
            stmp = $('input[name="iPlanSeq"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPlanSeq"]').val("");
                alert('Warning：顺序号输入错误,请输入数字！');
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
            stmp = $('#iBrandName').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：品牌名称不能为空！');
               return false;
            }
            stmp = $('input[name="iPlanQuantity"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPlanQuantity"]').val("");
                alert('Warning：计划重量输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iActQuantity"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iActQuantity"]').val("");
                alert('Warning：实际重量输入错误,请输入数字！');
                return false;
            }
            stmp = $('#iUnit').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：单位不能为空！');
               return false;
            }
            stmp = $('input[name="iActTank"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：实际罐号不能为空！');
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
            stmp = $('input[name="iSetRepeatCount"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iSetRepeatCount"]').val("");
                alert('Warning：设定重复次数输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iCurretnRepeatCount"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iCurretnRepeatCount"]').val("");
                alert('Warning：当前重复次数输入错误,请输入数字！');
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
                    TaskID:$('input[name="iTaskID"]').val(),
                    BatchID:$('#iBatchID').find("option:selected").val(),
                    PlanSeq:$('input[name="iPlanSeq"]').val(),
                    PUID:$('#iPUID').find("option:selected").val(),
                    PlanType:$('input[name="iPlanType"]').val(),
                    BrandID:$('#iBrandName').find("option:selected").val(),
                    BrandName:$('#iBrandName').find("option:selected").html(),
                    PlanQuantity:$('input[name="iPlanQuantity"]').val(),
                    ActQuantity:$('input[name="iActQuantity"]').val(),
                    Unit:$('#iUnit').find("option:selected").val(),
                    //EnterTime:$('input[name="iEnterTime"]').val(),
                    ActBeginTime:$('#iActBeginTime').datetimebox('getValue'),
                    ActEndTime:$('#iActEndTime').datetimebox('getValue'),
                    SetRepeatCount:$('input[name="iSetRepeatCount"]').val(),
                    CurretnRepeatCount:$('input[name="iCurretnRepeatCount"]').val(),
                    ActTank:$('input[name="iActTank"]').val(),
                    TaskStatus:$('input[name="iTaskStatus"]').val(),
                    LockStatus:$('input[name="iLockStatus"]').val()
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allZYTasks/Create',
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
                            $(tableId).datagrid('reload',{ url: "/allZYTasks/Find?_t=" + new Date().getTime() });
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
                field: 'PlanDate',
                title: '生产日期',
                align: 'center',
                width: 100
            },
            {
                field: 'TaskID',
                title: '任务ID',
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
                field: 'PlanSeq',
                title: '顺序号',
                align: 'center',
                width: 100
            },
            {
                field: 'PUID',
                title: '工艺段编号',
                align: 'center',
                width: 100
            },
            {
                field: 'PlanType',
                title: '计划类型',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandID',
                title: '品牌ID',
                align: 'center',
                width: 100
            },
            {
                field: 'BrandName',
                title: '品牌名称',
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
                field: 'ActQuantity',
                title: '实际重量',
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
                field: 'EnterTime',
                title: '录入时间',
                align: 'center',
                width: 100
            },
            {
                field: 'ActBeginTime',
                title: '实际开始时间',
                align: 'center',
                width: 100
            },
            {
                field: 'ActEndTime',
                title: '实际结束时间',
                align: 'center',
                width: 100
            },
            {
                field: 'SetRepeatCount',
                title: '设定重复次数',
                align: 'center',
                width: 100
            },
            {
                field: 'CurretnRepeatCount',
                title: '当前重复次数',
                align: 'center',
                width: 100
            },
            {
                field: 'ActTank',
                title: '实际罐号',
                align: 'center',
                width: 100
            },
            {
                field: 'TaskStatus',
                title: '任务状态',
                align: 'center',
                width: 100,
                formatter: function(value,row,index){
                    if (value == 10){
                        return "编制"
                    }else if(value == 20){
                        return "下达"
                    }else if(value == 30){
                        return "新增"
                    }else if(value == 40){
                        return "确认"
                    }else if(value == 50){
                        return "执行"
                    }else if(value == 60){
                        return "完成"
                    }else if(value == 70){
                        return "取消"
                    }else if(value == 80){
                        return "暂停"
                    }else if(value == 85){
                        return "故障"
                    }else if(value == 90){
                        return "中止"
                    }
                }
            },
            {
                field: 'LockStatus',
                title: '锁定状态',
                align: 'center',
                width: 100,
                formatter: function(value,row,index){
                    if (value == 0){
                        return "解锁"
                    }else if(value == 10){
                        return "锁定"
                    }
                }
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
