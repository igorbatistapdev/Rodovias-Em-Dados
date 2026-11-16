"""Gera o artigo a partir de template único, sem sobrescrever o design manual.

Edite templates/article.html (fonte de verdade) e docs/assets/css/style.css.
A cada execução, somente docs/index.html é recompilado com os agregados em JSON.

Uso:
    python scripts/refinar_artigo.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'docs/assets/data/analysis.json'
TEMPLATE_DIR = ROOT / 'templates'
OUTPUT = ROOT / 'docs/index.html'


def fmt_br(value: int | float) -> str:
    return f'{int(value):,}'.replace(',', '.')


def fmt_en(value: int | float) -> str:
    return f'{int(value):,}'


def pct_br(value: float) -> str:
    return f'{abs(float(value)):.2f}'.replace('.', ',') + '%'


def pct_br_signed(value: float) -> str:
    return ('+' if float(value) > 0 else '−' if float(value) < 0 else '') + pct_br(value)


def data_table(rows: list[dict], headers: list[tuple[str, str]]) -> str:
    head = '<thead><tr>' + ''.join(f'<th scope="col">{html.escape(title)}</th>' for title, _ in headers) + '</tr></thead>'
    body_rows = []
    for row in rows:
        values = []
        for _, key in headers:
            value = row.get(key, '')
            if key == 'fatal_rate': value = pct_br(value)
            elif isinstance(value, (int, float)): value = fmt_br(value)
            values.append(f'<td>{html.escape(str(value))}</td>')
        body_rows.append('<tr>' + ''.join(values) + '</tr>')
    return '<table class="data-table">' + head + '<tbody>' + ''.join(body_rows) + '</tbody></table>'


def render_article(path: Path = DATA_PATH, output: Path = OUTPUT) -> str:
    data = json.loads(path.read_text(encoding='utf-8'))
    if len(data['annual']) != 3 or sorted(x['year'] for x in data['annual']) != [2023, 2024, 2025]:
        raise ValueError('A pesquisa exige três séries anuais de 2023 a 2025')
    annual = data['annual']
    total_accidents = sum(r['accidents'] for r in annual)
    total_deaths = sum(r['deaths'] for r in annual)
    total_injured = sum(r['injured'] for r in annual)
    total_fatal = sum(r['fatal_accidents'] for r in annual)
    def get_type(text):
        return next(row for row in data['top_types_2025'] if row['name'].casefold() == text.casefold())
    rear, frontal = get_type('Colisão traseira'), get_type('Colisão frontal')
    by_pista = data['severity_2025']['tipo_pista']
    single = next(row for row in by_pista if row['name'] == 'Simples')
    double = next(row for row in by_pista if row['name'] == 'Dupla')
    pct = lambda x: float(x) * 100
    public = {k: v for k, v in data.items() if k not in ('map_grid_2025', 'audit')}
    # JSON inline avoids network requests and works offline/file://.
    analysis_json = json.dumps(public, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    tables = {
        'table_time': data_table([{'label': str(x['year']), **x} for x in annual], [('Ano','label'), ('Sinistros','accidents'), ('Mortes','deaths'), ('Feridos','injured')]),
        'table_types': data_table(data['top_types_2025'][:7], [('Tipo','name'),('Ocorrências','accidents'),('Mortes','deaths'),('Feridos','injured')]),
        'table_severity': data_table(by_pista, [('Tipo de pista','name'),('Ocorrências','accidents'),('Com morte','fatal_accidents'),('Proporção','fatal_rate')]),
        'table_geo': data_table(data['top_states_2025'][:9], [('UF','name'),('Ocorrências','accidents'),('Mortes','deaths'),('Feridos','injured')]),
        'table_clock': data_table(data['hourly'], [('Hora','hour'), ('Sinistros','accidents'),('Mortes','deaths')]),
    }
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(['html']), keep_trailing_newline=True)
    for key, value in {'fmt_br': fmt_br, 'fmt_en': fmt_en, 'pct_br': pct_br, 'pct_br_signed': pct_br_signed}.items():
        env.filters[key] = value
    rendered = env.get_template('article.html').render(
        annual=annual,
        total_accidents=total_accidents,
        total_deaths=total_deaths,
        total_fatal=total_fatal,
        total_injured=total_injured,
        change_2024=pct(annual[1]['accidents']/annual[0]['accidents']-1),
        change_2025_abs=pct(1-annual[2]['accidents']/annual[1]['accidents']),
        top_type_name=data['top_types_2025'][0]['name'],
        top_type_accidents=data['top_types_2025'][0]['accidents'],
        rear_total=rear['accidents'], rear_fatal_count=rear['fatal_accidents'],
        frontal_total=frontal['accidents'], frontal_fatal_count=frontal['fatal_accidents'],
        rear_fatal_rate=pct(rear['fatal_accidents']/rear['accidents']),
        frontal_fatal_rate=pct(frontal['fatal_accidents']/frontal['accidents']),
        single=single, double=double,
        top_state_name=data['top_states_2025'][0]['name'],
        top_state_accidents=data['top_states_2025'][0]['accidents'],
        top_road_1=data['top_roads_2025'][0]['name'],
        top_road_2=data['top_roads_2025'][1]['name'],
        analysis_json=analysis_json,
        **tables,
    )
    output.write_text(rendered, encoding='utf-8')
    return rendered


if __name__ == '__main__':
    page=render_article()
    print(f'Artigo gerado com template preservado: {OUTPUT}, {len(page):,} caracteres')
