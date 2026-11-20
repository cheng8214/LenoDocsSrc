
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
