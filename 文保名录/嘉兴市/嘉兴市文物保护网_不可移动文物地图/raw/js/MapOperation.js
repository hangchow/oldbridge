var measureToolbar, measureGraphicsLayer;
var wwdGraphicsLayer, fwxGraphicsLayer //定义文物点图层,和行政范围线
var markerGraphicsLayer, glGraphicsLayer; //定义标注层和高亮显示层
var dyhGraphicsLayer; //大运河图层
var pageSize = 7; //每页7条
var dataList = null; //数据源
function initMap() {
    var popupOptions = {
        'markerSymbol': new esri.symbol.SimpleMarkerSymbol('circle', 32, null, new dojo.Color([0, 0, 0, 0.25])),
        'marginLeft': '20',
        'marginTop': '20'
    };
    var popup = new esri.dijit.Popup(popupOptions, dojo.create("div"));

    // 在创建地图时直接设置初始范围
    var initialExtent = new esri.geometry.Extent({
        xmin: 120.30034606933594 - 0.35,  // 向东偏移约35公里,
        ymin: 30.409627868652346,
        xmax: 121.42026489257813,
        ymax: 30.97688433837891,
        spatialReference: { wkid: 4326 }
    });
    
    map = new esri.Map("map", {
        logo: false,
        infoWindow: popup,
        extent: initialExtent
    });

    //添加css样式
    dojo.addClass(map.infoWindow.domNode, "myTheme"); //覆盖原来的样式
    dojo.addClass(map.infoWindow.domNode, "contentPane");
    //为对象注册事件
    dojo.connect(map, 'onLoad', function (map) {
        fwxGraphicsLayer = new esri.layers.GraphicsLayer({ id: "fwxGraphicsLayer" });
        map.addLayer(fwxGraphicsLayer);
        wwdGraphicsLayer = new esri.layers.GraphicsLayer({ id: "wwdGraphicsLayer" });
        map.addLayer(wwdGraphicsLayer);
        measureGraphicsLayer = new esri.layers.GraphicsLayer({ id: "measureGraphicsLayer" });
        map.addLayer(measureGraphicsLayer);
        markerGraphicsLayer = new esri.layers.GraphicsLayer({ id: "markerGraphicsLayer" });
        map.addLayer(markerGraphicsLayer);
        dyhGraphicsLayer = new esri.layers.GraphicsLayer({ id: "dyhGraphicsLayer" });
        map.addLayer(dyhGraphicsLayer);
        glGraphicsLayer = new esri.layers.GraphicsLayer({ id: "glGraphicsLayer" });
        map.addLayer(glGraphicsLayer);
        var scalebar = new esri.dijit.Scalebar({
            map: map,
            scalebarUnit: 'metric'
        });
        // 设置初始范围
        // var initialExtent = new esri.geometry.Extent({
        //     xmin: 120.30034606933594,
        //     ymin: 30.409627868652346,
        //     xmax: 121.42026489257813,
        //     ymax: 30.97688433837891,
        //     spatialReference: { wkid: 4326 }
        // });
        // map.setExtent(initialExtent);
    });
    dojo.connect(dijit.byId('map'), 'resize', map, map.resize);
    navToolbar = new esri.toolbars.Navigation(map);
    measureToolbar = new Measure(map);
    dojo.connect(navToolbar, "onExtentHistoryChange", function () {
        navToolbar.deactivate();
    });
    map.infoWindow.resize(300, 350);
    var basemap = new TDTLayer({ id: "layer0" }); //底片  在TDTTiledLayer.js中定义
    var basemapAnno = new TDTLayerAnno({ id: "layer1" }); //标注
    //var ab = new rbTDTLayerthAnno({ id: "layer2" }); //标注
    map.addLayer(basemap);
    map.addLayer(basemapAnno);
    // map.addLayer(ab);
    meatureGraphicClick();
    dojo.connect(markerGraphicsLayer, "onClick", showInfowindow);
    dojo.connect(wwdGraphicsLayer, "onClick", showInfowindow);
    dojo.connect(dyhGraphicsLayer, "onClick", showdyhInfowindow);
    //map.setLevel(0);
    //dojo.connect(map, "onMouseMove", showmappoint);
}
//dojo.addOnLoad接受一个函数作为参数   //需要等到相关js和dom加载完成后执行的代码
dojo.addOnLoad(initMap);
if (type == "2") { dojo.addOnLoad(dispalyAllwwd); }

function showmappoint(evt) {

    var po = evt.mapPoint
    var s = po.x
    var y = po.y;
    var dd = "x=" + s + "y=" + y
    dojo.byId("jjj").innerHTML = dd;
}

function dispalyAllwwd()//显示所有文物点 
{


    $.ajax({
        type: "POST",
        async: false,
        url: "handler/PostHandler.ashx",
        dataType: 'json',
        data: "action=getAllwwd",
        success: function (result) {
            var results = result.Allwwds;
            //aa = result;
            if (results != null) {
                showWWDS(results);

            }
        },
        error: function (e) { //alert(e.responseText) 
        }
    });

    // cluster layer that uses OpenLayers style clustering



}
//点击目录树
//显示行政区划范围线（若有的情况下）和文物点
function displayfwxAndwwd(result) {
    window.clearTimeout(t);
    var wwdGraphicLayer = map.getLayer("wwdGraphicsLayer");
    //    var fwxGraphicLayer = map.getLayer("fwxGraphicsLayer");

    if (result.length == 2) //点击的是行政区划节点
    {
        wwdGraphicLayer.clear();
        //fwxGraphicLayer.clear();
        //        var fwx = new esri.geometry.Polyline(); //范围线
        //        var fwxsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([255, 0, 0]), 2); //行政线样式
        if (result[0].length != 0) //有范围矩形框的值
        {
            var extent = result[0][0].RP.split(',');
            var retcExent = new esri.geometry.Extent(parseFloat(extent[0]), parseFloat(extent[1]), parseFloat(extent[2]), parseFloat(extent[3]), new esri.SpatialReference({ wkid: 4326 }))
            map.setExtent(retcExent);
            var CentPoint = new esri.geometry.Point(parseFloat(result[0][0].cX), parseFloat(result[0][0].cY)); //行政区划政府所在点
            map.centerAt(CentPoint); //地图定位到行政区划中心点
            if (result[1].length != 0) //既有范围矩形框又有文物节点
            {
                showWWDS(result[1]);
            }
        }
    }
    if (result.length == 1) //点击的是文物节点层
    {
        if (result[0][0].X != null) {
            var myPoint = new esri.geometry.Point(result[0][0].X, result[0][0].Y); //点击目录树文物点在地图上的生成的点
            //map.centerAt(myPoint);
            showWWDS(result[0]);
            var infoWindow = map.infoWindow;
            var wincontent = setwwdWinCont(result[0][0], getArticleIDBywwid(result[0][0].Bkydwwid));
            infoWindow.setContent(wincontent);
            infoWindow.setTitle("不可移动文物信息窗口");
            infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
            var isApprove = result[0][0].IsApprove;
            if (isApprove != null && isApprove.replace(/\s/g, "") == "1") {
                setBHXKZX(result[0][0].bhxcoord, result[0][0].kzxcoord); //调用绘制保护线，控制线
            }
            //map.centerAndZoom(myPoint, 5);
            map.centerAt(myPoint);
        }
    }
}

function showWWDS(result) //点击目录树或初始加载时显示文物点
{
    var wwdGraphicLayer = map.getLayer("wwdGraphicsLayer");
    for (var i = 0; i < result.length; i++) {
        if (result[i].X != "") {
            var myPoint = new esri.geometry.Point(parseFloat(result[i].X), parseFloat(result[i].Y)); //初始化显示所有文物点查询出的X，Y坐标为string型，要转为number型才不会在点击graphic时显示错误
            var attr = { "graphictype": "wwd", "value": result[i] };
            wwdGraphicLayer.add(new esri.Graphic(myPoint, getwwdPicSymbol(result[i].Bkydwwjibie, result[i].Bkydwwleibie), attr));
        }
    }
}

function meatureGraphicClick()//点击测量结果的关闭图片，清除测量结果
{
    dojo.connect(measureGraphicsLayer, "onClick", function (evt) {
        try {
            if (evt.graphic.attributes.name === "measure_del") {

                measureGraphicsLayer.clear();

            }
        } catch (e) { }
    });

}

function showWwdTable(result, pageindex) //显示查询的文物点表格
{
    dataList = result;
    var len = result.length; //总记录条数    
    var max_elem = Math.min((1) * pageSize, len);
    for (var i = 0; i < max_elem; i++) {
        var sresulttr = "sresulttr" + i;
        $("#ContentIframe").contents().find("#wwresultTable").append
        ("<tr style='padding-top:7px;' id='" + sresulttr + "'  class='jh'>" +
          "<td  class='cp' ><img src='../Admin/Images/abc/" + (i + 1) + ".png'/></td><td class='cp' ><table>" +
          "<tr style='color:#2888C6;font-weight:bold;font-family:微软雅黑'><td colspan='2' style='font-size:16px'>" + result[i].Bkydwwmc + "</td></tr>" +
          "<tr ><td style='white-space:nowrap;font-size:13px;font-weight:bold'>地址:</td>" +
               "<td style='font-size:12px'>" + result[i].Addr + "</td></tr>" + "</table></td></tr>");
        var row = $("#ContentIframe").contents().find("#" + sresulttr);
        row[0].data = result[i]; //给每行添加自定义属性data，用于保存数据,Iframe这样用，不是Iframe不用加[0]
        row[0].index = i; //用于单击左边查询记录时控制marker中的数字
        row[0].onclick = function () {
            showAQWinClick(this.data, ((this.index) % 7 + 1))
        }
        showmap(dataList[i], (i % 7 + 1))//显示带序号的marker
    }
    if (result.length > pageSize) //查询结果大于所设置的每页的pagesize，显示分页控件
    {
        $("#ContentIframe").contents().find("#Pagination").show();
        $("#ContentIframe").contents().find("#Pagination").pagination(result.length, {
            callback: pageselectCallback,
            prev_text: '前一页',
            next_text: '后一页',
            items_per_page: 7,
            num_display_entries: 1, //连续分页主体部分分页条目数
            current_page: pageindex, //当前页索引
            num_edge_entries: 1//两侧首尾分页条目数         
        });
    }
    else //查询结果小于所设置的每页的pagesize，则不显示分页控件
    {
        $("#ContentIframe").contents().find("#Pagination").hide();
    }
}

function pageselectCallback(pageIndex) //属性查询的翻页回调函数
{
    $("#ContentIframe").contents().find("#wwresultTable").empty();
    ClearGraphic();
    var len = dataList.length; //总记录条数    
    var max_elem = Math.min((pageIndex + 1) * pageSize, len);
    for (var i = pageIndex * pageSize; i < max_elem; i++) {
        var sresulttr = "sresulttr" + i;
        $("#ContentIframe").contents().find("#wwresultTable").append
        ("<tr style='padding-top:7px;' id='" + sresulttr + "'  class='jh'>" +
          "<td  class='cp' ><img src='../Admin/Images/abc/" + ((i % 7) + 1) + ".png'/></td><td class='cp' ><table>" +
          "<tr style='color:#2888C6;font-weight:bold;font-family:微软雅黑'><td colspan='2' style='font-size:16px'>" + dataList[i].Bkydwwmc + "</td></tr>" +
          "<tr ><td style='white-space:nowrap;font-size:13px;font-weight:bold'>地址:</td>" +
               "<td style='font-size:12px'>" + dataList[i].Addr + "</td></tr>" + "</table></td></tr>");
        var row = $("#ContentIframe").contents().find("#" + sresulttr);
        row[0].data = dataList[i]; //给每行添加自定义属性data，用于保存数据
        row[0].index = i; //用于单击左边查询记录时控制marker中的数字
        row[0].onclick = function () {
            showAQWinClick(this.data, ((this.index) % 7 + 1))
        }
        showmap(dataList[i], (i % 7 + 1));
    }
}

function showmap(result, i) //属性查询显示的文物点
{
    var wwdGraphicLayer = map.getLayer("wwdGraphicsLayer");
    var attr = { "graphictype": "wwd", "value": result };
    var myPoint = new esri.geometry.Point(parseFloat(result.X), parseFloat(result.Y)); //点击目录树文物点在地图上的生成的点
    var wwdsymbol = new esri.symbol.PictureMarkerSymbol({ "url": "../Admin/Images/abc/" + i + ".png", "height": 23, "width": 30 }); //文物点样式
    wwdGraphicLayer.add(new esri.Graphic(myPoint, wwdsymbol, attr));
}

function SpPointQuery()//空间点查询 
{
    dataList = null;
    var hand = dojo.connect(map, 'onClick', function (evt) //点击空间查询的参考点，则弹出查询信息窗口
    {
        var infoWindow = map.infoWindow;
        infoWindow.resize(340, 350);
        var geometry = evt.mapPoint;
        drawpoint = geometry; //把点赋给全局变量，供空间点查询调用
        var symbol = new esri.symbol.PictureMarkerSymbol("img/sign_1.png", 18, 25);
        var attr = { "graphictype": 'lsmarkerPoint' };
        var graphic = new esri.Graphic(geometry, symbol, attr);
        map.graphics.add(graphic); //map.graphics图层只用来存储空间查询参考graphic，如参考点或矩形
        var content = setPointWinInfor();
        var scrPnt = map.toScreen(geometry);
        infoWindow.setTitle("空间点查询");
        infoWindow.setContent(content);
        infoWindow.show(scrPnt, map.getInfoWindowAnchor(scrPnt));
        var dojoShape = graphic.getDojoShape();
        var moveable = new dojox.gfx.Moveable(dojoShape);
        var moveStopToken = dojo.connect(moveable, "onMoveStop", function (mover) {
            var tx = dojoShape.getTransform();
            var startPoint = graphic.geometry;
            var endPoint = map.toMap(map.toScreen(startPoint).offset(tx.dx, tx.dy));
            infoWindow.reposition(endPoint);
            dojoShape.setTransform(null);
            graphic.setGeometry(endPoint);
            endPoint.setSpatialReference(map.spatialReference);
            drawpoint = endPoint; //把移动后的点赋给全局变量，供空间点查询调用
            var geoPt = esri.geometry.webMercatorToGeographic(endPoint);
            infoWindow.show(map.toScreen(endPoint), map.getInfoWindowAnchor(map.toScreen(endPoint)));
        });
        dojo.disconnect(hand);
    });

}
function pointQuery()//空间点点击确定按钮执行的查询 
{
    var wwjb = $("#pointsel").val();
    var radius = radvalue;
    var point = drawpoint;
    $.ajax({
        type: "POST",
        url: "handler/PostHandler.ashx",
        dataType: 'json',
        data: "action=getwwdByPoint&wwjb=" + wwjb + "&radius=" + radius + "&point=" + point.x + "," + point.y,
        cache: false,
        success: function (result) {
            if (result.wwd != undefined || result.wwd != null) {
                dataList = result.wwd;
                $("#ContentIframe").contents().find("#wwresultTable").empty();
                Clear();
                if (dataList.length == 0) {
                    $("#ContentIframe").contents().find("#cxresult").html(""); //清除div中的提示内容
                    $("#ContentIframe").contents().find("#cxresult").append("无相关查询记录");
                }
                else {
                    $("#ContentIframe").contents().find("#cxresult").html(""); //清除div中的提示内容
                    $("#ContentIframe").contents().find("#cxresult").append("共查询到" + dataList.length + "条记录！");
                    showWwdTable(result.wwd);
                }
            }
        },
        error: function (e)
        { }
    });
}

function setPointWinInfor() //设置空间点查询信息窗口的内容
{
    var content = "<div>" + "<table '>" +
                              "<tr><td style=' white-space:nowrap;font-weight:bold'>文物等级:</td>" + "<td  >" +
                              "<select id='pointsel' style='width:180px'  >" +
                        "<option value='-1'>全部</option>" +
                        "<option value='1'>全国重点文物保护单位</option>" +
                        "<option value='2'>省级文物保护单位</option>" +
                        "<option value='3'>市、县级文物保护单位</option>" +
                        "<option value='4'>尚未核定为保护单位</option>" +
                       " <option value='5'>文保点</option>" +
                       "</select>" +
                               "</td>" + "<td><img src='img/queding.png' style='cursor:pointer' onclick='pointQuery()'/></td>" +
                              "<tr style='line-height:40px'><td style='font-weight:bold'>搜索半径:</td><td  colspan='2'>" +
                                "<iframe id='pointslider' scrolling='auto'  frameborder='0' " +
                                "src='LengthSlider.htm' marginwidth='0'width='250px'  height='50px' marginheight='0'></iframe>" +
                             "</td></tr>" +
                             "</table></div>"
    return content;
}

function SetRadii(radio)//获取查询半径
{
    radvalue = radio;
    return radvalue;
}

function SpRectQuery()//空间矩形查询 
{
    toolbar.activate(esri.toolbars.Draw.EXTENT); //绘制矩形
}

function addRectToMap(geometry, pageindx) //画完矩形后执行的查询
{
    var symbol = new esri.symbol.SimpleFillSymbol(esri.symbol.SimpleFillSymbol.STYLE_SOLID, new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([255, 0, 0]), 2), new dojo.Color([255, 255, 0, 0.25]));
    var drawExtent = new esri.Graphic(geometry, symbol);
    map.graphics.add(drawExtent);
    toolbar.deactivate(); //释放绘制事件
    if (drawExtent != null && geometry.type == "extent") {
        sppoints = drawExtent.geometry.xmin + "," + drawExtent.geometry.xmax + "," + drawExtent.geometry.ymin + "," + drawExtent.geometry.ymax;
        $.ajax({
            type: "POST",
            url: "handler/PostHandler.ashx",
            dataType: 'json',
            data: "action=getwwdByRect&points=" + sppoints + "",
            success: function (result) {
                if (result != undefined || result != null) {
                    dataList = result.wwd;
                    $("#ContentIframe").contents().find("#wwresultTable").empty();
                    if (dataList.length == 0) {
                        $("#ContentIframe").contents().find("#cxresult").html(""); //清除div中的提示内容
                        $("#ContentIframe").contents().find("#cxresult").append("无相关查询记录");
                    }
                    else {
                        $("#ContentIframe").contents().find("#cxresult").html(""); //清除div中的提示内容
                        $("#ContentIframe").contents().find("#cxresult").append("共查询到" + dataList.length + "条记录！");
                        showWwdTable(result.wwd);
                    }
                }
            },
            error: function (e) { //alert(e.responseText) 
            }
        });
    }
}

//点击大运河目录树中国大运河
function showchinayh() {
    $('#win').window('open');
    $('#win').window({
        href: "../ShowDyhBasicInfor.aspx"
    })
}

//点击大运河目录树上的长虹桥长安闸
function showchqcaz(id) {
    $.ajax({
        cache: false,
        type: "POST",
        url: "Handler/PostHandler.ashx",
        dataType: 'json',
        data: "action=getchqcazxx&treeID=" + id,
        success: function (result) {
            var result = result.qz;
            showClicktreeWin(result[0]);
        }
    });


}

//显示大运河缓冲区、遗产区，本体范围，点击大运河专题目录树
function showdyhfw(id) {
    $.ajax({
        cache: false,
        type: "POST",
        url: "Handler/PostHandler.ashx",
        dataType: 'json',
        data: "action=showdyhRegion&treeID=" + id,
        success: function (result) {
            if (result[1].length != 0) {
                drawdyhLine(result);
            }
        }
    });
}

//点击大运河目录树提供数据
function drawdyhLine(btvalue) {
    if (selGraph.length != 0) {
        for (var i = 0; i < selGraph.length; i++) {
            selGraph[i].show();
        }
    }
    selGraph.length = 0;
    window.clearTimeout(t);
    flashGraph();
    var fwxGraphicLayer = map.getLayer("fwxGraphicsLayer");
    fwxGraphicLayer.clear();

    var jbvalue = btvalue[0];
    var ycqvalue = btvalue[1];
    var hcqvalue = btvalue[2];
    var pvalue = btvalue[3];

    for (var i = 0; i < jbvalue.length; i++) {
        drawjblines(jbvalue[i])
    }
    for (var i = 0; i < ycqvalue.length; i++) {
        drawtreedyhLines(ycqvalue[i], "2", "fwxGraphicsLayer")
    }
    for (var i = 0; i < hcqvalue.length; i++) {
        drawtreedyhLines(hcqvalue[i], "3", "fwxGraphicsLayer")
    }
    showClicktreeWin(pvalue[0]);
}

//或有多条线段的河道本体
function drawjblines(zbcoord) {
    var fwxGraphicLayer = map.getLayer("fwxGraphicsLayer");
    var Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([30, 144, 255]), 2); //河本体样式
    //jbcoord = zbcoord.jbcoord; 
    var attr = { "dyhgratype": "line" };
    var jbcoords = zbcoord.jbcoord.split(";");
    for (var i = 0; i < jbcoords.length; i++) {
        var jbcoord = jbcoords[i];
        if (jbcoord != null) {
            var jbvalue = jbcoord.split(",");
            var jbArray = new Array(); //存储保护线的坐标数组
            var jbx = new esri.geometry.Polyline(); //
            for (var j = 0; j < jbvalue.length; j += 2) {
                jbArray.push([jbvalue[j], jbvalue[j + 1]]);
            }
            jbx.addPath(jbArray);
            fwxGraphicLayer.add(new esri.Graphic(jbx, Basicsymbol, attr))
        }
    }
}


var t
var flag = 0;
var selGraph = new Array();
//显示或隐藏点击点的边界线
function flashGraph() {
    var RccLayer = map.getLayer("fwxGraphicsLayer");
    for (var i = 0; i < RccLayer.graphics.length; i++) {
        selGraph.push(RccLayer.graphics[i]);
    }
    if (!flag) {
        for (var i = 0; i < selGraph.length; i++) {
            selGraph[i].hide();
        }
        flag = 1;
    }
    else {
        for (var i = 0; i < selGraph.length; i++) {
            selGraph[i].show();
        }
        flag = 0;
    }
    t = window.setTimeout("flashGraph()", 250);
}


//单击目录树画大运河线(主要是样式加粗，高亮闪烁)
function drawtreedyhLines(zbcoord, type, layer) {
    var fwxGraphicLayer = map.getLayer(layer);
    var Basicsymbol;
    var jbcoord;
    var jbvalue;
    //    if (type == "1") {
    //        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([30, 144, 255]), 4); //河本体样式
    //        jbcoord = zbcoord.jbcoord;
    //    }
    if (type == "2") {
        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([255, 0, 0]), 4); //河本体样式
        jbcoord = zbcoord.ycqCoord;
    }
    if (type == "3") {
        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([0, 0, 255]), 4); //河本体样式
        jbcoord = zbcoord.hcqCoord;
    }
    var attr = { "dyhgratype": "line" };
    if (jbcoord != null) {
        jbvalue = jbcoord.split(",");
        var jbArray = new Array(); //存储保护线的坐标数组
        var jbx = new esri.geometry.Polyline(); //
        for (var i = 0; i < jbvalue.length; i += 2) {
            jbArray.push([jbvalue[i], jbvalue[i + 1]]);
        }
        jbx.addPath(jbArray);
        fwxGraphicLayer.add(new esri.Graphic(jbx, Basicsymbol, attr))
    }
}


//画大运河线
function drawdyhLines(zbcoord, type, layer) {
    var fwxGraphicLayer = map.getLayer(layer);
    var Basicsymbol;
    var jbcoord;
    var jbvalue;
    if (type == "1") {
        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([34, 139, 34]), 2); //保护区样式
        jbcoord = zbcoord.bhqCoord;
    }
    if (type == "2") {
        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([255, 0, 0]), 2); //河本体样式
        jbcoord = zbcoord.ycqCoord;
    }
    if (type == "3") {
        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([0, 0, 255]), 2); //河本体样式
        jbcoord = zbcoord.hcqCoord;
    }
    if (type == "4") {
        Basicsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([139, 69, 19]), 2); //河本体样式
        jbcoord = zbcoord.jsdCoord;
    }
    var attr = { "dyhgratype": "line" };
    if (jbcoord != null) {
        jbvalue = jbcoord.split(",");
        var jbArray = new Array(); //存储保护线的坐标数组
        var jbx = new esri.geometry.Polyline(); //
        for (var i = 0; i < jbvalue.length; i += 2) {
            jbArray.push([jbvalue[i], jbvalue[i + 1]]);
        }
        jbx.addPath(jbArray);
        fwxGraphicLayer.add(new esri.Graphic(jbx, Basicsymbol, attr))
    }
}


//获取所有大运河河道的本体，遗产区、缓冲区数据
function getAlldyhData() {
    $.ajax({
        cache: false,
        type: "POST",
        url: "Handler/PostHandler.ashx",
        dataType: 'json',
        data: "action=getAlldyhLine",
        success: function (result) {
            if (result[1].length != 0) {
                sendAllDyh(result);
            }
        }
    });
}

//发送大运河本体、遗产区、缓冲区线数据给显示函数
function sendAllDyh(alldyhValue) {

    var bhqvalue = alldyhValue[0];
    var ycqvalue = alldyhValue[1];
    var hcqvalue = alldyhValue[2];
    var dyhpoint = alldyhValue[3];
    var jsdvalue = alldyhValue[4];
    for (var i = 0; i < bhqvalue.length; i++) {
        drawdyhLines(bhqvalue[i], "1", "dyhGraphicsLayer")
    }
    for (var i = 0; i < ycqvalue.length; i++) {
        drawdyhLines(ycqvalue[i], "2", "dyhGraphicsLayer")
    }
    for (var i = 0; i < hcqvalue.length; i++) {
        drawdyhLines(hcqvalue[i], "3", "dyhGraphicsLayer")
    }
    for (var i = 0; i < jsdvalue.length; i++) {
        drawdyhLines(jsdvalue[i], "4", "dyhGraphicsLayer")
    }
    showdyhPointS(dyhpoint)
}

function showdyhPointS(result) //显示大运河河道点
{
    var dyhGraphicLayer = map.getLayer("dyhGraphicsLayer");
    var highLightSymbol = new esri.symbol.PictureMarkerSymbol({ "url": "img/bz3.gif", "height": 26, "width": 20 });


    for (var i = 0; i < result.length; i++) {
        if (result[i].X != null) {
            var myPoint = new esri.geometry.Point(parseFloat(result[i].X), parseFloat(result[i].Y)); //初始化显示所有文物点查询出的X，Y坐标为string型，要转为number型才不会在点击graphic时显示错误
            var attr = { "dyhgratype": "point", "value": result[i] };
            var font = new esri.symbol.Font(14)
            var color = new dojo.Color([160, 32, 240])
            var textSymbol = new esri.symbol.TextSymbol(result[i].ycmc, font, color);
            textSymbol.decoration = esri.symbol.TextSymbol.DECORATION_UNDERLINE
            dyhGraphicLayer.add(new esri.Graphic(myPoint, textSymbol, attr));

        }
    }
}