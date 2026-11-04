
function showdyhInfowindow(evt) //点击大运河图层上的点显示基本信息窗口
{
    var slglmpLayer = map.getLayer("glGraphicsLayer");
    slglmpLayer.clear();
    var wwd = evt.graphic;
    var ptype = wwd.attributes.dyhgratype;
    if (ptype == "point") {
        var wwdvalue = wwd.attributes.value;
        var infoWindow = map.infoWindow;
        var highLightSymbol = new esri.symbol.PictureMarkerSymbol({ "url": "img/around.gif", "height": 20, "width": 20 });
        if (wwd.attributes != undefined) {
            var wincontent = setdyhBasicWin(wwdvalue);
            infoWindow.setContent(wincontent);
            infoWindow.setTitle("大运河遗产信息概况窗口");
            var myPoint = new esri.geometry.Point(wwd.geometry.x, wwd.geometry.y);
           infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
            var connectZoomEnd = dojo.connect(map, "onExtentChange", function () {
                infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
//                dojo.disconnect(connectZoomEnd);
            });
            slglmpLayer.add(new esri.Graphic(myPoint, highLightSymbol));
            //当关闭infoWindow时清除高亮层
            var connectCloseWin = dojo.connect(infoWindow, "onHide", function () {
                var slglmpLayer = map.getLayer("glGraphicsLayer");
                slglmpLayer.clear();
                dojo.disconnect(connectCloseWin);
                dojo.disconnect(connectZoomEnd);
            });
        } 
    }
}

//点击大运河目录树显示大运河信息窗口
function showClicktreeWin(value) {
    var slglmpLayer = map.getLayer("glGraphicsLayer");
    slglmpLayer.clear();
        var infoWindow = map.infoWindow;
        var highLightSymbol = new esri.symbol.PictureMarkerSymbol({ "url": "img/around.gif", "height": 20, "width": 20 });
        if (value.X != null) {
            var wincontent = setdyhBasicWin(value);
            infoWindow.setContent(wincontent);
            infoWindow.setTitle("大运河遗产信息概况窗口");
            var myPoint = new esri.geometry.Point(parseFloat(value.X), parseFloat(value.Y));
            //infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
         //  slglmpLayer.add(new esri.Graphic(myPoint, highLightSymbol));
            //当关闭infoWindow时清除高亮层

            var connectZoomEnd = dojo.connect(map, "onExtentChange", function () {
                infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
                //                dojo.disconnect(connectZoomEnd);
            });
            map.centerAt(myPoint);
            var connectCloseWin = dojo.connect(infoWindow, "onHide", function () {
                var slglmpLayer = map.getLayer("glGraphicsLayer");
                slglmpLayer.clear();
                dojo.disconnect(connectCloseWin);
                dojo.disconnect(connectZoomEnd);
            });
        }
    



}



function showInfowindow(evt) //点击图上的文物点显示文物信息窗口
{
    window.clearTimeout(t);
    var slglmpLayer = map.getLayer("glGraphicsLayer");
    slglmpLayer.clear();
    var fwxLayer = map.getLayer("fwxGraphicsLayer");
    fwxLayer.clear();
    var wwd = evt.graphic;
    var wwdvalue = wwd.attributes.value;
    var infoWindow = map.infoWindow;
    var highLightSymbol = new esri.symbol.PictureMarkerSymbol({ "url": "img/around.gif", "height": 20, "width": 20 });
    if (wwd.attributes != undefined) {
        var dj = "";
        //根据文物ID查询对应的Article表中的ID,供articleshow使用

        var wincontent = setwwdWinCont(wwdvalue);
        infoWindow.setContent(wincontent);
        infoWindow.setTitle("不可移动文物信息窗口");
        var myPoint = new esri.geometry.Point(wwd.geometry.x, wwd.geometry.y);
        var connectZoomEnd = dojo.connect(map, "onExtentChange", function () {
            infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));

        });
        infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
        slglmpLayer.add(new esri.Graphic(myPoint, highLightSymbol));
        //当关闭infoWindow时清除高亮层
        var connectCloseWin = dojo.connect(infoWindow, "onHide", function () {
            var slglmpLayer = map.getLayer("glGraphicsLayer");
            slglmpLayer.clear();
            dojo.disconnect(connectCloseWin);
            dojo.disconnect(connectZoomEnd);
        });
        var isApprove = wwdvalue.IsApprove;
        if (isApprove != null && isApprove.replace(/\s/g, "") == "1") //有保护线、范围线
        {
            setBHXKZX(wwdvalue.bhxcoord, wwdvalue.kzxcoord); //调用绘制保护线，控制线
        }
       // map.centerAndZoom(myPoint, 5);//要放在最后，要不会出不来信息窗口
    }
}


function setwwdWinCont(result)//设置文物点信息窗口内容
{
    var content =
                "<div >" +
                    "<div style='font-size:13px;margin:0; padding:0'>" +
                             "<table style='line-height:25px; width:280px'  cellspacing='0' cellpadding='0'>" +
                                "<tr>" +
                                      "<td  style='font-weight:bold;white-space:nowrap' class='infortd'>" + "文物名称：" + "</td>" +
                                      "<td class='infortd'>" + result.Bkydwwmc + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "级别：" + "</td>" +
                                     "<td class='infortd'>" + getwwdjbName(result.Bkydwwjibie) + "</td>" +
                                "</tr>" +
                                  "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "地址：" + "</td>" +
                                      "<td class='infortd'>" + result.Addr + "</td>" +
                                "</tr>" +
                                "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "年代：" + "</td>" +
                                     "<td class='infortd'>" + result.Bkydwwniandai + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "类别：" + "</td>" +
                                     "<td class='infortd'>" + '&nbsp' + result.bkwwtype + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td colspan='2' style='text-align:center' valign='top'>" + "<a href=../ShowDetail.aspx?wwid=" + result.Bkydwwid + " target='_blank'" + " >" + "<br>点击查看详细信息...</a>" + "</td>" +
                                "</tr>" +
                         "</table>" +
                  "</div>" +
            "</div>"
    return content;
}


function setBHXKZX(bhxcoord, kzxcoord)//生成保护线和控制线 
{
    var fwxGraphicLayer = map.getLayer("fwxGraphicsLayer");
    fwxGraphicLayer.clear();
    var kzxsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_DASH, new dojo.Color([0, 0, 255]), 4); //控制性样式
    var kzx = new esri.geometry.Polyline(); //控制线
    var BHX = bhxcoord;
    var KZX = kzxcoord;
    if (BHX != null && KZX != null) {
        if (BHX.indexOf(";") > 0) //是否包含";"包含表示有多个保护线
        {
            var bhxvalue = BHX.split(";");
            for (var i = 0; i < bhxvalue.length; i++) {
                setBHX(bhxvalue[i])
            }
        }
        else {

            setBHX(BHX)
        }
        var kzxcoord = KZX.split(",");
        // 生成保护线
        var kzxArray = new Array(); //存储控制线的坐标数组
        for (var i = 0; i < kzxcoord.length; i += 2) {
            kzxArray.push([kzxcoord[i], kzxcoord[i + 1]]);
        }
        kzx.addPath(kzxArray);
        fwxGraphicLayer.add(new esri.Graphic(kzx, kzxsymbol));
    }
}
//生成保护线
function setBHX(BHX) {
    var bhxsymbol = new esri.symbol.SimpleLineSymbol(esri.symbol.SimpleLineSymbol.STYLE_SOLID, new dojo.Color([255, 0, 0]), 2); //保护线样式
    var bhxcoord = BHX.split(",");
    var bhx = new esri.geometry.Polyline(); //
    var  bhxArray = new Array(); //存储保护线的坐标数组
    var fwxGraphicLayer = map.getLayer("fwxGraphicsLayer");
    for (var i = 0; i < bhxcoord.length; i += 2) {
            bhxArray.push([bhxcoord[i], bhxcoord[i + 1]]);
        }
        bhx.addPath(bhxArray);
        fwxGraphicLayer.add(new esri.Graphic(bhx, bhxsymbol))

}


function showAQWinClick(result, i)//点击属性查询的结果列表，弹出Inforwindow
{
    window.clearTimeout(t);
    var slglmpLayer = map.getLayer("glGraphicsLayer");
    slglmpLayer.clear();
    var fwxLayer = map.getLayer("fwxGraphicsLayer");
    fwxLayer.clear();
    var highLightSymbol = new esri.symbol.PictureMarkerSymbol({ "url": "img/around.gif", "height": 20, "width": 20 });
    var infoWindow = map.infoWindow;
    var myPoint = new esri.geometry.Point(parseFloat(result.X), parseFloat(result.Y)); //
    showmap(result, i);
    var wincontent = setwwdWinCont(result,getArticleIDBywwid(result.Bkydwwid));
    infoWindow.setContent(wincontent);
    infoWindow.setTitle("不可移动文物信息窗口");
    var connectZoomEnd = dojo.connect(map, "onExtentChange", function () {
        infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
    });
   infoWindow.show(map.toScreen(myPoint), map.getInfoWindowAnchor(map.toScreen(myPoint)));
    slglmpLayer.add(new esri.Graphic(myPoint, highLightSymbol));
    //当关闭infoWindow时清除高亮层
    var connectCloseWin = dojo.connect(infoWindow, "onHide", function () {
        var slglmpLayer = map.getLayer("glGraphicsLayer");
        slglmpLayer.clear();
        dojo.disconnect(connectCloseWin);
        dojo.disconnect(connectZoomEnd);
    });
    var isApprove = result.IsApprove;
    if (isApprove != null && isApprove.replace(/\s/g, "") == "1") {
        setBHXKZX(result.bhxcoord, result.kzxcoord); //调用绘制保护线，控制线
    }
    map.centerAt(myPoint);
}

function getArticleIDBywwid(wwdid) //根据文物点ID获取在文章表中的相应ArticleID
{
    var articleID =null;
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        async: false,
        url: "handler/queryArticleIDBywwid.ashx?wwdid=" + wwdid,
        success: function (result) {
            articleID = result;
        },
        error: function (e) { //alert(e.responseText) 
        }
    });
    return articleID;
}


//量测功能
function setTool(toolname) {
    try {
        navToolbar.deactivate();
        measureToolbar.deactivate();
    } catch (e) { }

    switch (toolname) {
        case "length":
            {
                measureToolbar.activate(Measurename.measure_length);
                //量测的时候鼠标样式变成尺子
                dojo.connect(map, "onMouseMove", function () { $(".layerTile").css("cursor", "url('img/mea.cur'),auto"); });
                break;
            }
        case "area":
            {
                measureToolbar.activate(Measurename.measure_area);
                dojo.connect(map, "onMouseMove", function () { $(".layerTile").css("cursor", "url('img/mea.cur'),auto"); });
                break;
            }
    }

}



//设置大运河基本信息窗口
function setdyhBasicWin(result) {

    var hrefurl;
    if (result.treeID == 5) {
        hrefurl = "../ShowcazBasicInfor.aspx";
    }
    if (result.treeID == 11) {
        hrefurl = "../ShowchqBasicInfor.aspx"
    }
    if (result.treeID == 6 || result.treeID == 7 || result.treeID == 8 || result.treeID == 9 || result.treeID == 10) {
        hrefurl = "../ShowhdBasicInfor.aspx?treeID="+result.treeID
    }

    var content =
                "<div >" +
                    "<div style='font-size:13px;margin:0; padding:0'>" +
                             "<table style='line-height:25px; width:280px'  cellspacing='0' cellpadding='0'>" +
                                "<tr>" +
                                      "<td  style='font-weight:bold;white-space:nowrap' class='infortd'>" + "遗产名称：" + "</td>" +
                                      "<td class='infortd'>" + result.ycmc + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "公布时代：" + "</td>" +
                                     "<td class='infortd'>" + result.gbsd + "</td>" +
                                "</tr>" +
                                  "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "保护级别：" + "</td>" +
                                      "<td class='infortd'>" + result.bhjb + "</td>" +
                                "</tr>" +
                                "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "公布类别：" + "</td>" +
                                     "<td class='infortd'>" + result.gblb + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "公布日期：" + "</td>" +
                                     "<td class='infortd'>" + '&nbsp' + formatcsny(result.gbrq) + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td style='font-weight:bold;' class='infortd'>" + "现在地址：" + "</td>" +
                                     "<td class='infortd'>" + '&nbsp' + result.xzdz + "</td>" +
                                "</tr>" +
                                 "<tr>" +
                                     "<td colspan='2' style='text-align:center' valign='top'>" + "<a href=" + hrefurl + " target='_blank'" + " >" + "<br>点击查看详细信息...</a>" + "</td>" +
                                "</tr>" +
                         "</table>" +
                  "</div>" +
            "</div>"
    return content;
}


//字符串类型时间转换为时间类型
function getDateBystr(strDate) {
    var date = new Date(Date.parse(strDate.replace(/-/g, "/")));
    return date;
}
//格式化日期
function formatcsny(value, rowData, rowIndex) {
    //function里面的三个参数代表当前字段值，当前行数据对象，行号（行号从0开始）
    if (value == "") {
        return "";
    } else {
        var dateValue = getDateBystr(value);
        return dateValue.getFullYear() + "-" + ((dateValue.getMonth() + 1) < 10 ? "0" + (dateValue.getMonth() + 1) : (dateValue.getMonth() + 1)) + "-" + (dateValue.getDate() < 10 ? "0" + dateValue.getDate() : dateValue.getDate());
    }
}


