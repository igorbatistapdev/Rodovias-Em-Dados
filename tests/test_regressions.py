"""Regressões da versão 4: dados, template, assets e geografia.

Rodar com: python -m pytest -q
"""
from __future__ import annotations
import json
from pathlib import Path
from bs4 import BeautifulSoup
from scripts.refinar_artigo import render_article

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'docs/assets/data/analysis.json').read_text(encoding='utf-8'))


def test_aggregates_annual_and_hourly():
    annual=DATA['annual']
    assert [x['year'] for x in annual]==[2023,2024,2025]
    assert sum(x['accidents'] for x in annual)==213497
    assert sum(x['deaths'] for x in annual)==17833
    assert sum(x['injured'] for x in annual)==246608
    assert sum(x['accidents'] for x in DATA['weekday'])==213497
    assert sum(x['accidents'] for x in DATA['hourly'])<=213497
    assert len(DATA['hourly'])==24 and len(DATA['weekday'])==7


def test_geographic_aggregates_by_uf():
    ufs=DATA['top_states_2025']
    assert len(ufs)==27
    assert set(x['name'] for x in ufs)==set(r['uf'] for r in DATA['uf_annual'] if r['year']==2025)
    assert sum(x['accidents'] for x in ufs)==DATA['annual'][2]['accidents']
    assert {r['year'] for r in DATA['uf_annual']}=={2023,2024,2025}
    for year in (2023,2024,2025):
        assert sum(r['accidents'] for r in DATA['uf_annual'] if r['year']==year) == next(r['accidents'] for r in DATA['annual'] if r['year']==year)


def test_distinction_between_deaths_and_fatal_crashes():
    assert sum(x['fatal_accidents'] for x in DATA['annual']) <= sum(x['deaths'] for x in DATA['annual'])
    frontal=next(x for x in DATA['top_types_2025'] if x['name']=='Colisão frontal')
    rear=next(x for x in DATA['top_types_2025'] if x['name']=='Colisão traseira')
    assert frontal['fatal_accidents']/frontal['accidents'] > rear['fatal_accidents']/rear['accidents']


def test_etl_audit_and_compact_public_data():
    audit=DATA['audit']
    assert len(audit)==3
    assert all(len(a['sha256'])==64 for a in audit)
    assert len(DATA['map_grid_2025'])>0
    for row in DATA['map_grid_2025']:
        assert len(row)==3
        assert -35<=row[0]<=6 and -75<=row[1]<=-32
    assert (ROOT/'data/processed/sinistros_diarios_uf_2023_2025.csv.gz').exists()


def test_render_is_deterministic_and_preserves_template(tmp_path):
    template=ROOT/'templates/article.html'
    before=template.read_bytes()
    a=render_article(output=tmp_path/'a.html')
    b=render_article(output=tmp_path/'b.html')
    assert a==b
    assert b'{{ analysis_json | safe }}' in before
    assert template.read_bytes()==before
    assert '{{ ' not in a and '{% ' not in a
    assert '213.497' in a and '15.293' in a
    assert '213,497' in a  # abstract em inglês
    assert 'data-map-year' not in a
    assert 'theme-toggle' not in a
    assert len(BeautifulSoup(a, 'html.parser').select('.research-card'))==3


def test_article_links_and_accessible_figures():
    html=(ROOT/'docs/index.html').read_text(encoding='utf-8')
    soup=BeautifulSoup(html,'html.parser')
    ids=[x['id'] for x in soup.select('[id]')]
    assert len(ids)==len(set(ids))
    assert len(soup.find_all('h1'))==1
    assert len(soup.select('figure figcaption'))>=6
    assert len(soup.select('.chart-button'))>=13
    assert len(soup.select('img.print-chart'))==5
    assert soup.select_one('link[href="./assets/css/print.css"]') is not None
    assert not soup.select('iframe, #theme-toggle, #uf-cartogram, .opening-illustration')
    for link in soup.select('a[href^="#"]'):
        anchor=link['href'][1:]
        assert anchor=='' or anchor in ids
    for asset in soup.select('script[src], img[src], link[rel="stylesheet"], link[rel="manifest"]'):
        uri=asset.get('src') or asset.get('href') or ''
        if uri.startswith('./'):
            assert (ROOT/'docs'/uri[2:]).is_file(),uri
    for img in soup.find_all('img'):
        assert img.has_attr('alt')


def test_portuguese_resumo_length():
    soup=BeautifulSoup((ROOT/'docs/index.html').read_text(encoding='utf-8'),'html.parser')
    text=soup.select_one('#resumo p').get_text(' ',strip=True)
    assert 150<=len(text.split())<=250


def test_removed_legacy_features_but_preserved_geographic_data():
    template=(ROOT/'templates/article.html').read_text(encoding='utf-8')
    assert 'data-map-view' not in template
    assert 'map-shapes-data' not in template
    assert 'mapa-calor-2025.html' not in template
    assert 'theme-dark' not in template
    assert 'rodovia-editorial-conceitual.webp' not in template
    assert not (ROOT/'docs/assets/images/mapa-celulas-2025.svg').exists()
    assert not (ROOT/'docs/assets/maps/mapa-calor-2025.html').exists()
    assert DATA['top_states_2025'] and DATA['top_roads_2025']


def test_print_style_and_generated_assets():
    css=(ROOT/'docs/assets/css/print.css').read_text(encoding='utf-8')
    main=(ROOT/'docs/assets/css/style.css').read_text(encoding='utf-8')
    v4=(ROOT/'docs/assets/js/interactions.js').read_text(encoding='utf-8')
    assert '@page' in css and 'A4' in css
    assert '.print-chart' in css and '.hero-note' not in css
    assert 'html.theme-dark' not in main
    assert 'localStorage' not in v4
    assert 'renderTiles' not in v4
    assert (ROOT/'docs/assets/images/grafico-ufs.svg').is_file()


def test_raw_zip_files_unchanged_sha256():
    import hashlib
    audit=json.loads((ROOT/'data/processed/auditoria.json').read_text(encoding='utf-8'))
    assert isinstance(audit, list) and len(audit)==3
    for y in (2023,2024,2025):
        p=ROOT/f'data/raw/datatran{y}.zip'
        assert p.is_file() and p.stat().st_size>1000000
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest==next(row['sha256'] for row in audit if row['year']==y)
