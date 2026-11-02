
$(function(){
    $.getJSON('http://z1.singdo.org/libao/shareinfo.php?callback=?',
        { 'strURL' :  location.href.split('#')[0]},
        function(data){
			//console.log(data);
            wx.config({
                debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
                appId: data.appId, // 必填，公众号的唯一标识
                timestamp: data.timestamp, // 必填，生成签名的时间戳
                nonceStr: data.nonceStr, // 必填，生成签名的随机串
                signature: data.signature,// 必填，签名，见附录1
                jsApiList: ['checkJsApi',
                    'onMenuShareTimeline',
                    'onMenuShareAppMessage'] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
            });
            window.share = {
                imgUrl : share_img,
                link : share_url,
                title : share_title,
                desc : share_desc
            };

            wx.ready(function () {
                wxcheck();
                function wxcheck(){
                    wx.checkJsApi({
                        jsApiList: [
                            'onMenuShareTimeline',
                            'onMenuShareAppMessage'
                        ],
                        success: function (res) {
                            //alert(JSON.stringify(res));

                        }
                    });
                }

                wx.onMenuShareTimeline({
                    title: window.share.title, // 分享标题
                    link: window.share.link, // 分享链接
                    imgUrl: window.share.imgUrl,
                    desc:  window.share.desc,
                    success: function () {
                        // 用户确认分享后执行的回调函数
                    },
                    cancel: function () {
                        // 用户取消分享后执行的回调函数
                    }
                });

                wx.onMenuShareAppMessage({
                    title: window.share.title, // 分享标题
                    link: window.share.link, // 分享链接
                    imgUrl: window.share.imgUrl,
                    desc:  window.share.desc,
                    trigger: function (res) {
                        //	alert('用户点击分享到朋友圈');
                    },
                    success: function (res) {
                        //	alert('已分享');
                    },
                    cancel: function (res) {
                        //	alert('已取消');
                    },
                    fail: function (res) {
                        //	alert(JSON.stringify(res));
                    }
                });

            });
        });



});