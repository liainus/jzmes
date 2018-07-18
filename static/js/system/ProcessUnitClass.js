/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_ProcessUnit.json';
    var urlPrefix = '/allProcessUnits/';
    var idPrefix = 'ProcessUnitClass';
    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";
    var titleText = "组织";

    function createKeyIDObj(keyID){
    return {
        ID:keyID
    }}
    

     $('input[name="iProcessUnitName"]').change(function () {
         var sProcessUnitName = $('input[name="iProcessUnitName"]').val();
        if(Bee.StringUtils.isNotEmpty(sProcessUnitName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iProcessUnitCode"]').change(function () {
        //  var sProcessUnitCode = $('input[name="iProcessUnitCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sProcessUnitCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iProcessUnitSeq"]').change(function () {
        //  var sProcessUnitSeq = $('input[name="iProcessUnitSeq"]').val();
        // if(Bee.StringUtils.isInteger(sProcessUnitSeq)){
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
                field: 'PUCode',
                title: '工艺段编码',
                align: 'center',
                width: 150
            },
            {
                field: 'PUName',
                title: '工艺段名称',
                align: 'center',
                width: 150
            },
             {
                field: 'PLineID',
                title: '生产线ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PURateCapacity',
                title: '额定能力',
                align: 'center',
                width: 150
            },
            {
                field: 'PUPLanCapacity',
                title: '计划能力',
                align: 'center',
                width: 150
            },
            {
                field: 'CapacityUnit',
                title: '能力单位',
                align: 'center',
                width: 100
            },
            {
                field: 'Seq',
                title: '顺序',
                width: 100,
                // type: validatebox,
                // options:{required:true},
                editor:{type:'validatebox',options:{required: true }},
                align: 'center'
            },
            {
                field: 'Desc',
                title: '说明',
                width: 300,
                align: 'center'
            },
            {
                field: 'PlaceTime',
                title: '静置时间',
                align: 'center',
                width: 150
            },
            {
                field: 'TimeUnit',
                title: '时间单位',
                width: 100,
                align: 'center'
            },
            {
                field: 'BatchRunTime',
                title: '批运行时间',
                width: 150,
                align: 'center'
            }
        ]]
    });


    ProcessUnitClassToolbar = {
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
                url: '/allProcessUnits/Search',
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
            $('input[name="iPUCode"]').val("");
            $('input[name="iPUName"]').val("");
            $('input[name="iPLineID"]').val("");
            $('#iPLineID option[value=""]').prop("selected", 'selected');//ID默认空
            $('input[name="iPURateCapacity"]').val("");
            $('input[name="iPUPLanCapacity"]').val("");
            $('input[name="iCapacityUnit"]').val("");
            $('input[name="iSeq"]').val("");
            // $('input[name="iProcessUnitSeq"]').onChange()
            $('input[name="iDesc"]').val("");
            $('input[name="iPlaceTime"]').val("");
            $('input[name="iTimeUnit"]').val("");
            $('input[name="iBatchRunTime"]').val("");

            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#ProcessUnitClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#ProcessUnitClassCombobox').combobox('showPanel');
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
                    $('input[name="iPUCode"]').val(row.PUCode);
                    $('input[name="iPUName"]').val(row.PUName);
                    $('#iPLineID option:contains('+row.ID+')').prop("selected", 'selected');//ID赋值
                    $('input[name="iPURateCapacity"]').val(row.PURateCapacity);
                    $('input[name="iPUPLanCapacity"]').val(row.PUPLanCapacity);
                    $('input[name="iCapacityUnit"]').val(row.CapacityUnit);
                    $('input[name="iSeq"]').val(row.Seq);
                    $('input[name="iDesc"]').val(row.Desc);
                    $('input[name="iPlaceTime"]').val(row.PlaceTime);
                    $('input[name="iTimeUnit"]').val(row.TimeUnit);
                    $('input[name="iBatchRunTime"]').val(row.BatchRunTime);

                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象  
                    if (row.IsEnable == '禁用') {

                        $("[switchbuttonName='IsEnable']").switchbutton("uncheck");
                    }else {
                        $("[switchbuttonName='IsEnable']").switchbutton("check");
                    }
                    $('input[name="iProcessUnitName"]').focus();
                    // $('#ProcessUnitClassCombobox').combobox('setValue',row['ProcessUnitClass'].id);
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
                            url: '/allProcessUnits/Delete',
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
            var stmp = $('input[name="iPUCode"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺段编码不能为空！');
               return false;
            }
            stmp = $('input[name="iPUName"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺段名称不能为空！');
               return false;
            }
            stmp = $('#iPLineID').find("option:selected").val()
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：生产线ID不能为空！');
               return false;
            }
            stmp = $('input[name="iSeq"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iSeq"]').val("");
                alert('Warning：顺序输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iPURateCapacity"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPURateCapacity"]').val("");
                alert('Warning：额定能力输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iPUPLanCapacity"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPUPLanCapacity"]').val("");
                alert('Warning：计划能力输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iPlaceTime"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iPlaceTime"]').val("");
                alert('Warning：静置时间输入错误,请输入数字！');
                return false;
            }
            stmp = $('input[name="iBatchRunTime"]').val();
            if(Bee.StringUtils.isInteger(stmp)) {
            //
            }else{
                $('input[name="iBatchRunTime"]').val("");
                alert('Warning：批运行时间输入错误,请输入数字！');
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
                    PUCode:$('input[name="iPUCode"]').val(),
                    PUName:$('input[name="iPUName"]').val(),
                    PLineID:$('#iPLineID').find("option:selected").html(),
                    PURateCapacity:$('input[name="iPURateCapacity"]').val(),
                    PUPLanCapacity:$('input[name="iPUPLanCapacity"]').val(),
                    CapacityUnit:$('input[name="iCapacityUnit"]').val(),
                    Seq:$('input[name="iSeq"]').val(),
                    Desc:$('input[name="iDesc"]').val(),
                    PlaceTime:$('input[name="iPlaceTime"]').val(),
                    TimeUnit:$('input[name="iTimeUnit"]').val(),
                    BatchRunTime:$('input[name="iBatchRunTime"]').val()
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allProcessUnits/Create',
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
                            $(tableId).datagrid('reload',{ url: "/allProcessUnits/Find?_t=" + new Date().getTime() });
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
                field: 'PUCode',
                title: '工艺段编码',
                align: 'center',
                width: 150
            },
            {
                field: 'PUName',
                title: '工艺段名称',
                align: 'center',
                width: 150
            },
             {
                field: 'PLineID',
                title: '生产线ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PURateCapacity',
                title: '额定能力',
                align: 'center',
                width: 150
            },
            {
                field: 'PUPLanCapacity',
                title: '计划能力',
                align: 'center',
                width: 150
            },
            {
                field: 'CapacityUnit',
                title: '能力单位',
                align: 'center',
                width: 100
            },
            {
                field: 'Seq',
                title: '顺序',
                width: 100,
                // type: validatebox,
                // options:{required:true},
                editor:{type:'validatebox',options:{required: true }},
                align: 'center'
            },
            {
                field: 'Desc',
                title: '说明',
                width: 300,
                align: 'center'
            },
            {
                field: 'PlaceTime',
                title: '静置时间',
                align: 'center',
                width: 150
            },
            {
                field: 'TimeUnit',
                title: '时间单位',
                width: 100,
                align: 'center'
            },
            {
                field: 'BatchRunTime',
                title: '批运行时间',
                width: 150,
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
