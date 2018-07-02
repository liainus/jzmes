/**
 * Created by ericlee on 2017/7/27.
 */

$(function () {

    var urlPrefix = 'productionPlan/';
    var idPrefix = 'ProductionPlan';
    var titleText = "生产计划";

    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#"+ idPrefix + "Toolbar";
    var dialogId = "#"+ idPrefix + "Dialog";
    var formId = "#"+ idPrefix + "Form";
    var formTitleId = "#"+ idPrefix + "FormTitle";

    $(tableId).datagrid({
        url: urlPrefix + 'findAll',
        idField: 'id',
        treeField: 'text',
        fit: true,
        fitColumns: true,
        striped: true,
        rownumbers: true,
        border: false,
        pagination: true,
        singleSelect:true,
        pageSize: 5,
        pageList: [5, 10, 15, 20],
        pageNumber: 1,
        toolbar: toolbarId,
        columns: [[
            {
                field: 'ck',
                width: 100,
                checkbox: true
            },
            {
                field: 'id',
                title: 'ID',
                align: 'center',
                width: 100
            },
            {
                field: 'planCode',
                title: '计划单号',
                width: 100
            },
            {
                field: 'text',
                title: '描述',
                width: 100
            },
            {
                field: 'startTime',
                title: '开始时间',
                formatter: Common.DateTimeFormatter,
                width: 100
            },
            {
                field: 'endTime',
                title: '结束时间',
                formatter: Common.DateTimeFormatter,
                width: 100
            }
        ]],
        onLoadSuccess: function (data) {
            if (data.rows.length === 0) {
                var body = $(this).data().datagrid.dc.body2;
                body.find('table tbody').append('<tr><td width="' + body.width() + '" style="height: 25px; text-align: center;" colspan="6">没有数据</td></tr>');
            }
            else {
                $(tableId).datagrid("selectRow", 0);
            }
        },
        onSelect: function (index, row) {
            console.log(row);
            if(row){
                $('#ProductionRequestTable').datagrid('load',{productionPlanId : row.id})
            }
        }
    });

    ProductionPlanToolbar = {
        url: "",
        message : "",
        search: function () {
            $(tableId).datagrid('load', {
                text: $.trim($('input[name="search"]').val())
            });
        },
        create: function () {
            $(dialogId).dialog('open').dialog('setTitle', '新增' + titleText);
            $(formTitleId).text(titleText);
            $('input[name="text"]').focus();
            $(formId).form('clear');
            url = urlPrefix + 'create';
            message = '新增'  + titleText;
        },
        update : function () {
            var rows = $(tableId).datagrid('getSelections');
            if (rows.length > 1) {
                $.messager.alert('警告操作！', '编辑记录只能选定一条数据！', 'warning');
            } else if (rows.length == 1) {
                var row = $(tableId).datagrid('getSelected');
                if (row) {
                    $(dialogId).dialog('open').dialog('setTitle', '编辑' + titleText);
                    $(formTitleId).text(titleText);
                    //$(formId).form('load', row);
                    //$('input[name="text"]').focus();
                    $(formId + ' input[name="id"]').val(row.id);
                    $(formId + ' input[name="planCode"]').val(row.planCode);
                    $(formId + ' input[name="text"]').val(row.text);
                    $('#startTime').datetimebox('setValue',Common.DateTimeFormatter(row.startTime));
                    $('#endTime').datetimebox('setValue',Common.DateTimeFormatter(row.endTime));
                    url = urlPrefix + 'update';
                    message = '编辑' + titleText;
                }
            } else if (rows.length == 0) {
                $.messager.alert('警告操作！', '请至少选定一条数据进行编辑！', 'warning');
            }
        },
        delete : function () {
            var rows = $(tableId).datagrid('getSelections');
            if (rows.length > 0) {
                $.messager.confirm('确定操作', '您正在删除所选的记录吗？', function (flag) {
                    if (flag) {
                        var ids = [];
                        for (var i = 0; i < rows.length; i ++) {
                            ids.push(parseInt(rows[i].id));
                        }
                        $.ajax({
                            url : urlPrefix + 'delete',
                            method : 'POST',
                            traditional: true,
                            data : {ids:ids},
                            beforeSend : function () {
                                $.messager.progress({
                                    text : '正在删除中...'
                                });
                            },
                            success : function (data) {
                                $.messager.progress('close');

                                if (data) {
                                    $(tableId).datagrid('loaded');
                                    $(tableId).datagrid('load');
                                    $(tableId).datagrid('unselectAll');
                                    $.messager.show({
                                        title : '提示',
                                        msg :  '删除' + titleText + '成功',
                                        style:{
                                            right:'',
                                            top:document.body.scrollTop+document.documentElement.scrollTop,
                                            bottom:''
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
        save : function () {
            if ($(formId).form('validate')) {

                var entity = {
                    id : $(formId + ' input[name="id"]').val(),
                    planCode : $(formId + ' input[name="planCode"]').val(),
                    text : $(formId + ' input[name="text"]').val(),
                    startTime : $('#startTime').datetimebox('getValue'),
                    endTime : $('#endTime').datetimebox('getValue')
                };
                $.ajax({
                    url : url,
                    method : 'POST',
                    traditional: true,
                    data : entity,
                    beforeSend : function () {
                        $.messager.progress({
                            text : '正在'+ message + '中...'
                        });
                    },
                    success : function (data, response, status) {
                        $.messager.progress('close');

                        if (data > 0) {
                            $.messager.show({
                                title : '提示',
                                msg :  message + '成功',
                                style:{
                                    right:'',
                                    top:document.body.scrollTop+document.documentElement.scrollTop,
                                    bottom:''
                                }
                            });
                            $(formId).form('reset');
                            $(dialogId).dialog('close');
                            $(tableId).datagrid('reload');
                        } else {
                            $.messager.alert(message + '失败！', '未知错误导致失败，请重试！', 'warning');
                        }
                    }
                });
            }
        },
        refresh : function() {
            $(tableId).datagrid('reload');
        }
    }

});
