/**
 * Created by ericlee on 2017/7/27.
 */
$(function () {

    var urlPrefix = '/product/materialSpecification/';
    var idPrefix = 'MaterialSpecification';
    var titleText = "物料规范";

    var tableId = "#" + idPrefix + "Table";
    var toolbarId = "#" + idPrefix + "Toolbar";
    var dialogId = "#" + idPrefix + "Dialog";
    var formId = "#" + idPrefix + "Form";
    var formTitleId = "#" + idPrefix + "FormTitle";

    var materialUseMap;
    $.get("/product/materialSpecification/findAllMaterialUse", function (data, status) {
        materialUseMap = data;
    });

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
        singleSelect: false,
        pageSize: 5,
        pageList: [5, 10, 15, 20],
        pageNumber: 1,
        toolbar: toolbarId,
        columns: [[
            {
                field: 'ck',
                width: 20,
                checkbox: true
            },
            {
                field: 'id',
                title: 'ID',
                align: 'center',
                width: 20
            },
            {
                field: 'materialClass',
                title: '物料类别',
                width: 100,
                formatter: function (val, row) {
                    return val.text;
                }
            },
            {
                field: 'material',
                title: '物料',
                width: 100,
                formatter: function (val, row) {
                    return val.text;
                }
            },
            {
                field: 'materialUse',
                title: '物料用途',
                width: 100,
                formatter: function (val, row) {
                    return materialUseMap[val];
                }
            },
            {
                field: 'text',
                title: '描述',
                width: 80
            },
            {
                field: 'quantity',
                title: '数量',
                width: 100
            },
            {
                field: 'unit',
                title: '单位',
                width: 100
            },
            {
                field: 'productSegment',
                title: '产品段',
                width: 100,
                formatter: function (val, row) {
                    return val.text;
                }
            }
        ]]
    });

    MaterialSpecificationToolbar = {
        url: "",
        message: "",
        search: function () {
            $(tableId).datagrid('load', {
                text: $.trim($('input[name="search"]').val())
            });
        },
        create: function () {
            var row = $('#ProductSegmentTable').datagrid('getSelected');
            if (row) {
                $(dialogId).dialog('open').dialog('setTitle', '新增' + titleText);
                $(formTitleId).text(titleText);
                $(formId).form('clear');
                $(formId + ' input[name="productSegment"]').val(row.id);
                $('#materialClassComboboxForMaterialSpecification').combobox('textbox').bind('focus',function(){
                    $('#materialClassComboboxForMaterialSpecification').combobox('showPanel');
                });

                url = urlPrefix + 'create';
                message = '新增' + titleText;
            } else {
                $.messager.alert('警告！', '没有选择产品定义，无法添加！', 'warning');
            }
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
                    $(formId).form('load', row);
                    $('input[name="text"]').focus();
                    $(formId + ' input[name="productSegment"]').val(row.productSegment.id);
                    $('#materialClassComboboxForMaterialSpecification').combobox('setValue',row.materialClass.id);
                    $('#materialComboboxForMaterialSpecification').combobox('setValue',row.material.id);
                    url = urlPrefix + 'update';
                    message = '编辑' + titleText;
                }
            } else if (rows.length == 0) {
                $.messager.alert('警告操作！', '请至少选定一条数据进行编辑！', 'warning');
            }
        },
        delete: function () {
            var rows = $(tableId).datagrid('getSelections');
            if (rows.length > 0) {
                $.messager.confirm('确定操作', '您正在删除所选的记录吗？', function (flag) {
                    if (flag) {
                        var ids = [];
                        for (var i = 0; i < rows.length; i++) {
                            ids.push(parseInt(rows[i].id));
                        }
                        $.ajax({
                            url: urlPrefix + 'delete',
                            method: 'POST',
                            traditional: true,
                            data: {ids: ids},
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
                                        msg: '删除' + titleText + '成功',
                                        style: {
                                            right: '',
                                            top: document.body.scrollTop + document.documentElement.scrollTop,
                                            bottom: ''
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
        save: function () {
            if ($(formId).form('validate')) {
                var entity = {
                    id: $(formId + ' input[name="id"]').val(),
                    'materialClass.id' : $('#materialClassComboboxForMaterialSpecification').combobox('getValue'),
                    'material.id' : $('#materialComboboxForMaterialSpecification').combobox('getValue'),
                    'materialUse' : $('#materialUse').combobox('getValue'),
                    text: $(formId + ' input[name="text"]').val(),
                    quantity: $(formId + ' input[name="quantity"]').val(),
                    unit: $(formId + ' input[name="unit"]').val(),
                    'productSegment.id': $(formId + ' input[name="productSegment"]').val()
                };

                $.ajax({
                    url: url,
                    method: 'POST',
                    traditional: true,
                    data: entity,
                    beforeSend: function () {
                        $.messager.progress({
                            text: '正在' + message + '中...'
                        });
                    },
                    success: function (data, response, status) {
                        $.messager.progress('close');

                        if (data > 0) {
                            $.messager.show({
                                title: '提示',
                                msg: message + '成功',
                                style: {
                                    right: '',
                                    top: document.body.scrollTop + document.documentElement.scrollTop,
                                    bottom: ''
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
