/**
 * Created by ericlee on 2017/7/27.
 */
$(function () {

    var resourceTypeNameMap;
    $.get("/Model/permission/findAllResourceType", function (data, status) {
        resourceTypeNameMap = data;
        console.log(resourceTypeNameMap);
    });

    $('#permission').treegrid({
        url: '/Model/permission/findAllPermission',
        idField: 'id',
        treeField: 'text',
        fit: true,
        fitColumns: true,
        striped: true,
        rownumbers: true,
        border: false,
        pagination: false,
        singleSelect:false,
        // pageSize: 20,
        // pageList: [10, 20, 30, 40, 50],
        // pageNumber: 1,
        toolbar: '#permission_tool',
        columns: [[
            {
                field: 'ck',
                width: 30,
                checkbox: true
            },
            {
                field: 'text',
                title: '名称',
                width: 120
            },
            {
                field: 'id',
                title: '编号',
                align: 'center',
                width: 50
            },
            {
                field: 'resourceType',
                title: '资源类型',
                formatter: formatResourceType,
                width: 50
            },
            {
                field: 'url',
                title: '资源路径',
                width: 120
            },
            {
                field: 'permission',
                title: '权限字符串',
                width: 120
            },
            {
                field: 'parentId',
                title: '父编号',
                align: 'center',
                width: 50
            },
            {
                field: 'available',
                title: '状态',
                align: 'center',
                formatter: formatState,
                width: 50
            },
            {
                field: 'iconCls',
                title: '图标',
                width: 50,
                align: 'center',
                formatter: formatIcon
            }
        ]]
    });

    function formatIcon(val, row) {
        var imgUrl = '/assets/easyui/themes/icons/' + val.substring(val.indexOf('-') + 1) + '.png';
        return '<img src="' + imgUrl + '" />';
    }

    function formatState(val, row) {
        return val ? '<span class="label-green">启用</span>' : '<span class="label-red">禁用</span>';
    }

    function formatResourceType(val, row) {
        return resourceTypeNameMap[val];
    }

    permission_tool = {
        url: "",
        message : "",
        search: function () {
            $('#permission').treegrid('load', {
                permission: $.trim($('input[name="search_permission"]').val())
            });
        },
        create: function () {
            $('#permission_dialog').dialog('open').dialog('setTitle', '新增权限');
            $('input[name="id"]').focus();
            $('#permission_form').form('clear');
            $('#resourceType').combobox('textbox').bind('focus',function(){
                $('#resourceType').combobox('showPanel');
            });
            $('#available').combobox('textbox').bind('focus',function(){
                $('#available').combobox('showPanel');
            });
            url = '/Model/permission/create';
            message = '新增';
        },
        update : function () {
            var rows = $('#permission').treegrid('getSelections');
            if (rows.length > 1) {
                $.messager.alert('警告操作！', '编辑记录只能选定一条数据！', 'warning');
            } else if (rows.length == 1) {
                var row = $('#permission').treegrid('getSelected');
                if (row) {
                    $('#permission_dialog').dialog('open').dialog('setTitle', '编辑权限');
                    $('#permission_form').form('load', row);
                    $('input[name="id"]').validatebox('disable');
                    $('input[name="text"]').focus();
                    //$('#available').combobox('setValue',row['available']);
                    url = '/Model/permission/create';
                    message = '编辑';
                }
            } else if (rows.length == 0) {
                $.messager.alert('警告操作！', '编辑记录至少选定一条数据！', 'warning');
            }
        },
        remove : function () {
            var rows = $('#permission').treegrid('getSelections');
            if (rows.length > 0) {
                $.messager.confirm('确定操作', '您正在要删除所选的记录吗？', function (flag) {
                    if (flag) {
                        var ids = [];
                        for (var i = 0; i < rows.length; i ++) {
                            ids.push(rows[i].id);
                        }
                        var sendIds = { ids: ids.join(',')};
                        console.log(sendIds);
                        $.ajax({
                            type : 'POST',
                            contentType:'application/json; charset=utf-8',
                            dataType:'json',
                            url : '/Model/permission/remove',
                            data : JSON.stringify(sendIds),
                            beforeSend : function () {
                                //$('#permission').treegrid('正在删除中...');
                            },
                            success : function (data) {
                                if (data) {
                                    $('#permission').treegrid('loaded');
                                    $('#permission').treegrid('load');
                                    $('#permission').treegrid('unselectAll');
                                    $.messager.show({
                                        title : '提示',
                                        msg : data + '个权限被删除成功！',
                                    });
                                }
                            },
                        });
                    }
                });
            } else {
                $.messager.alert('提示', '请选择要删除的记录！', 'info');
            }
        },
        save : function () {
            if ($('#permission_form').form('validate')) {

                var permission = {
                    id : $('input[name="id"]').val(),
                    text : $('input[name="text"]').val(),
                    resourceType : $('#resourceType').combobox('getValue'),
                    url : $('input[name="url"]').val(),
                    permission : $('input[name="permission"]').val(),
                    parentId : $('input[name="parentId"]').val(),
                    available : Boolean($('#available').combobox('getValue')),
                    iconCls : $('input[name="iconCls"]').val()
                };
                $.ajax({
                    url : url,
                    type : 'post',
                    contentType:'application/json; charset=utf-8',
                    dataType:'json',
                    data : JSON.stringify(permission),
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
                                msg :  message + '权限成功',
                                style:{
                                    right:'',
                                    top:document.body.scrollTop+document.documentElement.scrollTop,
                                    bottom:''
                                }
                            });
                            $('#permission_form').form('reset');
                            $('#permission_dialog').dialog('close');
                            $('#permission').treegrid('reload');
                        } else {
                            $.messager.alert(message + '失败！', '未知错误导致失败，请重试！', 'warning');
                        }
                    }
                });
            }
        },
        refresh : function() {
            $('#permission').treegrid('reload');
        }
    }

});
