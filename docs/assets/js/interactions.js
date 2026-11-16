/* Rodovias em Dados v5.0 | Interações progressivas sem bibliotecas externas.
   Dados: agregados públicos gerados por src.etl. Nenhuma requisição para uma API externa.
*/
(() => {
  'use strict';
  const $ = (q) => document.querySelector(q);
  const fmt = new Intl.NumberFormat('pt-BR');
  const num = (x) => Number(x) || 0;
  let data;
  try { data = JSON.parse($('#analysis-data')?.textContent || '{}'); } catch (_) { data = {}; }

  // A experiência de leitura é sempre clara. A impressão usa CSS A4 dedicado.
  const replication = $('#disponibilidade .replication-details');
  let wasOpen = false;
  window.addEventListener('beforeprint', () => {
    if (replication) { wasOpen = replication.open; replication.open = true; }
  });
  window.addEventListener('afterprint', () => {
    if (replication) replication.open = wasOpen;
  });
  $('#print-article')?.addEventListener('click', () => window.print());

  // Navegação discreta, sem rolagem forçada ou efeitos de movimento.
  const navLinks = [...document.querySelectorAll('.article-nav a[href^="#"]')];
  if ('IntersectionObserver' in window && navLinks.length) {
    const sections = navLinks.map(a => document.getElementById(a.hash.slice(1))).filter(Boolean);
    const observer = new IntersectionObserver((entries) => {
      const shown = entries.filter(x => x.isIntersecting).sort((a,b) => b.intersectionRatio-a.intersectionRatio);
      if (!shown.length) return;
      const target = shown[0].target.id;
      for(const a of navLinks) a.classList.toggle('is-current',a.hash === '#'+target);
    }, {rootMargin:'-20% 0px -58% 0px', threshold:[0,.1,.2,.4,.6]});
    sections.forEach(section => observer.observe(section));
  }

  function toggle(group, val) {
    document.querySelectorAll(`[${group}]`).forEach(button => {
      const active = button.getAttribute(group) === val;
      button.classList.toggle('is-active',active);
      button.setAttribute('aria-pressed',String(active));
    });
  }
  function selected(group, fallback) {
    return document.querySelector(`[${group}].is-active`)?.getAttribute(group) || fallback;
  }
  const btnGroups = {
    'data-clock-mode': 'hourly',
    'data-clock-metric': 'accidents'
  };
  for (const [attr] of Object.entries(btnGroups)) {
    document.querySelectorAll(`[${attr}]`).forEach(button => button.addEventListener('click', () => {
      toggle(attr,button.getAttribute(attr));
      renderClock();
    }));
  }

  // Histograma temporal em CSS, legível com mouse, teclado e leitor de tela.
  function renderClock() {
    const root = $('#chart-clock');
    if (!root || !data.hourly || !data.weekday) return;
    const mode = selected('data-clock-mode','hourly');
    const metric = selected('data-clock-metric','accidents');
    const rows = data[mode];
    const max = Math.max(1, ...rows.map(r => num(r[metric])));
    const grid = document.createElement('div');
    grid.className = 'clock-bars';
    grid.setAttribute('role','group');
    grid.setAttribute('aria-label',`Distribuição por ${mode==='hourly'?'hora':'dia da semana'}`);
    rows.forEach((r) => {
      const label = mode === 'hourly' ? `${String(r.hour).padStart(2,'0')}h` : r.name;
      const value = num(r[metric]);
      const item = document.createElement('div');
      item.className = 'clock-bars__item';
      item.setAttribute('tabindex','0');
      item.setAttribute('role','img');
      item.setAttribute('aria-label',`${label}: ${fmt.format(value)} ${metric==='deaths'?'mortes':'sinistros'}`);
      item.title = item.getAttribute('aria-label');
      const val = document.createElement('span'); val.className='clock-bars__value';
      val.textContent = fmt.format(value);
      const bar = document.createElement('span');
      bar.className = 'clock-bars__bar';
      bar.style.height = `${Math.max(4,100*value/max)}%`;
      bar.style.background = metric === 'deaths' ? '#BA704C' : '#3F769C';
      const axis = document.createElement('span'); axis.className='clock-bars__label';
      axis.textContent = label;
      item.append(val,bar,axis);
      grid.appendChild(item);
    });
    root.replaceChildren(grid);
    const target = $('#table-clock');
    if (target) {
      const head = document.createElement('thead');
      head.innerHTML = '<tr><th scope="col">Período</th><th scope="col">Sinistros</th><th scope="col">Mortes</th></tr>';
      const tbody = document.createElement('tbody');
      rows.forEach(r=>{
        const tr=document.createElement('tr');
        const label=mode==='hourly'?`${String(r.hour).padStart(2,'0')}h`:r.name;
        [label,fmt.format(r.accidents),fmt.format(r.deaths)].forEach(t=>{const td=document.createElement('td');td.textContent=t;tr.appendChild(td)});
        tbody.appendChild(tr);
      });
      const table=document.createElement('table');table.className='data-table';table.append(head,tbody);
      target.replaceChildren(table);
    }
  }

  // Exportações espelham a métrica atualmente selecionada em cada gráfico.
  function exportRows(kind) {
    const timeMetric = selected('data-time-metric','accidents');
    const timeMode = selected('data-time-mode','annual');
    const typeMode = selected('data-type-mode','top_types_2025');
    const severityMode = selected('data-severity-mode','tipo_pista');
    const geoMode = selected('data-geo-mode','top_states_2025');
    const clockMode = selected('data-clock-mode','hourly');
    switch(kind) {
      case 'time': return {name:`prf-${timeMode}-${timeMetric}.csv`,rows:data[timeMode],columns:timeMode==='monthly'?['year','month',timeMetric]:['year',timeMetric]};
      case 'clock': return {name:`prf-${clockMode}.csv`,rows:data[clockMode],columns:clockMode==='hourly'?['hour','accidents','deaths','injured']:['name','accidents','deaths','injured']};
      case 'types': return {name:`prf-${typeMode}.csv`,rows:data[typeMode],columns:['name','accidents','deaths','injured','fatal_accidents']};
      case 'severity': return {name:`prf-gravidade-${severityMode}.csv`,rows:data.severity_2025?.[severityMode],columns:['name','accidents','fatal_accidents','deaths','fatal_rate']};
      case 'geo': return {name:`prf-${geoMode}.csv`,rows:data[geoMode],columns:['name','accidents','deaths','injured']};

      default: return null;
    }
  }
  function csvSafe(value) {
    let v=String(value ?? '');
    if (/^[=+@\-]/.test(v) && !/^-?\d+(?:\.\d+)?$/.test(v)) v="'"+v;
    return '"' + v.replaceAll('"','""') + '"';
  }
  document.querySelectorAll('[data-export]').forEach(button=>button.addEventListener('click',()=>{
    const item=exportRows(button.dataset.export);
    if (!item?.rows?.length) return;
    const csv='\ufeff'+item.columns.map(csvSafe).join(';')+'\r\n'+item.rows.map(row=>item.columns.map(k=>csvSafe(row[k])).join(';')).join('\r\n');
    const uri=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
    const link=document.createElement('a');link.href=uri;link.download=item.name;
    document.body.appendChild(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(uri),2500);
  }));

  renderClock();
})();
