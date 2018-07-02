var version = '2.2.7';
var sp = location.pathname.lastIndexOf('/');
var ep = location.pathname.lastIndexOf('.html');
var curPage = sp < ep ? location.pathname.slice(sp + 1, ep) : 'index';
var enVersion = location.href.indexOf('-en.html') != -1;

var activeClass = {};
var loc = {};
var forkWidth = 149;
curPage = curPage.replace('-en', '');
var isExample = false;
switch (curPage) {
    case 'index' :
        activeClass[curPage] = 'active';
        loc[curPage] = '.';
        loc.feature = './doc';
        loc.example = './doc';
        loc.doc = './doc';
        loc.about = './doc';
        loc.changelog = './doc';
        loc.option = './doc';
        loc.spreadsheet = './doc';
        loc.start = './doc';
        loc.img = './doc';
        break;
    case 'feature' :
    case 'example' :
    case 'doc' :
    case 'option' :
    case 'spreadsheet' :
    case 'about' :
    case 'changelog' :
    case 'start' :
        activeClass[curPage] = 'active';
        loc.index = '..';
        break;
    default :
        isExample = true;
        forkWidth = 60;
        activeClass['example'] = 'active';
        var extSub = location.href.indexOf('extension') != -1 ? '../' : '';
        loc.index = extSub + '../..';
        loc.feature = extSub + '../../doc';
        loc.example = extSub + '../../doc';
        loc.doc = extSub + '../../doc';
        loc.about = extSub + '../../doc';
        loc.changelog = extSub + '../../doc';
        loc.option = extSub + '../../doc';
        loc.spreadsheet = extSub + '../../doc';
        loc.start = extSub + '../../doc';
        loc.img = extSub + '../../doc';
        break;
}

// Those pages only exist in echarts-www project,
// but not in http://ecomfe.github.io/echarts/ and doc in echarts project.
if (location.href.indexOf('.baidu.com') < 0) {
    loc.option = 'http://echarts.baidu.com/doc';
    loc.spreadsheet = 'http://echarts.baidu.com/doc';
}


function back2Top() {
    $("body,html").animate({scrollTop:0},1000);
    return false;
}

function changeVersion() {
    if (!isExample) {
        window.location = curPage + (enVersion ? '' : '-en') + '.html'
    }
    else {
        window.location = curPage + '.html' + (enVersion ? '' : '#-en');
        if (enVersion) {
            window.location.hash = window.location.hash.replace('-en', '');
        }
        window.location.reload();
    }
}

var $footer = $('#footer');
if ($footer.length) {
    $footer[0].style.marginTop = '50px';
    $footer[0].innerHTML =
         '<div class="container">'
            + '<div class="row" style="padding-bottom:20px;">'
                + '<div class="col-md-3">'
                    + '<p>' + (enVersion ? 'Link' : 'ECharts团队出品') + '</p>'
                    + '<ul>'
                        + '<li><a href="http://tushuo.baidu.com/" target="_blank">Baidu 图说</a></li>'
                        + '<li><a href="' + (enVersion ? "http://ecomfe.github.io/echarts-x" : 'http://echarts.baidu.com/x/doc') + '" target="_blank">ECharts-X</a></li>'
                        + '<li><a href="http://ecomfe.github.io/zrender/index.html" target="_blank">ZRender</a></li>'
                        + '<li><a href="https://github.com/pissang/qtek" target="_blank">QTEK</a></li>'
                    + '</ul>'
                + '</div>'
                + '<div class="col-md-3">'
                    + '<p>' + (enVersion ? 'More' : '更多') + '</p>'
                    + '<ul>'
                        + '<li><a href="https://github.com/ecomfe/echarts/blob/master/LICENSE.txt" target="_blank">License</a></li>'
                        + '<li><a href="http://echarts.baidu.com/doc/changelog' + (enVersion ? '-en' : '') + '.html" target="_blank">Changelog</a></li>'
                        + '<li><a href="http://efe.baidu.com" target="_blank">Baidu EFE</a></li>'
                        + '<li><a href="http://www.oschina.net/p/echarts" target="_blank">' + (enVersion ? 'Open Source China' : '开源中国') + '</a></li>'
                    + '</ul>'
                + '</div>'
                + '<div class="col-md-3">'
                    + '<p>' + (enVersion ? 'Contact Us' : '联系我们') + '</p>'
                    + '<ul>'
                        + '<li><a href="mailto:echarts(a)baidu.com">echarts(a)baidu.com</a></li>'
                        + '<li><a href="https://github.com/ecomfe/echarts" target="_blank"> Github</a></li>'
                        + '<li><a href="http://weibo.com/echarts" target="_blank">Weibo</a></li>'
                    + '</ul>'
                + '</div>'
                + '<div class="col-md-3 flogo">'
                    + '<a href="javascript:void(0)" onclick="back2Top()" title="' + (enVersion ? 'Back to top' : '回到顶部') + '"><img src="'+ (loc.img || '.')+ '/asset/img/echarts-logo2.png" alt="ECharts"/></a>'
                + '</div>'
            + '</div>'
            + '<p class="pull-right"><a href="javascript:void(0)" onclick="back2Top()" >Back to top</a></p>'
            + '<p>&copy; 2015 <a href="http://www.baidu.com/" target="_blank">Baidu</a></p>'
        + '</div>';
}

if (document.location.href.indexOf('local') == -1) {
    var hm = document.createElement("script");
    hm.src = "//hm.baidu.com/hm.js?4bad1df23f079e0d12bdbef5e65b072f";
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(hm, s);
}

//function fixFork () {
//    var navMarginRight = 0;
//    var bodyWidth = document.body.offsetWidth;
//    var contnetWidth = $('#nav-wrap')[0].offsetWidth;
//    if (bodyWidth < 1440) {
//        navMarginRight = 150 - (bodyWidth - contnetWidth) / 2;
//    }
//    $('#nav')[0].style.marginRight = navMarginRight + 'px';
//    $('#fork-image')[0].style.width = (document.body.offsetWidth < 768 ? 1 : forkWidth) + 'px';
//};
////fixFork();
//$(window).on('resize', fixFork);