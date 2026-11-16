/* Rodovias em Dados. Visualizações acessíveis e progressivas, sem dependências externas.
   Os dados são estatísticas agregadas produzidas pelo pipeline Python, não registros individuais. */
(() => {
  'use strict';
  const input = document.querySelector('#analysis-data');
  if (!input) return;
  let data;
  try { data = JSON.parse(input.textContent); } catch (_) { return; }
  const nf = new Intl.NumberFormat('pt-BR');
  const pf = (v) => `${new Intl.NumberFormat('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(v)}%`;
  const monthNames = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  const SVGNS = 'http://www.w3.org/2000/svg';
  const color = {sage: '#3F769C',forest: '#203C36',ochre: '#BA704C',line: '#DFE2DE',muted: '#54665E',pale: '#F0F2EF',blue: '#3F769C',copper: '#BA704C',gold: '#AE8540',purple: '#75668F'};
  const metricPalette = {accidents: color.blue, deaths: color.copper, injured: color.gold};
  const metricNames = {accidents:'Sinistros',deaths:'Mortes',injured:'Feridos'};
  const $ = (s) => document.querySelector(s);
  const svgEl=(tag,attrs={})=>{
    const node=document.createElementNS(SVGNS,tag);
    Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,String(value)));
    return node;
  };
  const clear = (node) => { while(node.firstChild)node.removeChild(node.firstChild); };
  const addText=(root,x,y,text,attrs={})=>{
    const t=svgEl('text',{x,y,'font-family':'Inter, system-ui, sans-serif','font-size':'13',fill:color.muted,...attrs});
    t.textContent=text;root.appendChild(t);return t;
  };
  const activate=(attribute,value)=>{
    document.querySelectorAll(`[${attribute}]`).forEach(el=>{
      const active=el.getAttribute(attribute)===value;
      el.classList.toggle('is-active',active);
      el.setAttribute('aria-pressed',String(active));
    });
  };
  function writeTable(selector,columns,rows){
    const root=$(selector);if(!root)return;
    clear(root);const table=document.createElement('table');table.className='data-table';
    const thead=document.createElement('thead');const tr=document.createElement('tr');
    columns.forEach(([header])=>{const th=document.createElement('th');th.scope='col';th.textContent=header;tr.appendChild(th);});
    thead.appendChild(tr);table.appendChild(thead);
    const tbody=document.createElement('tbody');
    rows.forEach(row=>{const tr=document.createElement('tr');columns.forEach(([,key,format])=>{const td=document.createElement('td');td.textContent=format?format(row[key]):String(row[key]??'');tr.appendChild(td);});tbody.appendChild(tr);});
    table.appendChild(tbody);root.appendChild(table);
  }
  function plotTime(){
    const svgRoot=$('#chart-time');if(!svgRoot)return;
    const metric=document.querySelector('[data-time-metric].is-active')?.getAttribute('data-time-metric')||'accidents';
    const mode=document.querySelector('[data-time-mode].is-active')?.getAttribute('data-time-mode')||'annual';
    const rows=mode==='annual'?data.annual:data.monthly;
    const name=metricNames[metric];
    const W=900,H=340,P={l:66,r:18,t:27,b:53};
    const width=W-P.l-P.r,height=H-P.t-P.b;
    const maxValue=Math.max(1,...rows.map(row=>row[metric]));
    const maxTick=Math.ceil(maxValue/(mode==='annual'?10000:1000))*(mode==='annual'?10000:1000);
    const posX=(i)=>P.l+((mode==='annual'?(i+0.5)/rows.length:(rows.length===1?0.5:i/(rows.length-1)))*width);
    const posY=(val)=>P.t+height-(val/maxTick)*height;
    const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':`${name} por ${mode==='annual'?'ano':'mês'} em 2023 a 2025. Consulte a tabela abaixo para valores exatos.`});
    for(let i=0;i<=4;i++){
      const val=Math.round(maxTick*i/4),y=posY(val);
      svg.appendChild(svgEl('line',{x1:P.l,x2:W-P.r,y1:y,y2:y,stroke:color.line,'stroke-width':1}));
      addText(svg,P.l-13,y+4,nf.format(val),{'text-anchor':'end','font-size':12});
    }
    const labels=rows.map(r=>mode==='annual'?String(r.year):`${monthNames[r.month-1]}/${String(r.year).slice(2)}`);
    if(mode==='annual'){
      rows.forEach((r,i)=>{
        const x=posX(i);const y=posY(r[metric]);
        svg.appendChild(svgEl('rect',{x:x-52,y,width:104,height:Math.max(0,height+P.t-y),rx:8,fill:metricPalette[metric]}));
        addText(svg,x,Math.max(y-14,P.t+6),nf.format(r[metric]),{'text-anchor':'middle','font-size':16,'font-weight':700,fill:color.forest});
        addText(svg,x,H-18,labels[i],{'text-anchor':'middle','font-size':15,fill:color.forest});
      });
    }else{
      const points=rows.map((r,i)=>`${posX(i).toFixed(2)},${posY(r[metric]).toFixed(2)}`).join(' ');
      const areaPath=`M ${posX(0)} ${P.t+height} L ${points.replaceAll(' ', ' L ')} L ${posX(rows.length-1)} ${P.t+height} Z`;
      svg.appendChild(svgEl('path',{d:areaPath,fill:(metric==='deaths'?'#BA704C18':metric==='injured'?'#AE854020':'#3F769C16')}));
      svg.appendChild(svgEl('polyline',{points,fill:'none',stroke:metricPalette[metric],'stroke-width':3.2,'stroke-linecap':'round','stroke-linejoin':'round'}));
      rows.forEach((r,i)=>{
        const x=posX(i),y=posY(r[metric]);
        const point=svgEl('circle',{cx:x,cy:y,r:5.5,fill:metricPalette[metric],stroke:'#FFFEFA','stroke-width':1.8,tabindex:0,role:'img','aria-label':`${labels[i]}: ${nf.format(r[metric])} ${name.toLowerCase()}`});
        const title=svgEl('title');title.textContent=`${labels[i]} · ${nf.format(r[metric])} ${name.toLowerCase()}`;point.appendChild(title);
        const announce=()=>{$('#time-announcement').textContent=title.textContent;};point.addEventListener('focus',announce);point.addEventListener('click',announce);
        svg.appendChild(point);
        if(i===0||i===rows.length-1||i%6===0){
          addText(svg,x,H-18,labels[i],{'text-anchor':'middle','font-size':12,fill:color.forest});
        }
      });
    }
    clear(svgRoot);svgRoot.appendChild(svg);
    const columns=[['Período','label'],[name,metric,nf.format]];
    writeTable('#table-time',columns,rows.map((r,i)=>({...r,label:labels[i]})));
  }

  function plotBars(rootSelector,tableSelector,rows,opts={}){
    const root=$(rootSelector);if(!root)return;
    clear(root);
    const list=document.createElement('div');list.className='bar-chart';
    const shown=rows.slice(0,opts.limit||8);
    const column=opts.column||'accidents';
    const max=Math.max(1,...shown.map(x=>x[column]));
    shown.forEach((row,index)=>{
      const outer=document.createElement('div');outer.className='bar-chart__row';
      const header=document.createElement('div');header.className='bar-chart__header';
      const label=document.createElement('span');label.textContent=row.name;
      const number=document.createElement('strong');number.textContent=opts.percent?pf(row[column]):nf.format(row[column]);
      header.append(label,number);
      const track=document.createElement('div');track.className='bar-chart__track';
      const bar=document.createElement('div');bar.className='bar-chart__bar';
      const width=(row[column]/max*100).toFixed(2)+'%';bar.style.width=width;
      if(opts.ochre)bar.classList.add('bar-chart__bar--ochre');
      if(opts.tone)bar.style.backgroundColor=opts.tone;
      if(opts.multi)bar.style.backgroundColor=['#3F769C','#75668F','#BA704C','#AE8540','#508B80','#6B7F99','#8C7989'][index%7];
      track.appendChild(bar);
      outer.setAttribute('title',`${row.name}: ${number.textContent}${row.accidents?` (total de ${nf.format(row.accidents)} ocorrências)`:''}`);
      outer.append(header,track);list.appendChild(outer);
    });
    root.appendChild(list);
    const columns=opts.percent?[
      ['Categoria','name'],['Ocorrências','accidents',nf.format],['Com morte','fatal_accidents',nf.format],['Percentual','fatal_rate',pf]
    ]:[['Categoria','name'],['Ocorrências','accidents',nf.format],['Mortes','deaths',nf.format],['Feridos','injured',nf.format]];
    writeTable(tableSelector,columns,shown);
  }
  const type=()=>{
    const mode=document.querySelector('[data-type-mode].is-active')?.dataset.typeMode||'top_types_2025';
    plotBars('#chart-types','#table-types',data[mode],{limit:7,multi:true});
  };
  const severity=()=>{
    const mode=document.querySelector('[data-severity-mode].is-active')?.dataset.severityMode||'tipo_pista';
    const rows=data.severity_2025[mode].slice().sort((a,b)=>b.fatal_rate-a.fatal_rate);
    plotBars('#chart-severity','#table-severity',rows,{column:'fatal_rate',percent:true,ochre:true,tone:'#BA704C',limit:10});
  };
  const geo=()=>{
    const mode=document.querySelector('[data-geo-mode].is-active')?.dataset.geoMode||'top_states_2025';
    plotBars('#chart-geo','#table-geo',data[mode],{limit:9,tone:'#75668F'});
  };
  for(const [selector,cb] of [['data-time-metric',plotTime],['data-time-mode',plotTime],['data-type-mode',type],['data-severity-mode',severity],['data-geo-mode',geo]]){
    document.querySelectorAll(`[${selector}]`).forEach(button=>button.addEventListener('click',()=>{
      activate(selector,button.getAttribute(selector));cb();
    }));
  }
  plotTime();type();severity();geo();
  // Leitura principal independe de animações; a barra de progresso é apenas auxiliar.
  const progress=$('#reading-progress');
  if(progress){
    let scheduled=false;
    const update=()=>{
      const distance=document.documentElement.scrollHeight-window.innerHeight;
      progress.style.width=`${Math.max(0,Math.min(100,distance>0?window.scrollY/distance*100:0))}%`;
      scheduled=false;
    };
    window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(update)}},{passive:true});
    update();
  }
})();
