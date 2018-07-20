/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_ProductParameter.json';
    var urlPrefix = '/allProductParameters/';
    var idPrefix = 'ProductParameterClass';
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
    

     $('input[name="iProductParameterName"]').change(function () {
         var sProductParameterName = $('input[name="iProductParameterName"]').val();
        if(Bee.StringUtils.isNotEmpty(sProductParameterName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iProductParameterCode"]').change(function () {
        //  var sProductParameterCode = $('input[name="iProductParameterCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sProductParameterCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iProductParameterSeq"]').change(function () {
        //  var sProductParameterSeq = $('input[name="iProductParameterSeq"]').val();
        // if(Bee.StringUtils.isInteger(sProductParameterSeq)){
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
                field: 'PDParaCode',
                title: '工艺参数编码',
                align: 'center',
                width: 100
            },
            {
                field: 'PDParaName',
                title: '工艺参数名称',
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
                field: 'Value',
                title: '参数值',
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


    ProductParameterClassToolbar = {
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
                url: '/allProductParameters/Search',
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
            $('input[name="iPDParaCode"]').val();
            $('input[name="iPDParaName"]').val();
            $('input[name="iDesc"]').val();
            $('input[name="iValue"]').val();
            $('input[name="iUnit"]').val();
            // $('input[name="iProductRuleID"]').val();
            // $('input[name="iPUID"]').val();
            $('#iProductRuleID option[value=""]').prop("selected", 'selected');//ID默认空
            $('#iPUID option[value=""]').prop("selected", 'selected');//ID默认空
            $('input[name="iSeq"]').val();        // $('input[name="iProductParameterSeq"]').onChange()
            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#ProductParameterClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#ProductParameterClassCombobox').combobox('showPanel');
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
                    $('input[name="iPDParaCode"]').val(row.PDParaCode);
                    $('input[name="iPDParaName"]').val(row.PDParaName);
                    $('input[name="iDesc"]').val(row.Desc);
                    $('input[name="iValue"]').val(row.Value);
                    $('input[name="iUnit"]').val(row.Unit);
                    // $('input[name="iProductRuleID"]').val(row.ProductRuleID);
                    // $('input[name="iPUID"]').val(row.PUID);
                    $('#iProductRuleID option:contains('+row.ProductRuleID+')').prop("selected", 'selected');//区域ID赋值
                    $('#iPUID option:contains('+row.PUID+')').prop("selected", 'selected');//区域ID赋值
                    $('input[name="iSeq"]').val(row.Seq);
                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象  
                    if (row.IsEnable == '禁用') {

                        $("[switchbuttonName='IsEnable']").switchbutton("uncheck");
                    }else {
                        $("[switchbuttonName='IsEnable']").switchbutton("check");
                    }
                    $('input[name="iProductParameterName"]').focus();
                    // $('#ProductParameterClassCombobox').combobox('setValue',row['ProductParameterClass'].id);
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
                            url: '/allProductParameters/Delete',
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
            var stmp = $('input[name="iPDParaCode"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺参数编码不能为空！');
               return false;
            }
            stmp = $('input[name="iPDParaName"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺参数名称不能为空！');
               return false;
            }
             stmp = $('#iProductRuleID').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：产品定义ID不能为空！');
               return false;
            }
            stmp = $('#iPUID').find("option:selected").val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：工艺段ID不能为空！');
               return false;
            }
            stmp = $('input[name="iValue"]').val();
            if(Bee.StringUtils.isDecimal(stmp)) {

            }else{
                $('input[name="iLowLimit"]').val("")
                alert('Warning：参数值输入错误！');
                return false;
            }
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
                    PDParaCode:$('input[name="iPDParaCode"]').val(),
                    PDParaName:$('input[name="iPDParaName"]').val(),
                    Desc:$('input[name="iDesc"]').val(),
                    Value:$('input[name="iValue"]').val(),
                    Unit:$('input[name="iUnit"]').val(),
                    ProductRuleID:$('#iProductRuleID').find("option:selected").val(),
                    PUID:$('#iPUID').find("option:selected").val(),
                    Seq:$('input[name="iSeq"]').val()
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allProductParameters/Create',
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
                            $(tableId).datagrid('reload',{ url: "/allProductParameters/Find?_t=" + new Date().getTime() });
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
                field: 'ID',
                title: 'ID',
                align: 'center',
                width: 100
            },
            {
                field: 'PDParaCode',
                title: '工艺参数编码',
                align: 'center',
                width: 100
            },
            {
                field: 'PDParaName',
                title: '工艺参数名称',
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
                field: 'Value',
                title: '参数值',
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
