#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 LenoDocsSrc 下的 Markdown 转成可离线访问的静态 HTML 站。

布局（md 源与 html 成品都放在本仓库，**代码仓库不再带文档**）：
  D:/CLeno/LenoDocsSrc/*.md      ← md 源码（本脚本所在处）
  D:/CLeno/LenoDocsSrc/site/     ← HTML 成品（生成物，下次重跑整目录重建）

⚠ 要改文档请改 md；**不要**手改 site/ 下的 html（那是生成物，会被覆盖）。
  代码仓库里引用的路径形如 `LenoDocsSrc/site/<名字>.html`。

用法:  python D:/CLeno/LenoDocsSrc/build_html.py [输出目录]
依赖:  LenoDocsSrc/_build_vendor/markdown （隔离安装，不污染全局 Python）
"""
from __future__ import annotations
import re
import sys
import json
import shutil
from pathlib import Path

SRC = Path(__file__).resolve().parent
VENDOR = SRC / "_build_vendor"
if VENDOR.is_dir():
    sys.path.insert(0, str(VENDOR))
try:
    import markdown
except ImportError:
    sys.exit("缺少 markdown 库，请先运行: python -m pip install --target LenoDocsSrc/_build_vendor markdown")

# 默认输出：本仓库的 site/（md 与 html 同一个仓库，代码仓库不再放文档）；可用命令行参数覆盖
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SRC / "site"
ASSETS = OUT / "assets"
INDEX_MD = SRC / "INDEX.md"
IMAGES_SRC = SRC / "images"
SITE_TITLE = "Leno Docs"


def inline_md(s: str) -> str:
    """把行内 `code` 渲染成 <code>（用于面包屑 / 分类标题这类不经 markdown 的纯文本字段）"""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s or "")


# ============================================================ 页面模板
TOOLS = """<span class="tools">
  <button id="btn-theme" title="切换深浅主题">◐</button>
  <button id="btn-wide" title="切换阅读宽度">⇔</button>
  <button id="btn-fs-down" title="缩小字号">A−</button>
  <button id="btn-fs-up" title="放大字号">A+</button>
</span>"""

PAGE_TPL = """<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {site}</title>
<link rel="stylesheet" href="{base}assets/style.css">
<script charset="utf-8" src="{base}assets/search-index.js" defer></script>
<script charset="utf-8" src="{base}assets/app.js" defer></script>
</head><body data-doc="{doc}">
<header class="topbar">
  <a class="brand" href="{base}index.html">{site}</a>
  <div class="searchbox">
    <input id="q" type="search" placeholder="搜索全部文档（/ 聚焦）…" autocomplete="off" spellcheck="false">
    <div id="results" class="results"></div>
  </div>
  {tools}
  <span class="crumb">{crumb}</span>
</header>
{banner}
<div class="layout">
  <aside class="side"><div class="side-title">本页目录</div>{toc}</aside>
  <main class="content" id="top">{body}</main>
</div>
<nav class="pager">{prev}{next}</nav>
<a class="totop" href="#top" title="返回顶部">↑</a>
<div id="toast" class="toast"></div>
</body></html>
"""

HOME_TPL = """<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{site} · 文档门户</title>
<link rel="stylesheet" href="assets/style.css">
<script charset="utf-8" src="assets/search-index.js" defer></script>
<script charset="utf-8" src="assets/app.js" defer></script>
</head><body data-doc="">
<header class="topbar">
  <span class="brand">{site}</span>
  <div class="searchbox wide">
    <input id="q" type="search" placeholder="搜索 {n} 篇文档：语言特性 / 报错症状 / 模块 API / 排查记录…" autocomplete="off" spellcheck="false" autofocus>
    <div id="results" class="results"></div>
  </div>
  {tools}
  <span class="crumb">{n} 篇 · {total}</span>
</header>
<main class="home">
  <div class="hero">
    <h1>快速找到你要的那一条</h1>
    <p>输入关键词直接搜全文，结果按章节定位；按 <kbd>/</kbd> 随时聚焦搜索。也可以从下面的分类进去翻。</p>
  </div>
  {recent}
  {sections}
  <div class="footnote">由 <code>build_html.py</code> 从 <code>LenoDocsSrc/*.md</code> 生成 ·
    <a href="INDEX_raw.html">查看原始索引全文</a> · 标题右侧的 <code>#</code> 可复制直达链接<br>
    ⚠ 这里是**生成物**（<code>LenoDocsSrc/site/</code>）：要改文档请改上一层的 <code>*.md</code>，
    再跑一次 <code>python build_html.py</code>；手改本目录的 html 会在下次生成时被整目录覆盖</div>
</main>
<a class="totop" href="#top" title="返回顶部">↑</a>
<div id="toast" class="toast"></div>
</body></html>
"""


CSS = r"""
:root{
  --bg:#f7f8fa; --panel:#ffffff; --line:#e3e6ec; --ink:#1f2430; --muted:#646b7a;
  --accent:#2563eb; --accent-soft:#eaf0ff; --code-bg:#f2f4f8; --warn:#b42318;
  --warn-bg:#fff3f0; --ok:#0a7f43; --quote:#33405c; --row-alt:#fbfcfe;
  --fs:15px; --layout-max:1500px; --text-max:100ch; --mark:#ffe9a8; --mark-ink:#5b3d00;
}
:root[data-theme="dark"]{
  --bg:#141821; --panel:#1c212c; --line:#333b4d; --ink:#e5e9f2; --muted:#98a2b5;
  --accent:#6ea8ff; --accent-soft:#1f2c47; --code-bg:#232a38; --warn:#ff8f85;
  --warn-bg:#392225; --ok:#59d69a; --quote:#c7d1e8; --row-alt:#202633;
  --mark:#7a5c12; --mark-ink:#ffedb5;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-size:var(--fs);line-height:1.75;
     font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
kbd{background:var(--code-bg);border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;
    padding:0 5px;font:12px Consolas,monospace}

/* ---- 顶栏 + 搜索 + 工具 ---- */
.topbar{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:14px;
  padding:10px 22px;background:var(--panel);border-bottom:1px solid var(--line)}
.brand{font-weight:700;font-size:17px;white-space:nowrap;color:var(--ink)}
.brand:hover{text-decoration:none;color:var(--accent)}
.searchbox{position:relative;flex:1;max-width:620px;margin:0 auto}
.searchbox.wide{max-width:720px}
.searchbox input{width:100%;padding:9px 14px;border:1px solid var(--line);border-radius:8px;
  background:var(--bg);color:var(--ink);font:inherit;font-size:14px;outline:none}
.searchbox input:focus{border-color:var(--accent);background:var(--panel);box-shadow:0 0 0 3px var(--accent-soft)}
.tools{display:flex;gap:4px;flex:none}
.tools button{width:30px;height:30px;border:1px solid var(--line);border-radius:6px;
  background:var(--panel);color:var(--muted);cursor:pointer;font-size:13px;line-height:1;padding:0}
.tools button:hover{color:var(--accent);border-color:var(--accent);background:var(--accent-soft)}
.crumb{color:var(--muted);font-size:13px;white-space:nowrap;max-width:210px;overflow:hidden;text-overflow:ellipsis}
.results{display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;max-height:70vh;overflow:auto;
  background:var(--panel);border:1px solid var(--line);border-radius:10px;
  box-shadow:0 12px 40px rgba(20,30,60,.18);padding:6px}
.results.on{display:block}
.r-item{display:block;padding:9px 12px;border-radius:7px;color:var(--ink);line-height:1.5}
.r-item:hover,.r-item.sel{background:var(--accent-soft);text-decoration:none}
.r-title{font-weight:650;font-size:14px}
.r-title .cat{font-weight:400;color:var(--muted);font-size:12px;margin-left:8px}
.r-frag{color:var(--muted);font-size:13px;margin-top:2px}
.r-frag mark,.content mark{background:var(--mark);color:var(--mark-ink);border-radius:2px;padding:0 1px}
.r-empty{padding:16px;color:var(--muted);text-align:center;font-size:14px}
.r-more{padding:8px;color:var(--muted);font-size:12px;text-align:center;border-top:1px solid var(--line)}

/* ---- 文档页 ---- */
.banner{padding:10px 22px;background:var(--warn-bg);color:var(--warn);border-bottom:1px solid var(--line);
  font-size:13px;text-align:center}
.layout{display:flex;gap:28px;max-width:var(--layout-max);margin:0 auto;padding:26px 22px 60px}
.side{width:250px;flex:none;position:sticky;top:70px;align-self:flex-start;
  max-height:calc(100vh - 100px);overflow:auto;font-size:13px}
.side-title{font-weight:700;color:var(--muted);margin:0 0 8px 8px;letter-spacing:.5px}
.side ul{list-style:none;margin:0;padding-left:12px;border-left:1px solid var(--line)}
.side li{margin:1px 0}
.side a{display:block;padding:3px 8px;border-radius:5px;color:var(--muted)}
.side a:hover,.side a.active{background:var(--accent-soft);color:var(--accent);text-decoration:none}
.side .lv3 a{padding-left:18px;font-size:12.5px}
.content{flex:1;min-width:0;background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:30px 38px 60px;overflow:hidden}
.content h1,.content h2,.content h3,.content h4{line-height:1.35;scroll-margin-top:80px;position:relative}
.content h1{font-size:26px;margin:0 0 22px;padding-bottom:14px;border-bottom:2px solid var(--line)}
.content h2{font-size:20px;margin:34px 0 12px;padding-bottom:7px;border-bottom:1px solid var(--line)}
.content h3{font-size:17px;margin:24px 0 8px}
.content h4{font-size:15px;margin:18px 0 6px}
.anchor{opacity:0;margin-left:8px;font-size:.7em;font-weight:400;color:var(--accent);
  border:1px solid var(--line);border-radius:5px;padding:0 6px;cursor:pointer;background:var(--panel)}
h1:hover .anchor,h2:hover .anchor,h3:hover .anchor,h4:hover .anchor{opacity:1}
.content p,.content li{max-width:var(--text-max);font-size:var(--fs)}
.content blockquote{margin:14px 0;padding:10px 16px;border-left:4px solid var(--accent);
  background:var(--accent-soft);border-radius:0 6px 6px 0;color:var(--quote)}
.content blockquote p{margin:4px 0}
.content hr{border:0;border-top:1px solid var(--line);margin:26px 0}
.content code{background:var(--code-bg);padding:1px 5px;border-radius:4px;font-size:.92em;
  font-family:"Cascadia Code",Consolas,"Courier New",monospace}
.content pre{background:var(--code-bg);border:1px solid var(--line);border-radius:8px;
  padding:14px 16px;overflow:auto;line-height:1.55;position:relative}
.content pre code{background:none;padding:0;font-size:13px}
.copy-btn{position:absolute;top:8px;right:8px;opacity:0;transition:opacity .15s;
  border:1px solid var(--line);border-radius:5px;background:var(--panel);color:var(--muted);
  font-size:11px;padding:3px 8px;cursor:pointer}
pre:hover .copy-btn{opacity:1}
.copy-btn:hover{color:var(--accent);border-color:var(--accent)}
.content table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;display:block;overflow:auto}
.content th,.content td{border:1px solid var(--line);padding:7px 11px;text-align:left;vertical-align:top}
.content th{background:var(--bg);font-weight:650;position:sticky;top:0}
.content tr:nth-child(even) td{background:var(--row-alt)}
.content img{max-width:100%}
.pager{max-width:var(--layout-max);margin:0 auto;padding:0 22px 60px;display:flex;gap:16px;justify-content:space-between}
.pager a{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 16px;font-size:14px}
.totop{position:fixed;right:24px;bottom:24px;width:38px;height:38px;border-radius:50%;
  background:var(--panel);border:1px solid var(--line);box-shadow:0 4px 14px rgba(0,0,0,.12);
  display:grid;place-items:center;font-size:18px;color:var(--ink)}
.totop:hover{text-decoration:none;background:var(--accent-soft)}
.toast{position:fixed;left:50%;bottom:32px;transform:translate(-50%,20px);opacity:0;pointer-events:none;
  background:var(--ink);color:var(--panel);padding:8px 18px;border-radius:7px;font-size:13px;
  transition:opacity .2s,transform .2s;z-index:100}
.toast.on{opacity:.95;transform:translate(-50%,0)}

/* ---- 门户页 ---- */
.home{max-width:1240px;margin:0 auto;padding:34px 22px 80px}
.hero h1{font-size:26px;margin:0 0 6px}
.hero p{color:var(--muted);margin:0 0 24px}
.cat{margin-bottom:34px}
.cat h2{font-size:19px;margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.cat h2 .n{color:var(--muted);font-size:13px;font-weight:400;margin-left:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:9px;
  padding:13px 15px;color:var(--ink);transition:border-color .15s,transform .15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px);text-decoration:none}
.card .f{font-weight:650;font-size:14px;word-break:break-all}
.card .d{color:var(--muted);font-size:13px;margin-top:4px;line-height:1.55}
.badge{display:inline-block;font-size:11px;padding:1px 6px;border-radius:10px;margin-left:6px;
  background:var(--code-bg);color:var(--muted);vertical-align:1px}
.badge.arch{background:var(--warn-bg);color:var(--warn)}
.badge.old{background:#fff7e6;color:#a35b00}
.recent{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:30px}
.recent h2{font-size:15px;margin:0 0 10px;color:var(--muted)}
.recent .grid{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.recent .card{padding:9px 12px}
.recent .d{display:none}
.footnote{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
@media(max-width:900px){.side{display:none}.content{padding:20px}.topbar{gap:8px;padding:8px 12px}
  .crumb{display:none}.tools button{width:26px;height:26px}}
@media print{.topbar,.side,.pager,.totop,.toast,.copy-btn,.anchor{display:none}
  .content{border:0;padding:0}.layout{display:block;padding:0}}
"""

APP_JS = r"""
(function(){
  var LS='lenodocs_';
  function get(k,d){try{var v=localStorage.getItem(LS+k);return v===null?d:v}catch(e){return d}}
  function put(k,v){try{localStorage.setItem(LS+k,String(v))}catch(e){}}
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function reEsc(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
  function base(){return /\/archive\//.test(location.pathname)?'../':''}
  function toast(msg){
    var el=document.getElementById('toast'); if(!el)return;
    el.textContent=msg; el.className='toast on';
    clearTimeout(toast._t); toast._t=setTimeout(function(){el.className='toast'},1400);
  }
  function copyText(text,okMsg){
    function done(){toast(okMsg||'已复制')}
    if(navigator.clipboard&&window.isSecureContext){
      navigator.clipboard.writeText(text).then(done,fallback);
    }else fallback();
    function fallback(){
      var ta=document.createElement('textarea');ta.value=text;
      ta.style.cssText='position:fixed;left:-9999px;top:0';document.body.appendChild(ta);
      ta.select();try{document.execCommand('copy');done()}catch(e){toast('复制失败，请手动选择')}
      document.body.removeChild(ta);
    }
  }

  /* ---- 主题 / 字号 / 宽度 ---- */
  var root=document.documentElement;
  root.dataset.theme=get('theme','light');
  root.style.setProperty('--fs',get('fs','15')+'px');
  root.style.setProperty('--layout-max',get('wide','1')==='1'?'1500px':'1040px');
  root.style.setProperty('--text-max',get('wide','1')==='1'?'100ch':'70ch');
  var bt=document.getElementById('btn-theme'),bw=document.getElementById('btn-wide');
  if(bt){bt.title='当前：'+(root.dataset.theme==='dark'?'深色':'浅色')+'（点击切换）';
    bt.onclick=function(){
      root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';
      put('theme',root.dataset.theme);bt.title='当前：'+(root.dataset.theme==='dark'?'深色':'浅色')+'（点击切换）';
    }}
  if(bw){bw.onclick=function(){
      var wide=get('wide','1')!=='1';put('wide',wide?'1':'0');
      root.style.setProperty('--layout-max',wide?'1500px':'1040px');
      root.style.setProperty('--text-max',wide?'100ch':'70ch');
      toast(wide?'宽屏阅读':'专注宽度');
    }}
  var fd=document.getElementById('btn-fs-down'),fu=document.getElementById('btn-fs-up');
  function setFs(v){root.style.setProperty('--fs',v+'px');put('fs',v);toast('字号 '+v+'px')}
  if(fd)fd.onclick=function(){setFs(Math.max(12,parseInt(get('fs','15'),10)-1))};
  if(fu)fu.onclick=function(){setFs(Math.min(22,parseInt(get('fs','15'),10)+1))};

  /* ---- 代码复制 / 标题锚点 ---- */
  document.querySelectorAll('pre').forEach(function(pre){
    var b=document.createElement('button');b.className='copy-btn';b.type='button';b.textContent='复制';
    b.onclick=function(){copyText(pre.innerText,'代码已复制')};
    pre.appendChild(b);
  });
  document.querySelectorAll('.content h2[id],.content h3[id],.content h4[id]').forEach(function(h){
    var a=document.createElement('button');a.className='anchor';a.type='button';a.textContent='#';
    a.title='复制本节直达链接';
    a.onclick=function(){copyText(location.href.split('#')[0]+'#'+h.id,'直达链接已复制')};
    h.appendChild(a);
  });

  /* ---- 最近访问 ---- */
  var doc=document.body.getAttribute('data-doc');
  if(doc){
    var list;try{list=JSON.parse(get('recent','[]'))}catch(e){list=[]}
    list=[doc].concat(list.filter(function(x){return x&&x!==doc})).slice(0,12);
    put('recent',JSON.stringify(list));
  }
  var recentBox=document.getElementById('recent');
  if(recentBox){
    var rl;try{rl=JSON.parse(get('recent','[]'))}catch(e){rl=[]}
    if(rl.length){
      var byName={};
      if(typeof SEARCH_DOCS!=='undefined')SEARCH_DOCS.forEach(function(d){byName[d.f]=d});
      var html='<div class="grid">'+rl.map(function(f){
        var d=byName[f];var name=d?d.t:f.replace(/\.html$/,'');
        return '<a class="card" href="'+esc(f)+'"><div class="f">'+esc(name)+'</div></a>';
      }).join('')+'</div>';
      recentBox.innerHTML='<h2>最近访问</h2>'+html;
    }else recentBox.style.display='none';
  }

  /* ---- 搜索 ---- */
  var q=document.getElementById('q'), box=document.getElementById('results');
  if(!q||!box||typeof SEARCH_DOCS==='undefined')return;
  var timer=null, items=[];
  function mark(s,terms){
    var out=esc(s);
    try{out=out.replace(new RegExp('('+terms.map(reEsc).join('|')+')','gi'),'<mark>$1</mark>')}catch(e){}
    return out;
  }
  function render(){
    var raw=q.value.trim().toLowerCase();
    if(!raw){box.className='results';box.innerHTML='';items=[];return}
    var terms=raw.split(/\s+/).filter(Boolean),hits=[];
    for(var i=0;i<SEARCH_DOCS.length;i++){
      var d=SEARCH_DOCS[i],best=null;
      for(var j=0;j<d.s.length;j++){
        var s=d.s[j],hay=(s.h+' '+s.x).toLowerCase(),first=-1,ok=true;
        for(var k=0;k<terms.length;k++){
          var p=hay.indexOf(terms[k]);if(p<0){ok=false;break}
          if(first<0||p<first)first=p;
        }
        if(ok){var a=Math.max(0,first-55),b=Math.min(s.x.length,first+130);
          best={s:s,frag:(a>0?'…':'')+s.x.slice(a,b)+(b<s.x.length?'…':'')};break}
      }
      if(best){hits.push({d:d,best:best,score:(best.s.h.toLowerCase().indexOf(terms[0])>=0?0:1)});
        if(hits.length>=60)break}
    }
    hits.sort(function(a,b){return a.score-b.score});
    box.innerHTML=hits.length?hits.map(function(h){
      var anchor=h.best.s.a?'#'+h.best.s.a:'';
      return '<a class="r-item" href="'+esc(base()+h.d.f+anchor)+'">'+
        '<div class="r-title">'+mark(h.d.t,terms)+'<span class="cat">'+esc(h.d.c)+
        (h.d.a?' · 已归档':'')+'</span></div>'+
        (h.best.s.h&&h.best.s.h!=='开头'?'<div class="r-frag">§ '+esc(h.best.s.h)+'</div>':'')+
        '<div class="r-frag">'+mark(h.best.frag,terms)+'</div></a>';
    }).join('')+(hits.length>=60?'<div class="r-more">仅显示前 60 条，继续输入以缩小范围</div>':'')
      :'<div class="r-empty">没有命中，换个词试试</div>';
    box.className='results on';items=Array.prototype.slice.call(box.querySelectorAll('.r-item'));
  }
  q.addEventListener('input',function(){clearTimeout(timer);timer=setTimeout(render,120)});
  q.addEventListener('keydown',function(e){
    if(e.key==='Escape'){q.value='';box.className='results';items=[];q.blur();return}
    if(!items.length)return;
    var cur=items.indexOf(document.activeElement);
    if(e.key==='ArrowDown'){e.preventDefault();items[(cur+1)%items.length].focus()}
    else if(e.key==='ArrowUp'){e.preventDefault();items[(cur-1+items.length)%items.length].focus()}
  });
  document.addEventListener('keydown',function(e){
    var tag=(e.target.tagName||'').toLowerCase();
    if(e.key==='/'&&tag!=='input'&&tag!=='textarea'){e.preventDefault();q.focus();q.select()}
    if(e.key==='Escape'&&document.activeElement!==q){box.className='results'}
  });
  document.addEventListener('click',function(e){
    if(!e.target.closest('.searchbox'))box.className='results';
  });
  /* 侧边目录随滚动高亮当前小节 */
  var links=Array.prototype.slice.call(document.querySelectorAll('.side a[href^="#"]'));
  if(links.length&&typeof IntersectionObserver!=='undefined'){
    var obs=new IntersectionObserver(function(es){
      es.forEach(function(en){if(en.isIntersecting){
        links.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+en.target.id)});
      }})
    },{rootMargin:'-70px 0px -75% 0px'});
    links.forEach(function(a){var el=document.getElementById(a.getAttribute('href').slice(1));if(el)obs.observe(el)});
  }
  if(q.value)render();
})();
"""


# ============================================================ 工具函数
def flatten_tokens(tokens, out):
    for t in tokens:
        out.append(t)
        flatten_tokens(t.get("children", []), out)
    return out


def lift_blockquote_fences(text):
    """Python-Markdown 的 fenced_code 不认引用块里的 ``` —— 会被当裸 HTML 解析。
    把 `> ```leno ... > ```` 整块提升为顶层围栏，保证代码内容被正确转义。"""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        m = re.match(r"^\s*>\s*(```+)(.*)$", lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        fence = m.group(1)
        out.append(m.group(0).lstrip("> "))
        i += 1
        closed = False
        while i < len(lines):
            cur = lines[i]
            if re.match(r"^\s*>\s*```+\s*$", cur) or re.match(r"^\s*```+\s*$", cur):
                out.append(fence); i += 1; closed = True; break
            out.append(re.sub(r"^\s*>\s?", "", cur))
            i += 1
        if not closed:
            out.append(fence)
    return "\n".join(out)


def fix_links(s):
    """只改本地 .md 链接；外链 / 锚点 / mailto 原样保留。"""
    def repl(m):
        u = m.group(1)
        if re.match(r"^(?:https?:|mailto:|javascript:|data:|#)", u, re.I):
            return m.group(0)
        if u.startswith("../docs/"):
            u = u[len("../docs/"):]
        elif u.startswith("../"):
            u = "../" + u
        if "build/leno_module/" not in u:
            u = re.sub(r"\.md(?=$|#)", ".html", u)
        return 'href="' + u + '"'
    return re.sub(r'href="([^"]*)"', repl, s)


def strip_md(s):
    s = re.sub(r"```[^\n]*\n.*?```", " ", s, flags=re.S)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"^\s*\|[\s:\-|]+\|\s*$", " ", s, flags=re.M)
    s = re.sub(r"[|*>_#]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def split_sections(text, toc):
    lines = text.split("\n")
    idmap = {t["name"]: t["id"] for t in toc if t["level"] in (2, 3)}
    marks = [(0, "开头", "")]
    for i, ln in enumerate(lines):
        m = re.match(r"^#{2,3}\s+(.*?)\s*$", ln)
        if m:
            title = strip_md(m.group(1))
            marks.append((i, title, idmap.get(title, "")))
    secs = []
    for k, (i, title, aid) in enumerate(marks):
        j = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
        chunk = "\n".join(lines[i + 1:j] if k else lines[i:j])
        x = strip_md(chunk)
        if x:
            secs.append({"h": title, "a": aid, "x": x})
    return secs


def toc_html(toc):
    items = [t for t in toc if t["level"] in (2, 3)]
    if not items:
        return '<div class="side-title">（无小节标题）</div>'
    out, depth = ["<ul>"], 0
    for t in items:
        lv = 2 if t["level"] == 2 else 3
        if lv == 3 and depth == 0:
            out.append('<ul class="lv3">'); depth = 1
        elif lv == 2 and depth:
            out.append("</ul>"); depth = 0
        title = re.sub(r"[`*]", "", t["name"])
        out.append('<li><a href="#' + t["id"] + '">' + title + "</a></li>")
    if depth:
        out.append("</ul>")
    out.append("</ul>")
    return "".join(out)


def parse_index():
    txt = INDEX_MD.read_text(encoding="utf-8")
    cats, cur = [], None
    for line in txt.split("\n"):
        m = re.match(r"^##\s+([一二三四五六七八])、\s*(.+?)\s*$", line)
        if m:
            cur = {"name": m.group(1) + "、" + m.group(2), "items": []}
            cats.append(cur)
            continue
        if not cur or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        m = re.match(r"\[([^\]]+)\]\(([^)]+?\.md)(?:#[^)]*)?\)", cells[0])
        if m:
            cur["items"].append({
                "name": m.group(1).strip(), "file": m.group(2).strip(),
                "desc": cells[1], "status": cells[2] if len(cells) > 2 else "",
            })
    return cats


def status_badge(s):
    if not s:
        return ""
    cls = "old" if ("归档" in s or "过时" in s or "已废" in s) else ""
    return '<span class="badge ' + cls + '">' + s.replace("|", "") + "</span>"


# ============================================================ 主流程
def main():
    cats = parse_index()
    spots = {}
    for ci, c in enumerate(cats):
        for ii, it in enumerate(c["items"]):
            spots.setdefault(it["file"], []).append((ci, ii))
    for places in spots.values():
        if len(places) > 1:
            arch = [x for x in places if "归档" in cats[x[0]]["name"]]
            keep = arch[0] if arch else places[0]
            for ci, ii in places:
                if (ci, ii) != keep:
                    cats[ci]["items"][ii] = None
    for c in cats:
        c["items"] = [it for it in c["items"] if it]
    # README.md 是**源仓库自述**（说明这个仓库是什么、怎么生成），不是文档页 ⇒ 排除
    registered = {it["file"] for c in cats for it in c["items"]} | {"INDEX.md", "README.md"}

    all_md = sorted(
        [p for p in SRC.rglob("*.md")
         if "_site" not in p.parts and "_build_vendor" not in p.parts and p.name != "README.md"],
        key=lambda p: (p.relative_to(SRC).as_posix().lower()),
    )
    files = [p for p in all_md if p != INDEX_MD]

    others = [p for p in files if p.relative_to(SRC).as_posix() not in registered]
    if others:
        cats.append({
            "name": "九、索引未收录（近期新增）",
            "items": [{"name": p.stem, "file": p.relative_to(SRC).as_posix(),
                       "desc": "INDEX.md 最后核对于 2026-10-02，这篇是之后新增或未登记的",
                       "status": ""} for p in others],
        })

    ordered, cat_of, seen = [], {}, set()
    for c in cats:
        for it in c["items"]:
            rel = it["file"]
            if rel in seen or not (SRC / rel).exists():
                continue
            seen.add(rel)
            ordered.append(rel)
            cat_of[rel] = c["name"]

    if OUT.exists():
        shutil.rmtree(OUT)
    ASSETS.mkdir(parents=True)

    index_docs = []
    for pos, rel in enumerate(ordered):
        path = SRC / rel
        text = lift_blockquote_fences(path.read_text(encoding="utf-8"))
        md = markdown.Markdown(
            extensions=["markdown.extensions.tables", "markdown.extensions.fenced_code",
                     "markdown.extensions.toc", "markdown.extensions.sane_lists"], output_format="html5")
        body = fix_links(md.convert(text))
        toc = flatten_tokens(getattr(md, "toc_tokens", []), [])

        archived = "archive/" in rel.replace("\\", "/")
        cat = cat_of.get(rel, "")
        base = "../" if archived else ""
        title = re.sub(r"^#\s+", "", next((l for l in text.split("\n") if l.startswith("# ")), path.stem))
        title = re.sub(r"[`*]", "", title).strip()

        banner = ""
        if archived:
            banner = ('<div class="banner">⛔ 已归档文档 —— 描述的实现已不在当前代码中，'
                      '仅供考古；现行状态请看 <a href="' + base + 'index.html">索引</a>。</div>')
        elif "历史" in text[:1500] or "过时" in text[:1500]:
            banner = '<div class="banner">🟡 本文档部分内容已标记「历史 / 局部过时」，引用前请先核对源码。</div>'

        prev_link = ('<a href="' + base + ordered[pos - 1].replace(".md", ".html") + '">← 上一篇</a>'
                     if pos > 0 else "<span></span>")
        next_link = ('<a href="' + base + ordered[pos + 1].replace(".md", ".html") + '">下一篇 →</a>'
                     if pos < len(ordered) - 1 else "<span></span>")

        out_path = OUT / rel.replace(".md", ".html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(PAGE_TPL.format(
            title=title, site=SITE_TITLE, base=base, crumb=inline_md(cat), tools=TOOLS,
            doc=rel.replace(".md", ".html").replace("\\", "/"),
            banner=banner, toc=toc_html(toc), body=body, prev=prev_link, next=next_link,
        ), encoding="utf-8", newline="\n")

        index_docs.append({
            "f": rel.replace(".md", ".html").replace("\\", "/"),
            "t": title, "c": cat, "a": 1 if archived else 0,
            "s": split_sections(text, toc),
        })

    md = markdown.Markdown(extensions=["markdown.extensions.tables", "markdown.extensions.fenced_code",
                     "markdown.extensions.toc", "markdown.extensions.sane_lists"], output_format="html5")
    # ⚠ 必须叫 INDEX_raw.html，不能叫 INDEX.html：Windows 文件名**不区分大小写**，
    #   `index.html`（门户）与 `INDEX.html`（原始索引）会互相覆盖 —— 实测只活下来一个，
    #   而且"查看原始索引全文"链接指回自己（死循环）。改成不同的基名才两地都对 ✓
    (OUT / "INDEX_raw.html").write_text(PAGE_TPL.format(
        title="INDEX 原文 · 文档索引", site=SITE_TITLE, base="", crumb="索引原文", tools=TOOLS,
        doc="INDEX_raw.html", banner="",
        toc=toc_html(flatten_tokens(getattr(md, "toc_tokens", []), [])),
        body=fix_links(md.convert(INDEX_MD.read_text(encoding="utf-8"))),
        prev='<a href="index.html">← 返回门户</a>', next="<span></span>",
    ), encoding="utf-8", newline="\n")

    total_bytes = sum(p.stat().st_size for p in files)
    sections = []
    for c in cats:
        items = [it for it in c["items"] if (SRC / it["file"]).exists()]
        if not items:
            continue
        cards = []
        for it in items:
            is_arch = "archive/" in it["file"].replace("\\", "/")
            badge = '<span class="badge arch">归档</span>' if is_arch else status_badge(it["status"])
            href = it["file"].replace(".md", ".html").replace("\\", "/")
            desc = re.sub(r"[`*]", "", it["desc"])
            cards.append('<a class="card" href="' + href + '"><div class="f">' +
                         it["name"] + badge + '</div><div class="d">' + desc + "</div></a>")
        # 分类标题里的 `code` 也要渲染；括号里的"N 篇"是 md 里手写的旧数字，
        #   与真实条数常年不一致（实测 18 vs 19）⇒ 生成时**去掉**，只信下面 span.n 的真实计数 ✓
        sec_name = re.sub(r"（\s*\d+\s*篇\s*）", "", c["name"])
        sections.append('<section class="cat"><h2>' + inline_md(sec_name) +
                        '<span class="n">' + str(len(items)) + ' 篇</span></h2><div class="grid">' +
                        "".join(cards) + "</div></section>")

    (OUT / "index.html").write_text(HOME_TPL.format(
        site=SITE_TITLE, n=len(index_docs), tools=TOOLS,
        total="{:.1f} MB 原文".format(total_bytes / 1024 / 1024),
        recent='<div class="recent" id="recent"></div>', sections="\n".join(sections),
    ), encoding="utf-8", newline="\n")

    (ASSETS / "style.css").write_text(CSS, encoding="utf-8", newline="\n")
    (ASSETS / "app.js").write_text(APP_JS, encoding="utf-8", newline="\n")
    (ASSETS / "search-index.js").write_text(
        "/* 由 build_html.py 生成；用 script src 加载以绕开 file:// 下 fetch 的 CORS 限制 */\n"
        "var SEARCH_DOCS=" + json.dumps(index_docs, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8", newline="\n",
    )

    if IMAGES_SRC.is_dir():
        shutil.copytree(IMAGES_SRC, OUT / "images", dirs_exist_ok=True)

    print("生成完成: {}".format(OUT))
    print("文档 {} 篇 | 分类 {} 组 | 搜索索引 {:.0f} KB".format(
        len(index_docs), len(cats), (ASSETS / "search-index.js").stat().st_size / 1024))
    print("入口: {}".format(OUT / "index.html"))


if __name__ == "__main__":
    main()
