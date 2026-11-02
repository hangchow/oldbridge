(function(window, document){
	var viewportNode,
		viewportContent = "",
		ua = window.navigator.userAgent.toLowerCase(),
		scalable = ",user-scalable=no";
if(window.devicePixelRatio>2){
	window.devicePixelRatio=2;
}
	var scale=1/window.devicePixelRatio;

	if (ua.indexOf("android") >= 0) {
		viewportContent = "width=device-width" + scalable+", maximum-scale="+scale+", minimum-scale="+scale+",target-densitydpi=320";
	}else if(ua.indexOf("ios") >= 0 || ua.indexOf("iphone") >= 0 || ua.indexOf("ipod") >= 0 || ua.indexOf("ipad") >= 0){
		viewportContent = "width=device-width" + scalable+", maximum-scale="+scale+", minimum-scale="+scale;
	}else{
		viewportContent = "width=640" + scalable+", maximum-scale="+scale+", minimum-scale="+scale;
	}
	viewportNode = document.querySelector('meta[name=viewport]');
	if(viewportNode){
		viewportNode.content = viewportContent;
	}else{
		viewportNode = document.createElement("meta");
		viewportNode.name = "viewport";
		viewportNode.content = viewportContent;
		document.head.appendChild(viewportNode);
	}
})(this, this.document);