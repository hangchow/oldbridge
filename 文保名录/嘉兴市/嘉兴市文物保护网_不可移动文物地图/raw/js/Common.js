function getwwdPicSymbol(wwjb,wwlb)//根据文物级别和类别获取文物点的pictureSymbol
{
    var wwdsymbol;
    var wwtype = wwlb.replace(/\s/g, "");
    var wwtypenum=wwtype.substr(1,1)
    switch (wwtypenum) {
        case "1":
            return wwdsymbol = new esri.symbol.PictureMarkerSymbol("img/marker/gyz" + wwjb + ".png", 20, 20); //文物点样式
            break;
        case "2":
            return wwdsymbol = new esri.symbol.PictureMarkerSymbol("img/marker/gmz" + wwjb + ".png", 20, 20);
            break;
        case "3":
            return wwdsymbol = new esri.symbol.PictureMarkerSymbol("img/marker/gjz" + wwjb + ".png", 20, 20);
            break;
        case "4":
            return wwdsymbol = new esri.symbol.PictureMarkerSymbol("img/marker/sksjsk" + wwjb + ".png", 20, 20);
            break;
        case "5":
            return wwdsymbol = new esri.symbol.PictureMarkerSymbol("img/marker/jxdjz" + wwjb + ".png", 20, 20);
            break;
    }
}
function getwwdjbName(wwjb)//根据文物级别代号获取文物级别名称
{
    var wwjbName;
    switch(wwjb)
    {
        case "1":
            return wwjbName = "全国重点文物保护单位";
            break;
        case "2":
            return wwjbName = "省级文物保护单位";
            break;
        case "3":
            return wwjbName = "县市区级文物保护单位";
            break;
        case "4":
            return wwjbName = "未核定文物保护单位";
            break;
        case "5":
            return wwjbName = "文物保护点";
            break;
    }
}

