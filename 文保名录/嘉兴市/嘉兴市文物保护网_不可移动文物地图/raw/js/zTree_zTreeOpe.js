var zTree, rMenu;
var setting = {
    data: {

        simpleData: {
            enable: true
        }
    },
    callback: {
        onRightClick: OnRightClick, //用于捕获 zTree 上鼠标右键点击之后的事件回调函数
        onClick: zTreeOnClick //节点单击事件
    }
};
$(document).ready(function () {
    $.fn.zTree.init($("#wwtree"), setting, TreezNodes);
    zTree = $.fn.zTree.getZTreeObj("wwtree");
    rMenu = $("#rMenu");
    setwwNodeicon();
});

function zTreeOnClick(event, treeId, treeNode) {
    var nodeID = treeNode.id //节点ID
    var nodeType = treeNode.nodeType//节点类型
    var nodeLevel = treeNode.level; //节点层次，从0开始
    var nodeName = treeNode.name; //节点名称
    parent.ClearAll();
    $.ajax({
        cache: false,
        type: "POST",
        url: "Handler/PostHandler.ashx",
        dataType: 'json',
        data: "action=OnClickTree&nodeID=" + nodeID + "&nodeType=" + nodeType + "&nodeLevel=" + nodeLevel + "&nodeName=" + escape(nodeName),
        success: function (result) {
            var a = result;
            parent.displayfwxAndwwd(result);
        },
        error: function () {
        }
    });
}

function OnRightClick(event, treeId, treeNode) //右键菜单回调事件
{
    if (!treeNode && event.target.tagName.toLowerCase() != "button" && $(event.target).parents("a").length == 0) {
        zTree.cancelSelectedNode();
        $("#rMenu ul").hide();
    } else if (treeNode && !treeNode.noR) {
        zTree.selectNode(treeNode);
        showRMenu(treeNode.level, event.clientX, event.clientY);
    }
}

function showRMenu(type, x, y) {
    $("#rMenu ul").show();

    rMenu.css({ "top": y + "px", "left": x + "px", "visibility": "visible" });
    $("body").bind("mousedown", onBodyMouseDown);
}
function onBodyMouseDown(event) {
    if (!(event.target.id == "rMenu" || $(event.target).parents("#rMenu").length > 0)) {
        rMenu.css({ "visibility": "hidden" });
    }
}

function setwwNodeicon() //根据nodes的nodeType值设置文物点层的icon
{
    var treeObj = $.fn.zTree.getZTreeObj("wwtree");
    var nodes = treeObj.getNodesByFilter(filter);
    for (i = 0; i < nodes.length; i++) {
        var wwtypeindex = nodes[i].nodeType.substr(2, 1);
        nodes[i].icon = "css/zTree/zTreeStyle/img/diy/" + wwtypeindex + ".png";
        treeObj.updateNode(nodes[i]);
    }

}


function filter(node) //获取目录树的文物层节点
{
    return (node.level == 3);
}

function ztreeExpand()//全部展开
{
    zTree.expandAll(true);
    zTree.cancelSelectedNode();
    $("#rMenu ul").hide();
    rMenu.css({ "visibility": "hidden" }); //不加会出现一个小点
}
function ztreeCollapse()//全部折叠
{
    zTree.expandAll(false);
    zTree.cancelSelectedNode();
    $("#rMenu ul").hide();
    rMenu.css({ "visibility": "hidden" });
}
function ztreeIniti() //把树还原成初始加载状态
{
    $.fn.zTree.init($("#wwtree"), setting, TreezNodes);
    zTree.cancelSelectedNode();
    $("#rMenu ul").hide();
    rMenu.css({ "visibility": "hidden" });
    setwwNodeicon(); //设置目录树文物点层的Icon
}
//查询目录树节点
function ztreeQuery() {
    $("#rMenu ul").hide();
    rMenu.css({ "visibility": "hidden" });
    parent.showFindTreeWin();

}

var fnodename//存储传过来的节点名称
function queryTreetNode(nodeName) {
    fnodename = "";
    var treeObj = $.fn.zTree.getZTreeObj("wwtree");
    fnodename = nodeName
    var node = treeObj.getNodesByFilter(ftfilter, true); //仅查找一个节点
    treeObj.expandNode(node);
    treeObj.selectNode(node);
}

function ftfilter(node) {
    return (node.name.indexOf(fnodename) > -1); //根据节点名称模糊查询
}
function hideRMenu() //隐藏菜单
{
    if (rMenu) rMenu.css({ "visibility": "hidden" });
    $("body").unbind("mousedown", onBodyMouseDown);

}
