/**
 * Created by Xujin on 2018/1/8.
 */
$(function () {

    // var urlPrefix = 'data/datagrid_ProductRule.json';
    var urlPrefix = '/allProductRules/';
    var idPrefix = 'ProductRuleClass';
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
    

     $('input[name="iProductRuleName"]').change(function () {
         var sProductRuleName = $('input[name="iProductRuleName"]').val();
        if(Bee.StringUtils.isNotEmpty(sProductRuleName)){
            //alert('角色名称不能为空！');
            //return false;
        }else{
            alert('角色名称不能为空！:');
           return true;
        }

        // $('input[name="iProductRuleCode"]').change(function () {
        //  var sProductRuleCode = $('input[name="iProductRuleCode"]').val();
        // if(Bee.StringUtils.isNotEmpty(sProductRuleCode)){
        //     //alert('角色名称不能为空！');
        //     //return false;
        // }else{
        //     alert('角色名称不能为空！:');
        //    return true;
        // }})
        //
        // $('input[name="iProductRuleSeq"]').change(function () {
        //  var sProductRuleSeq = $('input[name="iProductRuleSeq"]').val();
        // if(Bee.StringUtils.isInteger(sProductRuleSeq)){
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
                field: 'PRCode',
                title: '产品定义编码',
                align: 'center',
                width: 150
            },
            {
                field: 'PRName',
                title: '产品名称',
                align: 'center',
                width: 150
            },
             {
                field: 'Version',
                title: '版本号',
                align: 'center',
                width: 100
            },
            {
                field: 'Desc',
                title: '说明',
                align: 'center',
                width: 300
            },
            {
                field: 'Publish_date',
                title: '发行日期',
                align: 'center',
                width: 220
            },
            {
                field: 'Appy_date',
                title: '使用日期',
                width: 220,
                // type: validatebox,
                // options:{required:true},
                align: 'center'
            },
            {
                field: 'IsUsed',
                title: '是否使用',
                width: 100,
                align: 'center'
            }
        ]]
    });


    ProductRuleClassToolbar = {
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
                url: '/allProductRules/Search',
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
            $('input[name="iPRCode"]').val("");
            $('input[name="iPRName"]').val("");
            $('input[name="iVersion"]').val("");
            $('input[name="iDesc"]').val("");
            $('input[name="iPublish_date"]').val("");
            $('input[name="iAppy_date"]').val("");
            $('input[name="iIsUsed"]').val("");

            // $(formId).form('clear');
            message = '新增' + titleText;
            // $('#ProductRuleClassCombobox').combobox('textbox').bind('focus', function () {
            //     $('#ProductRuleClassCombobox').combobox('showPanel');
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
                    $('input[name="iPRCode"]').val(row.PRCode);
                    $('input[name="iPRName"]').val(row.PRName);
                    $('input[name="iVersion"]').val(row.Version);
                    $('input[name="iDesc"]').val(row.Desc);
                    $('input[name="iPublish_date"]').val(row.Publish_date);
                    $('input[name="iAppy_date"]').val(row.Appy_date);
                    $('input[name="iIsUsed"]').val(row.IsUsed);

                    //var thisSwitchbuttonObj = $(".switchstatus").find("[switchbuttonName='IsEnable']");//获取switchbutton对象  
                    if (row.IsEnable == '禁用') {

                        $("[switchbuttonName='IsEnable']").switchbutton("uncheck");
                    }else {
                        $("[switchbuttonName='IsEnable']").switchbutton("check");
                    }
                    $('input[name="iProductRuleName"]').focus();
                    // $('#ProductRuleClassCombobox').combobox('setValue',row['ProductRuleClass'].id);
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
                            url: '/allProductRules/Delete',
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
            var stmp = $('input[name="iPRCode"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：组织机构编号不能为空！');
               return false;
            }
            stmp = $('input[name="iPRName"]').val();
            if(Bee.StringUtils.isEmpty(stmp)) {
               alert('Warning：组织机构名称不能为空！');
               return false;
            }
            // stmp = $('input[name="iSeq"]').val();
            // if(Bee.StringUtils.isInteger(stmp)) {
            //
            // }else{
            //     $('input[name="iSeq"]').val("");
            //     // alert('Warning：组织机构顺序输入错误,请输入数字！');
            //     return false;
            // }
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
                    PRCode:$('input[name="iPRCode"]').val(),
                    PRName:$('input[name="iPRName"]').val(),
                    Version:$('input[name="iVersion"]').val(),
                    Desc:$('input[name="iDesc"]').val(),
                    Publish_date:$('#iPublish_date').datebox('getValue'),
                    Appy_date:$('#iAppy_date').datebox('getValue'),
                    IsUsed:$('input[name="iIsUsed"]').val()
                };
                $.ajax({
                    url: urlAddr,
                    //url: '/allProductRules/Create',
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
                            $(tableId).datagrid('reload',{ url: "/allProductRules/Find?_t=" + new Date().getTime() });
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
                field: 'PRCode',
                title: '产品定义编码',
                align: 'center',
                width: 150
            },
            {
                field: 'PRName',
                title: '产品名称',
                align: 'center',
                width: 150
            },
             {
                field: 'Version',
                title: '版本号',
                align: 'center',
                width: 100
            },
            {
                field: 'Desc',
                title: '说明',
                align: 'center',
                width: 300
            },
            {
                field: 'Publish_date',
                title: '发行日期',
                align: 'center',
                width: 220
            },
            {
                field: 'Appy_date',
                title: '使用日期',
                width: 220,
                // type: validatebox,
                // options:{required:true},
                align: 'center'
            },
            {
                field: 'IsUsed',
                title: '是否使用',
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
