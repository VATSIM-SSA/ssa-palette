/* ===== VATSSA Brand Guidelines — shared behaviour ===== */
(function(){
  const root=document.documentElement;

  /* ===================== CONFIG ===================== */
  /* Home nav button style — change this one value:      */
  /* 'tint' | 'gradient' | 'accent' | 'outline' | 'solid' */
  const NAV_BUTTON_STYLE = 'tint';
  root.setAttribute('data-btn', NAV_BUTTON_STYLE);
  /* ================================================== */

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
  window.__copy=copy;

  document.querySelectorAll('.chip').forEach(c=>{
    c.style.cursor='pointer';
    c.addEventListener('click',()=>{ if(c.dataset.hex) copy(c.dataset.hex); });
  });
  document.querySelectorAll('.envrow').forEach(r=>{
    r.addEventListener('click',()=>{ const h=r.querySelector('.hex'); if(h) copy(h.textContent.trim()); });
  });
  document.querySelectorAll('.typerow').forEach(r=>{
    r.style.cursor='pointer';
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

  /* ---- smooth accordion (one open at a time) ---- */
  function anim(d,open){
    const body=d.querySelector('.cbody');
    if(!body){ d.open=open; return; }
    if(open){
      d.open=true; body.style.overflow='hidden';
      const h=body.scrollHeight; body.style.height='0px';
      requestAnimationFrame(()=>{ body.style.transition='height .32s ease'; body.style.height=h+'px'; });
      body.addEventListener('transitionend',function te(e){ if(e.propertyName!=='height')return;
        body.style.transition=''; body.style.height='auto'; body.style.overflow='visible'; body.removeEventListener('transitionend',te); });
    } else {
      const h=body.scrollHeight; body.style.overflow='hidden'; body.style.height=h+'px';
      requestAnimationFrame(()=>{ body.style.transition='height .28s ease'; body.style.height='0px'; });
      body.addEventListener('transitionend',function te(e){ if(e.propertyName!=='height')return;
        d.open=false; body.style.transition=''; body.style.height=''; body.removeEventListener('transitionend',te); });
    }
  }
  document.querySelectorAll('details.coll').forEach(d=>{
    const s=d.querySelector('summary'); if(!s) return;
    s.addEventListener('click',e=>{
      e.preventDefault();
      if(!d.open){
        d.parentElement.querySelectorAll(':scope > details.coll[open]').forEach(o=>{ if(o!==d) anim(o,false); });
        anim(d,true);
      } else anim(d,false);
    });
  });

  /* ---- email signature generator (applications page) ---- */
  const sgName=document.getElementById('sg-name');
  if(sgName){
    const ids=['name','role','email','web','cid'];
    const el={}; ids.forEach(k=>el[k]=document.getElementById('sg-'+k));
    const prev=document.getElementById('sgp');
    const dl=document.getElementById('sg-download');
    let logoData=null;
    fetch('logo_icon_fill.png').then(r=>r.blob()).then(b=>{const fr=new FileReader();fr.onload=()=>{logoData=fr.result;build();};fr.readAsDataURL(b);}).catch(()=>{});
    const esc=s=>(s+'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    const vals=()=>({name:el.name.value||'Name Surname',role:el.role.value||'Division Staff',email:el.email.value||'name@vatssa.org',web:el.web.value||'vatssa.org',cid:el.cid.value.trim()});
    function sig(v,logo){
      const cid=v.cid?(' · CID '+esc(v.cid)):'';
      return '<table style="border-collapse:collapse;font-family:Arial,Helvetica,sans-serif"><tr>'+
        '<td style="padding-right:14px;vertical-align:middle"><img src="'+logo+'" width="52" height="52" alt="VATSSA" style="display:block;border-radius:12px"></td>'+
        '<td style="vertical-align:middle;border-left:2px solid #0197B0;padding-left:14px">'+
        '<div style="font-weight:700;font-size:15px;color:#07262C">'+esc(v.name)+'</div>'+
        '<div style="font-size:12px;color:#0197B0;margin-top:2px">'+esc(v.role)+' · VATSSA</div>'+
        '<div style="font-size:11px;color:#5d6b6e;margin-top:3px">'+esc(v.email)+' · '+esc(v.web)+cid+'</div>'+
        '</td></tr></table>';
    }
    function build(){
      const v=vals();
      prev.innerHTML=sig(v,'logo_icon_fill.svg');
      const html='<!doctype html><meta charset="utf-8">\n'+sig(v,logoData||'logo_icon_fill.png');
      dl.href='data:text/html;charset=utf-8,'+encodeURIComponent(html); dl.download='vatssa-email-signature.html';
    }
    ids.forEach(k=>el[k].addEventListener('input',build));
    build();
    document.getElementById('sg-copy').addEventListener('click',()=>copy(sig(vals(),logoData||'logo_icon_fill.png'),'signature HTML'));
  }

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
