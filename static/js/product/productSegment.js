/**
 * Created by ericlee on 2017/7/27.
 */
$(function () {

    var urlPrefix = '/product/productSegment/';
    var idPrefix = 'ProductSegment';
    var titleText = "产品段";

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
                width: 30,
                checkbox: true
            },
            {
                field: 'id',
                title: 'ID',
                align: 'center',
                width: 50
            },
            {
                field: 'text',
                title: '名称',
                width: 100
            },
            {
                field: 'duration',
                title: '持续时间',
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
            },
            {
                field: 'productRule',
                title: '产品定义',
                width: 100,
                formatter: function (val, row) {
                    return val.name;
                }
            },
            {
                field: 'sequenceNumber',
                title: '排序号',
                width: 100
            },
            {
                field: 'productionCapacity',
                title: '生产能力',
                width: 100
            },
            {
                field: 'parent',
                title: '父产品段',
                width: 120,
                formatter: function (val, row) {
                    if(val){
                        return val.text;
                    } else {
                        return '';
                    }

                }
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
            if(row){
                $('#ProductSegmentParameterTable').datagrid('load',{productSegmentId : row.id});
                $('#MaterialSpecificationTable').datagrid('load',{productSegmentId : row.id});
            }
        }
    });

    ProductSegmentToolbar = {
        url: "",
        message : "",
        search: function () {
            $(tableId).datagrid('load', {
                text: $.trim($('input[name="search"]').val())
            });
        },
        create: function () {
            var row = $('#ProductRuleTable').datagrid('getSelected');
            console.log(row);
            if(row) {
                $(dialogId).dialog('open').dialog('setTitle', '新增' + titleText);
                $(formTitleId).text(titleText);
                $('input[name="text"]').focus();
                $(formId).form('clear');
                $(formId + ' input[name="productRule"]').val(row.id);
                url = urlPrefix + 'create';
                message = '新增'  + titleText;
            }else {
                $.messager.alert('警告！', '没有选择产品定义，无法添加！', 'warning');
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
                    $(formId + ' input[name="parent"]').val(row.parent.id);
                    $(formId + ' input[name="productRule"]').val(row.productRule.id);
                    $('#processSegmentComboboxForProductRule').combobox('reload');
                    $('#processSegmentComboboxForProductRule').combobox('setValue',row.processSegment.id);
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
                            },
                            error: function (XMLHttpRequest, textStatus, errorThrown) {
                                $.messager.progress('close');
                                $.messager.alert('删除失败','错误信息: ' + XMLHttpRequest.responseText,'error');
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
                var entity;
                var parentId = $(formId + ' input[name="parent"]').val();
                if(parentId) {
                    entity = {
                        id : $(formId + ' input[name="id"]').val(),
                        text : $(formId + ' input[name="text"]').val(),
                        duration : $(formId + ' input[name="duration"]').val(),
                        unit : $(formId + ' input[name="unit"]').val(),
                        sequenceNumber : $(formId + ' input[name="sequenceNumber"]').val(),
                        productionCapacity : $(formId + ' input[name="productionCapacity"]').val(),
                        'processSegment.id' : $('#processSegmentComboboxForProductRule').combobox('getValue'),
                        'productRule.id' : $(formId + ' input[name="productRule"]').val(),
                        'parent.id' : parentId
                    }
                } else {
                    entity = {
                        id : $(formId + ' input[name="id"]').val(),
                        text : $(formId + ' input[name="text"]').val(),
                        duration : $(formId + ' input[name="duration"]').val(),
                        unit : $(formId + ' input[name="unit"]').val(),
                        sequenceNumber : $(formId + ' input[name="sequenceNumber"]').val(),
                        productionCapacity : $(formId + ' input[name="productionCapacity"]').val(),
                        'processSegment.id' : $('#processSegmentComboboxForProductRule').combobox('getValue'),
                        'productRule.id' : $(formId + ' input[name="productRule"]').val()
                    }
                }

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
        refresh : function () {
            $(tableId).datagrid('reload');
        }
    }

});
