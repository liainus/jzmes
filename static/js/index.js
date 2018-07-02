/**
 * Created by ericlee on 2017/7/27.
 */
$(function () {
    $('#RightTree').tree({
        url: 'Model/permission/findMenusById',
        lines: true,
        onLoadSuccess: function (node, data) {
            var _this = this;
            if (data) {
                $(data).each(function (index, value) {
                    if (this.state == 'closed') {
                        $(_this).tree('expandAll');
                    }
                });
            }
        },
        onClick: function (node) {
            console.log(node);
            if (node.url && node.resourceType=='MENU_ITEM') {
                if ($('#MainTab').tabs('exists', node.text)) {
                    $('#MainTab').tabs('select', node.text)
                } else {
                    $('#MainTab').tabs('add', {
                        title: node.text,
                        closable: true,
                        iconCls: node.iconCls,
                        href: node.url
                    });
                }
            }
        }
    })
});