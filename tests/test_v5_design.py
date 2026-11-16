"""Critérios de aceite específicos da direção B, Rodovias em Dados v5.0.

Os testes validam o código final regenerado, não apenas uma imagem ilustrativa.
"""
from pathlib import Path
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'docs/index.html').read_text(encoding='utf-8')
TEMPLATE = (ROOT / 'templates/article.html').read_text(encoding='utf-8')
CSS = (ROOT / 'docs/assets/css/style.css').read_text(encoding='utf-8')
DATA = json.loads((ROOT / 'docs/assets/data/analysis.json').read_text(encoding='utf-8'))
SOUP = BeautifulSoup(HTML, 'html.parser')


def test_visual_direction_and_headline():
    assert SOUP.html['data-release'] == '5.1'
    assert SOUP.select_one('.article-opening--v5 h1')
    assert SOUP.select_one('.opening-deck')
    assert SOUP.select_one('.opening-meta')
    assert len(SOUP.select('.overview-metric')) == 4
    assert '213.497' in SOUP.select_one('.overview-strip').get_text(' ', strip=True)
    assert not SOUP.select('.hero-note,.opening-illustration,.theme-toggle,.map-shell,iframe')


def test_research_cards_and_analysis_links():
    cards = SOUP.select('.research-card')
    assert len(cards) == 3
    assert [c.select_one('.research-card__symbol').get_text(strip=True) for c in cards] == ['01', '02', '03']
    assert [c['href'] for c in cards] == ['#rq1-title', '#rq2-title', '#rq3-title']
    for card in cards:
        assert card.find('strong') and card.select_one('.research-card__arrow')


def test_chart_data_and_fair_access():
    assert len(SOUP.select('img.print-chart')) == 5
    assert len(SOUP.select('.interactive-chart')) == 5
    assert len(SOUP.select('#disponibilidade .fair-rows > div')) == 4
    assert len(SOUP.select('#disponibilidade .csv-collections a')) >= 4
    assert len(DATA['annual']) == 3
    assert sum(x['accidents'] for x in DATA['annual']) == 213497
    assert sum(x['fatal_accidents'] for x in DATA['annual']) == 15293


def test_only_one_light_theme_and_no_legacy_css():
    assert 'theme-dark' not in CSS and 'color-scheme:dark' not in CSS
    assert '.hero-note' not in CSS and '.map-shell' not in CSS
    assert '#disponibilidade' in CSS and '.pipeline' in CSS
    assert 'v2.1' not in CSS and 'v4.1' not in CSS
    assert 'data-release="5.1"' in TEMPLATE


def test_source_files_and_print_pdf_rules():
    print_css = (ROOT / 'docs/assets/css/print.css').read_text(encoding='utf-8')
    assert '@page' in print_css and 'A4' in print_css
    assert 'break-before:page' in print_css
    for path in ['src/etl.py','src/visualizations.py','src/persist.py','scripts/refinar_artigo.py','docs/assets/js/interactions.js',
                 'templates/article.html','data/processed/auditoria.json','docs/assets/data/analysis.json']:
        assert (ROOT / path).is_file(), path
