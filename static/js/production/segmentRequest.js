/**
 * Created by ericlee on 2017/7/27.
 */
$(function () {

    var urlPrefix = '/production/productionRequest/';
    var idPrefix = 'ProductionRequest';
    var titleText = "生产请求";

    var tableId = "#" + idPrefix + "Table" + "ForSegmentRequest";
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
        //toolbar: toolbarId,
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
                field: 'batchCode',
                title: '批次号',
                width: 100
            },
            {
                field: 'productRule',
                title: '产品',
                width: 100,
                formatter: function (val, row) {
                    return val.name;
                }
            },
            {
                field: 'quantity',
                title: '投料量',
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
            },
            {
                field: 'priority',
                title: '优先级',
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
            if(row){
                $('#SegmentRequestTable').datagrid('load',{productionRequestId : row.id})
            }
        }
    });

    $('#SegmentRequestTable').datagrid({
        url: '/production/segmentRequest/findAll',
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
        //toolbar: toolbarId,
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
                width: 30
            },
            {
                field: 'workOrderCode',
                title: '工单号',
                width: 50
            },
            {
                field: 'processSegment',
                title: '过程段',
                width: 80,
                formatter: function (val, row) {
                    return val.text;
                }
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
            },
            {
                field: 'duration',
                title: '持续时间',
                width: 60
            },
            {
                field: 'text',
                title: '描述',
                width: 40
            }
        ]],
        onLoadSuccess: function (data) {
            if (data.rows.length !== 0) {
                $('#SegmentRequestTable').datagrid("selectRow", 0);
            }
        },
        onSelect: function (index, row) {
            if(row){
                $('#ProductSegmentParameterTableForSegmentRequest').datagrid('options').url = '/product/productSegmentParameter/findAll';
                $('#ProductSegmentParameterTableForSegmentRequest').datagrid('load',{productSegmentId : row.productSegment.id});
                $('#MaterialSpecificationTableForSegmentRequest').datagrid('options').url = '/product/materialSpecification/findAll';
                $('#MaterialSpecificationTableForSegmentRequest').datagrid('load',{productSegmentId : row.productSegment.id});
            }
        }
    });

    $('#ProductSegmentParameterTableForSegmentRequest').datagrid({
        //url: 'product/productSegmentParameter/' + 'findAll',
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
        //toolbar: toolbarId,
        columns: [[
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
                field: 'value',
                title: '值',
                width: 100
            },
            {
                field: 'unit',
                title: '单位',
                width: 100
            }
        ]]
    });

    var materialUseMap;
    $.get("/product/materialSpecification/findAllMaterialUse", function (data, status) {
        materialUseMap = data;
    });

    $('#MaterialSpecificationTableForSegmentRequest').datagrid({
        //url: 'product/materialSpecification/' + 'findAll',
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
        //toolbar: toolbarId,
        columns: [[
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
            }
        ]]
    });

});
