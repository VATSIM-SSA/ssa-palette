/* ===== VATSSA Brand Guidelines — shared behaviour ===== */
(function(){
  const root=document.documentElement;
  const getTheme=()=>root.getAttribute('data-theme');
  const roleFor=c=>c.getAttribute('data-role-'+getTheme())||c.dataset.role||'';

  /* ---- copy + toast ---- */
  let toast=document.querySelector('.toast');
  if(!toast){toast=document.createElement('div');toast.className='toast';document.body.appendChild(toast);}
  let tt;
  function copy(text,label){
    if(navigator.clipboard) navigator.clipboard.writeText(text);
    toast.textContent='Copied  '+(label||text);
    toast.classList.add('show');
    clearTimeout(tt); tt=setTimeout(()=>toast.classList.remove('show'),1300);
  }

  document.querySelectorAll('.chip').forEach(c=>{
    c.style.cursor='pointer';
    c.addEventListener('click',()=>{ if(c.dataset.hex) copy(c.dataset.hex); });
  });
  document.querySelectorAll('.envrow').forEach(r=>{
    r.addEventListener('click',()=>{ const h=r.querySelector('.hex'); if(h) copy(h.textContent.trim()); });
  });
  document.querySelectorAll('.typerow').forEach(r=>{
    r.addEventListener('click',()=>{ const n=r.querySelector('.ti'); if(n) copy(n.textContent.trim(),n.textContent.trim()+' (font)'); });
  });

  /* ---- interactive gradient sampler ---- */
  const TEAL=[1,151,176], GREEN=[123,215,88];
  const hx=n=>n.toString(16).padStart(2,'0').toUpperCase();
  const hexAt=t=>'#'+TEAL.map((a,i)=>hx(Math.round(a+(GREEN[i]-a)*t))).join('');
  document.querySelectorAll('.grad').forEach(g=>{
    const samp=document.createElement('div'); samp.className='gsamp';
    const tip=document.createElement('div');  tip.className='gtip';
    g.appendChild(samp); g.appendChild(tip);
    function at(e){
      const r=g.getBoundingClientRect();
      const x=Math.max(0,Math.min(1,((e.touches?e.touches[0].clientX:e.clientX)-r.left)/r.width));
      const hex=hexAt(x); g.dataset.samp=hex;
      samp.style.left=(x*100)+'%'; tip.style.left=(x*100)+'%'; tip.textContent=hex; g.classList.add('sampling');
    }
    g.addEventListener('mousemove',at);
    g.addEventListener('touchmove',at,{passive:true});
    g.addEventListener('mouseleave',()=>g.classList.remove('sampling'));
    g.addEventListener('click',()=>copy(g.dataset.samp||'#0197B0'));
  });

  /* ---- accordion: opening one section closes the others ---- */
  document.querySelectorAll('details.coll').forEach(d=>{
    d.addEventListener('toggle',()=>{
      if(d.open) d.parentElement.querySelectorAll(':scope > details.coll').forEach(o=>{ if(o!==d) o.open=false; });
    });
  });

  /* ---- theme ---- */
  function apply(t){
    root.setAttribute('data-theme',t);
    document.querySelectorAll('img[data-dark-src]').forEach(img=>{const v=img.getAttribute('data-'+t+'-src'); if(v) img.src=v;});
    document.querySelectorAll('.chip').forEach(c=>{const r=c.querySelector('.role');const v=roleFor(c);if(v&&r)r.textContent=v;});
    document.querySelectorAll('[data-dark]').forEach(el=>{
      const v=el.getAttribute('data-'+t); if(!v) return;
      if(el.classList.contains('sw')) el.style.background=v; else el.textContent=v;
    });
    document.querySelectorAll('.toggle').forEach(btn=>{
      const i=btn.querySelector('.tgIcon'), x=btn.querySelector('.tgTxt');
      if(i) i.textContent=t==='dark'?'☀':'☾';
      if(x) x.textContent=t==='dark'?'Light':'Dark';
    });
    localStorage.setItem('vatssa-theme',t);
  }
  apply(localStorage.getItem('vatssa-theme')||'dark');
  document.querySelectorAll('.toggle').forEach(btn=>btn.addEventListener('click',()=>apply(getTheme()==='dark'?'light':'dark')));
})();
