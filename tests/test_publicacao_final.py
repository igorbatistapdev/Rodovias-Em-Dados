"""Regressão da edição acadêmica final: fontes, gráficos, impressão e arquivos."""
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGE = BeautifulSoup((ROOT/'docs/index.html').read_text(encoding='utf-8'),'html.parser')
CSS = (ROOT/'docs/assets/css/style.css').read_text(encoding='utf-8')
PRINT = (ROOT/'docs/assets/css/print.css').read_text(encoding='utf-8')
JS = (ROOT/'docs/assets/js/main.js').read_text(encoding='utf-8')


def test_edicao_publicavel_sem_elementos_provisorios():
    assert PAGE.html['data-release'] == '5.1'
    assert not PAGE.select('.theme-toggle,.opening-illustration,.map-shell,iframe')
    assert 'protótipo' not in PAGE.get_text(' ',strip=True).casefold()
    assert len(PAGE.select('.research-card')) == 3
    assert 'repositório github' in PAGE.select_one('.masthead__right').get_text(' ',strip=True).lower()
    assert PAGE.select_one('.masthead__right a')['href'] == 'https://github.com/igorbatistapdev/Rodovias-Em-Dados'


def test_referencias_abnt_com_urls_completas_e_ancoras():
    block = PAGE.select_one('#referencias')
    assert 'NBR 6023:2025' in block.get_text(' ',strip=True)
    assert 'NBR 10520:2023' in block.get_text(' ',strip=True)
    refs = block.select('ol.references li')
    assert len(refs) == 7
    for ref in refs:
        assert ref.get('id','').startswith('ref-')
        link = ref.find('a',href=True)
        assert link and urlsplit(link['href']).scheme == 'https'
        assert link.get_text(strip=True).startswith('https://')
        assert 'Acesso em: 12 nov. 2026' in ref.get_text(' ',strip=True)
    assert PAGE.select_one('#ref-wilkinson a')['href'].startswith('https://pmc.ncbi.nlm.nih.gov')
    assert PAGE.select_one('#ref-mckinney a')['href'].endswith('.pdf')


def test_integridade_links_locais_e_ids():
    ids=[el['id'] for el in PAGE.select('[id]')]
    assert len(ids)==len(set(ids))
    for a in PAGE.select('a[href]'):
        href=a['href']
        if href.startswith('#'):
            assert href[1:] in ids, href
        elif href.startswith('./'):
            assert (ROOT/'docs'/href).is_file(), href
    for tag in PAGE.select('img[src],script[src],link[rel="stylesheet"][href]'):
        p=tag.get('src',tag.get('href',''))
        if p.startswith('./'):
            assert (ROOT/'docs'/p).is_file(), p


def test_graficos_com_cores_alternativas_e_pdf():
    for c in ('#3F769C','#BA704C','#75668F','#AE8540'):
        assert c in JS or c in CSS
    assert 'metricPalette' in JS
    assert len(PAGE.select('img.print-chart'))==5
    assert 'A4' in PRINT and '#abstract-title' in PRINT
    assert '.references--abnt' in PRINT
    assert PAGE.find(class_='method-code-sample') is not None
