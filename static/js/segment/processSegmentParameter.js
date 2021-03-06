/**
 * Created by ericlee on 2017/7/27.
 */
$(function () {

    var urlPrefix = '/segment/processSegmentParameter/';
    var idPrefix = 'ProcessSegmentParameter';
    var titleText = "过程段参数";

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
        singleSelect:false,
        pageSize: 20,
        pageList: [10, 20, 30, 40, 50],
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
                field: 'text',
                title: '名称',
                width: 100
            },
            {
                field: 'value',
                title: '值',
                width: 100
            },
            {
                field: 'unit',
                title: '单位',
                width: 100
            },
            {
                field: 'processSegment',
                title: '过程段',
                width: 100,
                formatter: function (val, row) {
                    return val.text;
                }
            }
        ]]
    });

    ProcessSegmentParameterToolbar = {
        url: "",
        message : "",
        search: function () {
            $(tableId).datagrid('load', {
                text: $.trim($('input[name="search"]').val())
            });
        },
        create: function () {

            var row = $('#ProcessSegmentTable').datagrid('getSelected');
            if (row) {
                $(dialogId).dialog('open').dialog('setTitle', '新增' + titleText);
                $(formTitleId).text(titleText);
                $('input[name="text"]').focus();
                $(formId).form('clear');
                $(formId + ' input[name="processSegment"]').val(row.id);
                this.url = urlPrefix + 'create';
                message = '新增' + titleText;
            } else {
                $.messager.alert('警告！', '没有选择过程段，无法添加！', 'warning');
            }

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
                    $(formId).form('load', row);
                    $('input[name="text"]').focus();
                    $(formId + ' input[name="processSegment"]').val(row.processSegment.id);
                    this.url = urlPrefix + 'update';
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
                    text : $(formId + ' input[name="text"]').val(),
                    value : $(formId + ' input[name="value"]').val(),
                    unit : $(formId + ' input[name="unit"]').val(),
                    'processSegment.id' : $(formId + ' input[name="processSegment"]').val()
                };
                $.ajax({
                    url : this.url,
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
        refresh : function () {
            $(tableId).datagrid('reload');
        }
    }

});
