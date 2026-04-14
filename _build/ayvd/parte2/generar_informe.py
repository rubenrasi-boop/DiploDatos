#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entregable AyVD — Parte 2 (versión HTML interactiva con Plotly)
Diplomatura en Ciencia de Datos 2026 — FAMAF, UNC

Alumno:  Rubén Rasi
Docente: Fredy Alexander Restrepo Blandon

Ejercicios cubiertos:
    1.   Estimación puntual e IC del 95 % para μA − μB (Welch + bootstrap).
    2.1  Formalización del test de hipótesis.
    2.2  P-valor, decisión y verificación no paramétrica (Mann-Whitney U).
    2.3  Potencia del test (Cohen's d, tt_ind_solve_power).
    3.   Comunicación y visualización (referencia al PDF A4).

Uso:
    python generar_informe.py
        Imprime por consola los cuadros que se muestran en el informe
        HTML y escribe informe_parte2.html en el mismo directorio.

Este archivo es la versión paralela al datos_parte2.py (apéndice en
matplotlib/seaborn). Comparte los mismos filtros, los mismos tests y
los mismos números; cambia sólo la capa de presentación (Plotly
interactivo + HTML autocontenido con KaTeX).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from statsmodels.stats.power import TTestIndPower, tt_ind_solve_power

pd.set_option('display.width', 130)
pd.set_option('display.max_columns', 20)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'sysarmy_survey_2026_processed.csv'
if not DATA_PATH.exists():
    DATA_PATH = (BASE_DIR.parents[2] /
                 'AnalisisyVisualizacion/entregables/parte2/data/'
                 'sysarmy_survey_2026_processed.csv')
OUTPUT_HTML = BASE_DIR / 'informe_parte2.html'

ALPHA = 0.05

COLOR_A = '#5B8DEF'
COLOR_B = '#C96C6C'
COLOR_BOOT = '#8FB39E'
COLOR_GRID = '#E6E8EF'
COLOR_TEXTO = '#2E3440'
COLOR_MUTED = '#5E6472'
BG_PLOT = '#FAFBFC'


def titulo(texto: str) -> None:
    print(f'\n=== {texto} ' + '=' * max(0, 70 - len(texto)))


# ============================================================
# 1.0  Carga y filtrado
# ============================================================

df = pd.read_csv(DATA_PATH)
N_INICIAL = len(df)

titulo('1.0  Carga')
print(f'archivo:          {DATA_PATH.name}')
print(f'filas iniciales:  {N_INICIAL}')

COLUMNAS = [
    'tools_programming_languages',
    'salary_monthly_NETO',
    'work_dedication',
    'work_contract_type',
    'profile_gender',
]
df = df[COLUMNAS].copy()

CONTRATOS_VALIDOS = [
    'Staff (planta permanente)',
    'Contractor',
    'Tercerizado (trabajo a través de consultora o SaaS)',
]
PISO_SMVM = 300_000
TECHO_SIMETRICO = 15_000_000

filtros_aplicados: list[dict] = []


def aplicar_filtro(dataframe, nombre, motivo, mascara):
    n_antes = len(dataframe)
    nuevo = dataframe[mascara].copy()
    n_despues = len(nuevo)
    recorte = n_antes - n_despues
    filtros_aplicados.append({
        'filtro': nombre, 'motivo': motivo,
        'n_antes': n_antes, 'n_despues': n_despues,
        'recorte': recorte,
        'pct': round(100 * recorte / n_antes, 2) if n_antes else 0,
    })
    return nuevo


df = aplicar_filtro(
    df, 'F1', 'Descartar filas sin lenguaje o sin sueldo NETO',
    df['tools_programming_languages'].notna() & df['salary_monthly_NETO'].notna(),
)
df = aplicar_filtro(
    df, 'F2', 'Retener sólo jornadas Full-Time',
    df['work_dedication'] == 'Full-Time',
)
df = aplicar_filtro(
    df, 'F3', 'Retener contratos con ingreso en forma de sueldo mensual',
    df['work_contract_type'].isin(CONTRATOS_VALIDOS),
)
df = aplicar_filtro(
    df, 'F5', f'Piso SMVM: NETO ≥ {PISO_SMVM:,} ARS'.replace(',', '.'),
    df['salary_monthly_NETO'] >= PISO_SMVM,
)
df = aplicar_filtro(
    df, 'F6', f'Techo simétrico: NETO ≤ {TECHO_SIMETRICO:,} ARS'.replace(',', '.'),
    df['salary_monthly_NETO'] <= TECHO_SIMETRICO,
)
N_FINAL = len(df)

titulo('1.1  Filtros aplicados')
for f in filtros_aplicados:
    print(f"  {f['filtro']}  {f['motivo'][:55]:<55} "
          f"{f['n_antes']:>5} → {f['n_despues']:>5}  (-{f['recorte']})")


# ============================================================
# 1.2  Grupos
# ============================================================

groupA = df.loc[df['profile_gender'] == 'Hombre Cis', 'salary_monthly_NETO']
groupB = df.loc[df['profile_gender'] == 'Mujer Cis', 'salary_monthly_NETO']
nA, nB = len(groupA), len(groupB)
mediaA, mediaB = float(groupA.mean()), float(groupB.mean())
medianaA, medianaB = float(groupA.median()), float(groupB.median())
sA = float(groupA.std(ddof=1))
sB = float(groupB.std(ddof=1))
sA2, sB2 = sA ** 2, sB ** 2

titulo('1.2  Grupos analíticos')
print(f'  groupA (Varón cis)  n={nA}  media=${mediaA:,.0f}  sd=${sA:,.0f}'
      .replace(',', '.'))
print(f'  groupB (Mujer cis)  n={nB}  media=${mediaB:,.0f}  sd=${sB:,.0f}'
      .replace(',', '.'))


# ============================================================
# EJERCICIO 1 — Estimación
# ============================================================

delta_hat = mediaA - mediaB
se_welch = np.sqrt(sA2 / nA + sB2 / nB)
nu_welch = (sA2 / nA + sB2 / nB) ** 2 / (
    (sA2 / nA) ** 2 / (nA - 1) + (sB2 / nB) ** 2 / (nB - 1)
)
t_crit = stats.t.ppf(1 - ALPHA / 2, nu_welch)
ic_welch_low = delta_hat - t_crit * se_welch
ic_welch_high = delta_hat + t_crit * se_welch

rng = np.random.default_rng(seed=202604)
n_boot = 10_000
a_arr, b_arr = groupA.to_numpy(), groupB.to_numpy()
diffs_boot = np.empty(n_boot)
for i in range(n_boot):
    diffs_boot[i] = (rng.choice(a_arr, size=nA, replace=True).mean()
                     - rng.choice(b_arr, size=nB, replace=True).mean())
ic_boot_low, ic_boot_high = np.percentile(
    diffs_boot, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)]
)

titulo('2.0  Estimación puntual e IC')
print(f'  Δ̂ = ${delta_hat:,.0f}'.replace(',', '.'))
print(f'  IC Welch     = [${ic_welch_low:,.0f} , ${ic_welch_high:,.0f}]'
      .replace(',', '.'))
print(f'  IC Bootstrap = [${ic_boot_low:,.0f} , ${ic_boot_high:,.0f}]'
      .replace(',', '.'))


# ============================================================
# EJERCICIO 2 — Tests
# ============================================================

t_stat, p_bilateral = stats.ttest_ind(groupA, groupB, equal_var=False)
u_stat, p_mwu = stats.mannwhitneyu(groupA, groupB, alternative='two-sided')

s_pooled = np.sqrt(((nA - 1) * sA2 + (nB - 1) * sB2) / (nA + nB - 2))
cohens_d = (mediaA - mediaB) / s_pooled
ratio_nb_na = nB / nA
n_necesario = {
    p: tt_ind_solve_power(effect_size=cohens_d, alpha=ALPHA,
                          power=p, ratio=ratio_nb_na)
    for p in (0.80, 0.90, 0.95)
}
power_obs = TTestIndPower().power(
    effect_size=cohens_d, nobs1=nA, alpha=ALPHA, ratio=ratio_nb_na,
)

titulo('2.1  Test de Welch')
print(f'  t = {t_stat:.4f}   ν = {nu_welch:.2f}   p = {p_bilateral:.3e}')
titulo('2.2  Mann-Whitney U')
print(f'  U = {u_stat:.0f}   p = {p_mwu:.3e}')
titulo('2.3  Potencia')
print(f"  Cohen's d = {cohens_d:.4f}  ·  potencia observada = {power_obs:.4f}")


# ============================================================
# 2.4  Extensión a tres grupos — ANOVA y Kruskal-Wallis
# ============================================================
# Aprovecha el material que el docente sumó al notebook 05 y a las
# slides de Test de Hipótesis: ANOVA de un factor (paramétrico) y
# Kruskal-Wallis (no paramétrico) sobre los TRES grupos analíticos
# (Varón cis, Mujer cis, Diversidades). La extensión a Diversidades
# sigue la misma agrupación respetuosa de identidades minoritarias
# que se usó en parte 1 (ej 2d / G11). Es complementaria a la
# consigna obligatoria de 2 grupos.
COLOR_D = '#9673C0'
CATEGORIAS_DIVERSIDADES = [
    'No binarie', 'Trans', 'Queer', 'Lesbiana', 'Agénero',
    'Prefiero no decir',
]
mask_div = df['profile_gender'].isin(CATEGORIAS_DIVERSIDADES)
groupD = df.loc[mask_div, 'salary_monthly_NETO']
nD = len(groupD)
mediaD = float(groupD.mean()) if nD > 0 else float('nan')
medianaD = float(groupD.median()) if nD > 0 else float('nan')
sD = float(groupD.std(ddof=1)) if nD > 1 else float('nan')

F_anova, p_anova = stats.f_oneway(groupA, groupB, groupD)
H_kw, p_kw = stats.kruskal(groupA, groupB, groupD)
N_total_3g = nA + nB + nD
gl_entre = 2
gl_dentro = N_total_3g - 3

titulo('2.4  ANOVA y Kruskal-Wallis sobre tres grupos')
print(f'  groupD (Diversidades): n = {nD}, '
      f'media = ${mediaD:,.0f}'.replace(',', '.'))
print(f'  ANOVA           F = {F_anova:.3f}  p = {p_anova:.3e}')
print(f'  Kruskal-Wallis  H = {H_kw:.3f}  p = {p_kw:.3e}')


# ============================================================
# Helpers Plotly
# ============================================================

def layout_claro(fig: go.Figure, titulo_fig: str, alto: int = 460) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo_fig, font=dict(size=15, color=COLOR_TEXTO)),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor='white',
        font=dict(family='-apple-system, Segoe UI, Inter, sans-serif',
                  size=12, color=COLOR_TEXTO),
        margin=dict(l=80, r=40, t=60, b=60),
        height=alto,
    )
    fig.update_xaxes(gridcolor=COLOR_GRID, linecolor=COLOR_GRID,
                     zerolinecolor=COLOR_GRID)
    fig.update_yaxes(gridcolor=COLOR_GRID, linecolor=COLOR_GRID,
                     zerolinecolor=COLOR_GRID)
    return fig


def fig_div(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       config={'displaylogo': False, 'responsive': True})


# ============================================================
# FIGURAS
# ============================================================

# ----- G1  Histogramas comparativos -----
fig_g1 = make_subplots(rows=1, cols=2, shared_yaxes=True,
                       subplot_titles=(f'groupA — Varón cis  (n = {nA})',
                                       f'groupB — Mujer cis  (n = {nB})'))
fig_g1.add_trace(go.Histogram(
    x=groupA / 1e6, nbinsx=40, marker_color=COLOR_A,
    marker_line=dict(color='white', width=0.4), opacity=0.85,
    showlegend=False,
    hovertemplate='NETO: $ %{x:.2f} M<br>freq: %{y}<extra></extra>',
), row=1, col=1)
fig_g1.add_trace(go.Histogram(
    x=groupB / 1e6, nbinsx=40, marker_color=COLOR_B,
    marker_line=dict(color='white', width=0.4), opacity=0.85,
    showlegend=False,
    hovertemplate='NETO: $ %{x:.2f} M<br>freq: %{y}<extra></extra>',
), row=1, col=2)
for col, media, mediana in [
    (1, mediaA / 1e6, medianaA / 1e6),
    (2, mediaB / 1e6, medianaB / 1e6),
]:
    fig_g1.add_vline(x=media, line_dash='dash', line_color=COLOR_MUTED,
                     line_width=1.4, row=1, col=col,
                     annotation_text=f'media = $ {media:.2f} M',
                     annotation_position='top right',
                     annotation_font_size=10,
                     annotation_font_color=COLOR_MUTED)
    fig_g1.add_vline(x=mediana, line_dash='dot', line_color=COLOR_MUTED,
                     line_width=1.4, row=1, col=col)
layout_claro(fig_g1, 'Distribución del sueldo NETO por grupo', alto=400)
fig_g1.update_xaxes(title='Sueldo NETO (millones de ARS)')
fig_g1.update_yaxes(title='frecuencia', row=1, col=1)


# ----- G2  Boxplot con puntos y medias -----
fig_g2 = go.Figure()
for nombre, serie, color in [
    (f'groupA (Varón cis)<br>n = {nA}', groupA / 1e6, COLOR_A),
    (f'groupB (Mujer cis)<br>n = {nB}', groupB / 1e6, COLOR_B),
]:
    fig_g2.add_trace(go.Box(
        y=serie, name=nombre,
        boxpoints='all', jitter=0.5, pointpos=0,
        marker=dict(color=color, size=3, opacity=0.35),
        line=dict(color=COLOR_MUTED, width=1.3),
        fillcolor=color, opacity=0.55,
        hovertemplate='NETO: $ %{y:.2f} M<extra></extra>',
    ))
fig_g2.add_trace(go.Scatter(
    x=[f'groupA (Varón cis)<br>n = {nA}',
       f'groupB (Mujer cis)<br>n = {nB}'],
    y=[mediaA / 1e6, mediaB / 1e6],
    mode='markers', marker=dict(symbol='diamond', size=13,
                                color='white',
                                line=dict(color=COLOR_MUTED, width=2)),
    name='media del grupo',
    hovertemplate='media: $ %{y:.2f} M<extra></extra>',
))
layout_claro(fig_g2, 'Comparación del sueldo NETO por grupo', alto=500)
fig_g2.update_yaxes(title='Sueldo NETO (millones de ARS)')
fig_g2.update_xaxes(title='')


# ----- G3  QQ-plots -----
def qq_data(serie):
    (qt, qm), (slope, intercept, r) = stats.probplot(serie.values, dist='norm')
    return qt, qm, slope, intercept, r


qtA, qmA, slopeA, interA, rA = qq_data(groupA)
qtB, qmB, slopeB, interB, rB = qq_data(groupB)

fig_g3 = make_subplots(rows=1, cols=2,
                       subplot_titles=('groupA — Varón cis',
                                       'groupB — Mujer cis'))
for col, qt, qm, slope, inter, r, color in [
    (1, qtA, qmA, slopeA, interA, rA, COLOR_A),
    (2, qtB, qmB, slopeB, interB, rB, COLOR_B),
]:
    fig_g3.add_trace(go.Scatter(
        x=qt, y=qm / 1e6, mode='markers',
        marker=dict(size=4, color=color, opacity=0.5),
        showlegend=False,
        hovertemplate='z teórico: %{x:.2f}<br>cuantil: $ %{y:.2f} M<extra></extra>',
    ), row=1, col=col)
    x_line = np.array([qt.min(), qt.max()])
    y_line = (slope * x_line + inter) / 1e6
    fig_g3.add_trace(go.Scatter(
        x=x_line, y=y_line, mode='lines',
        line=dict(color=COLOR_MUTED, width=1.4),
        name=f'ajuste r² = {r**2:.3f}',
        showlegend=False,
        hovertemplate=f'ajuste r² = {r**2:.3f}<extra></extra>',
    ), row=1, col=col)
layout_claro(fig_g3, 'QQ-plots contra la normal '
             '(chequeo visual de normalidad)', alto=430)
fig_g3.update_xaxes(title='Cuantil teórico normal')
fig_g3.update_yaxes(title='Cuantil muestral (M ARS)', row=1, col=1)


# ----- G4  Forest plot IC -----
fig_g4 = go.Figure()
fig_g4.add_vline(x=0, line_dash='dot', line_color=COLOR_MUTED,
                 line_width=1.3,
                 annotation_text='H₀: Δ = 0',
                 annotation_position='top',
                 annotation_font_size=10,
                 annotation_font_color=COLOR_MUTED)
metodos_g4 = ['Welch paramétrico', 'Bootstrap percentil']
centros = [delta_hat / 1e6, float(diffs_boot.mean()) / 1e6]
ics_low_m = [ic_welch_low / 1e6, ic_boot_low / 1e6]
ics_high_m = [ic_welch_high / 1e6, ic_boot_high / 1e6]
colores_m = [COLOR_A, COLOR_BOOT]
for metodo, centro, lo, hi, col in zip(
    metodos_g4, centros, ics_low_m, ics_high_m, colores_m,
):
    fig_g4.add_trace(go.Scatter(
        x=[centro], y=[metodo],
        mode='markers',
        marker=dict(symbol='diamond', size=15, color=col,
                    line=dict(color='white', width=1.5)),
        error_x=dict(type='data', symmetric=False,
                     array=[hi - centro], arrayminus=[centro - lo],
                     color=col, thickness=2.8, width=8),
        name=metodo,
        hovertemplate=(f'{metodo}<br>'
                       'Δ̂ = $ %{x:.3f} M<br>'
                       f'IC: [$ {lo:.3f} , $ {hi:.3f}] M<extra></extra>'),
    ))
layout_claro(fig_g4, 'Estimación puntual e intervalo de confianza del 95 %',
             alto=340)
fig_g4.update_xaxes(title='Δ̂ = μ_A − μ_B  (millones de ARS)')
fig_g4.update_yaxes(title='', categoryorder='array',
                    categoryarray=metodos_g4[::-1])
fig_g4.update_layout(showlegend=False)


# ----- G5  Curva de potencia -----
n_grid = np.linspace(20, max(nA * 1.05, 500), 200)
power_grid = [
    TTestIndPower().power(effect_size=cohens_d, nobs1=n,
                          alpha=ALPHA, ratio=ratio_nb_na)
    for n in n_grid
]
fig_g5 = go.Figure()
fig_g5.add_trace(go.Scatter(
    x=n_grid, y=power_grid, mode='lines',
    line=dict(color=COLOR_A, width=2.2),
    name=f"curva (d = {cohens_d:.3f})",
    hovertemplate='n_A = %{x:.0f}<br>potencia = %{y:.3f}<extra></extra>',
))
for target, marker in [(0.80, 'circle'), (0.90, 'square'),
                       (0.95, 'triangle-up')]:
    n_needed = tt_ind_solve_power(effect_size=cohens_d, alpha=ALPHA,
                                  power=target, ratio=ratio_nb_na)
    fig_g5.add_hline(y=target, line_dash='dash', line_color=COLOR_MUTED,
                     line_width=1.0, opacity=0.8,
                     annotation_text=f'power = {target}',
                     annotation_position='top right',
                     annotation_font_size=9,
                     annotation_font_color=COLOR_MUTED)
    fig_g5.add_trace(go.Scatter(
        x=[n_needed], y=[target], mode='markers',
        marker=dict(symbol=marker, size=14, color=COLOR_B,
                    line=dict(color='white', width=1.5)),
        name=f'n_A p={target} → {int(np.ceil(n_needed))}',
        hovertemplate=(f'n_A necesario = {int(np.ceil(n_needed))}<br>'
                       f'power target = {target}<extra></extra>'),
    ))
fig_g5.add_vline(x=nA, line_color=COLOR_MUTED, line_width=1.1, opacity=0.7,
                 annotation_text=f'n_A real = {nA}',
                 annotation_position='bottom right',
                 annotation_font_size=10,
                 annotation_font_color=COLOR_TEXTO)
layout_claro(fig_g5, 'Curva de potencia del test para el effect size observado',
             alto=470)
fig_g5.update_xaxes(title='Tamaño muestral n_A  (n_B = ratio · n_A)')
fig_g5.update_yaxes(title='Potencia 1 − β', range=[0, 1.05])


# ----- G6  Boxplot/violin de los TRES grupos (sección 2.4) -----
fig_g6 = go.Figure()
for nombre, serie, color in [
    (f'groupA (Varón cis)<br>n = {nA}', groupA / 1e6, COLOR_A),
    (f'groupB (Mujer cis)<br>n = {nB}', groupB / 1e6, COLOR_B),
    (f'groupD (Diversidades)<br>n = {nD}', groupD / 1e6, COLOR_D),
]:
    fig_g6.add_trace(go.Box(
        y=serie, name=nombre,
        boxpoints='all', jitter=0.5, pointpos=0,
        marker=dict(color=color, size=3, opacity=0.35),
        line=dict(color=COLOR_MUTED, width=1.3),
        fillcolor=color, opacity=0.55,
        hovertemplate='NETO: $ %{y:.2f} M<extra></extra>',
    ))
fig_g6.add_trace(go.Scatter(
    x=[f'groupA (Varón cis)<br>n = {nA}',
       f'groupB (Mujer cis)<br>n = {nB}',
       f'groupD (Diversidades)<br>n = {nD}'],
    y=[mediaA / 1e6, mediaB / 1e6, mediaD / 1e6],
    mode='markers', marker=dict(symbol='diamond', size=13,
                                color='white',
                                line=dict(color=COLOR_MUTED, width=2)),
    name='media del grupo',
    hovertemplate='media: $ %{y:.2f} M<extra></extra>',
))
layout_claro(
    fig_g6,
    'Comparación del sueldo NETO sobre los tres grupos analíticos (2.4)',
    alto=520,
)
fig_g6.update_yaxes(title='Sueldo NETO (millones de ARS)')
fig_g6.update_xaxes(title='')
fig_g6.add_annotation(
    text=(f'ANOVA  F = {F_anova:.2f}, p = {p_anova:.2e}   ·   '
          f'Kruskal-Wallis  H = {H_kw:.2f}, p = {p_kw:.2e}'),
    xref='paper', yref='paper', x=0, y=-0.16, showarrow=False,
    font=dict(size=10, color=COLOR_MUTED), xanchor='left',
)


# ============================================================
# HELPERS HTML / TABLAS
# ============================================================

def fmt_ars(v: float) -> str:
    return f'$ {v:,.0f}'.replace(',', '.')


def tabla_filtros_html() -> str:
    filas = ''
    for f in filtros_aplicados:
        filas += (
            f'<tr>'
            f'<td>{f["filtro"]}</td>'
            f'<td class="muted">{f["motivo"]}</td>'
            f'<td class="num">{f["n_antes"]}</td>'
            f'<td class="num">{f["n_despues"]}</td>'
            f'<td class="num">−{f["recorte"]} ({f["pct"]:.1f} %)</td>'
            f'</tr>'
        )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Filtro</th><th>Motivo</th>'
        '<th>N antes</th><th>N después</th><th>Recorte</th>'
        '</tr></thead>'
        f'<tbody>{filas}</tbody></table>'
    )


def tabla_descriptivos_html() -> str:
    filas = [
        ('n',          f'{nA}', f'{nB}'),
        ('media',      fmt_ars(mediaA), fmt_ars(mediaB)),
        ('mediana',    fmt_ars(medianaA), fmt_ars(medianaB)),
        ('desvío std', fmt_ars(sA), fmt_ars(sB)),
        ('Q1',         fmt_ars(float(groupA.quantile(.25))),
                       fmt_ars(float(groupB.quantile(.25)))),
        ('Q3',         fmt_ars(float(groupA.quantile(.75))),
                       fmt_ars(float(groupB.quantile(.75)))),
    ]
    cuerpo = ''.join(
        f'<tr><td>{et}</td><td class="num">{a}</td><td class="num">{b}</td></tr>'
        for et, a, b in filas
    )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Métrica</th>'
        '<th>groupA — Varón cis</th>'
        '<th>groupB — Mujer cis</th>'
        '</tr></thead>'
        f'<tbody>{cuerpo}</tbody></table>'
    )


def tabla_ic_html() -> str:
    ancho_w = ic_welch_high - ic_welch_low
    ancho_b = ic_boot_high - ic_boot_low
    filas = [
        ('Welch (t, varianzas desiguales)',
         fmt_ars(ic_welch_low), fmt_ars(delta_hat),
         fmt_ars(ic_welch_high), fmt_ars(ancho_w)),
        ('Bootstrap percentil (10 000 resamples)',
         fmt_ars(ic_boot_low), fmt_ars(float(diffs_boot.mean())),
         fmt_ars(ic_boot_high), fmt_ars(ancho_b)),
    ]
    cuerpo = ''.join(
        f'<tr>'
        f'<td>{m}</td>'
        f'<td class="num">{lo}</td>'
        f'<td class="num"><b>{est}</b></td>'
        f'<td class="num">{hi}</td>'
        f'<td class="num muted">{ancho}</td>'
        f'</tr>'
        for m, lo, est, hi, ancho in filas
    )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Método</th>'
        '<th>IC inferior</th>'
        '<th>Estimador</th>'
        '<th>IC superior</th>'
        '<th>Ancho</th>'
        '</tr></thead>'
        f'<tbody>{cuerpo}</tbody></table>'
    )


def tabla_test_html() -> str:
    dec_welch = ('<b style="color:#C96C6C">se rechaza H₀</b>'
                 if p_bilateral < ALPHA else '<b>no se rechaza H₀</b>')
    dec_mwu = ('<b style="color:#C96C6C">se rechaza H₀</b>'
               if p_mwu < ALPHA else '<b>no se rechaza H₀</b>')
    filas = [
        ('Welch (t, varianzas desiguales)',
         f'{t_stat:.4f}', f'{nu_welch:.1f}', f'{p_bilateral:.3e}',
         dec_welch),
        ('Mann-Whitney U (no paramétrico)',
         f'U = {u_stat:.0f}', '—', f'{p_mwu:.3e}', dec_mwu),
    ]
    cuerpo = ''.join(
        f'<tr>'
        f'<td>{m}</td>'
        f'<td class="num">{t}</td>'
        f'<td class="num">{nu}</td>'
        f'<td class="num">{p}</td>'
        f'<td>{d}</td>'
        f'</tr>'
        for m, t, nu, p, d in filas
    )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Test</th><th>Estadístico</th><th>ν</th>'
        '<th>P-valor bilateral</th><th>Decisión al α = 0,05</th>'
        '</tr></thead>'
        f'<tbody>{cuerpo}</tbody></table>'
    )


def tabla_potencia_html() -> str:
    filas = [
        ("Cohen's d (effect size)", f'{cohens_d:.4f}', 'magnitud moderada'),
        ('Desvío pooled (s_pooled)', fmt_ars(float(s_pooled)), ''),
        ('ratio n_B / n_A', f'{ratio_nb_na:.4f}', ''),
        ('n_A necesario para power = 0,80', f'{int(np.ceil(n_necesario[0.80]))}', ''),
        ('n_A necesario para power = 0,90', f'{int(np.ceil(n_necesario[0.90]))}', ''),
        ('n_A necesario para power = 0,95', f'{int(np.ceil(n_necesario[0.95]))}', ''),
        ('n_A real de la muestra', f'{nA}', ''),
        ('Potencia observada al n_A real', f'{power_obs:.4f}', ''),
    ]
    cuerpo = ''.join(
        f'<tr><td>{et}</td><td class="num">{val}</td><td class="muted">{com}</td></tr>'
        for et, val, com in filas
    )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Métrica</th><th>Valor</th><th>Comentario</th>'
        '</tr></thead>'
        f'<tbody>{cuerpo}</tbody></table>'
    )


def tabla_eleccion_ej3_html() -> str:
    filas = [
        ('<b>Tweet / LinkedIn</b>',
         'Una frase impactante, un número grande',
         'Buscar atención, simplificar, <b>exacerbar o distorsionar</b>',
         '❌ La reducción a <i>"las mujeres ganan X % menos"</i> pierde el '
         '<i>"en esta muestra y sin controlar por otros factores"</i>. '
         'La afirmación se vuelve una generalización causal que el informe '
         '<b>no sostiene</b>.'),
        ('<b>Difusión ONG</b>',
         'Narrativa con cifras apoyando una causa',
         'Advocar, movilizar, emocionar',
         '⚠️ Permite limitaciones pero tiende a subordinarlas al mensaje. '
         'El informe soporta una afirmación descriptiva bivariada, que en '
         'un artículo de difusión queda diluida.'),
        ('<b>Reporte técnico / publicación científica</b>',
         'Resultado numérico, IC, test, tamaño del efecto, '
         '<b>limitaciones explícitas</b>',
         'Precisión, reproducibilidad, nuance',
         '✅ Es <b>exactamente</b> el envase que pide el contenido del '
         'informe. El medio <i>espera</i> y <i>celebra</i> las limitaciones '
         'en vez de castigarlas.'),
    ]
    cuerpo = ''.join(
        f'<tr><td>{m}</td><td>{a}</td><td class="muted">{t}</td><td>{e}</td></tr>'
        for m, a, t, e in filas
    )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Medio</th>'
        '<th>Qué afirma con honestidad</th>'
        '<th>Tendencia habitual</th>'
        '<th>¿Encaja?</th>'
        '</tr></thead>'
        f'<tbody>{cuerpo}</tbody></table>'
    )


# ============================================================
# HTML
# ============================================================

html = f"""<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<title>AyVD Parte 2 — Inferencia sobre la diferencia de medias</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{
    delimiters: [
      {{left: '$$', right: '$$', display: true}},
      {{left: '\\\\(', right: '\\\\)', display: false}}
    ],
    throwOnError: false
  }});"></script>
<style>
  :root {{
    --bg:#FAFBFC; --card:#FFFFFF; --border:#E6E8EF;
    --text:#2E3440; --muted:#5E6472; --accent:#5B8DEF; --soft:#F5F7FB;
  }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; padding:0; }}
  body {{
    font-family:-apple-system,"Segoe UI",Inter,system-ui,sans-serif;
    background:var(--bg); color:var(--text); line-height:1.6;
  }}
  header {{
    background:linear-gradient(135deg,#EEF3FB,#F8FAFF);
    padding:44px 40px 28px; border-bottom:1px solid var(--border);
  }}
  header h1 {{ margin:0 0 8px; font-size:1.85rem; letter-spacing:-.01em; }}
  header .sub {{ color:var(--muted); font-size:.95rem; margin-top:2px; }}
  main {{ max-width:1100px; margin:0 auto; padding:32px 40px 72px; }}
  h2 {{
    margin-top:44px; padding-bottom:8px;
    border-bottom:2px solid var(--accent); font-size:1.35rem;
  }}
  h3 {{ margin-top:24px; font-size:1.05rem; color:#3A63A8; }}
  .card {{
    background:var(--card); border:1px solid var(--border);
    border-radius:12px; padding:22px 26px; margin:18px 0;
  }}
  .nota {{
    background:var(--soft); border-left:3px solid var(--accent);
    padding:12px 16px; margin:12px 0; border-radius:0 6px 6px 0;
    color:var(--muted); font-size:.92rem;
  }}
  table {{
    width:100%; border-collapse:collapse;
    font-size:.88rem; margin:14px 0;
  }}
  th,td {{
    text-align:left; padding:9px 12px;
    border-bottom:1px solid var(--border);
    vertical-align:top;
  }}
  th {{
    background:var(--soft); color:var(--muted); font-weight:600;
    text-transform:uppercase; font-size:.72rem; letter-spacing:.05em;
  }}
  td.num, .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.muted, .muted {{ color:var(--muted); font-size:.86rem; }}
  table.filtros td:first-child {{ font-weight:600; white-space:nowrap; }}
  ol li, ul li {{ margin:8px 0; }}
  code {{
    background:var(--soft); padding:1px 6px; border-radius:4px;
    font-size:.87em; color:#3A63A8;
  }}
  .chart {{
    background:var(--card); border:1px solid var(--border);
    border-radius:12px; padding:14px 14px 6px 14px; margin:18px 0;
    position:relative;
  }}
  .chart-id {{
    text-align:right;
    font-size:.78rem;
    color:var(--muted);
    font-family:"JetBrains Mono",Consolas,monospace;
    padding:6px 6px 2px 0;
    letter-spacing:.05em;
  }}
  footer {{
    text-align:center; padding:28px; color:var(--muted);
    font-size:.82rem; border-top:1px solid var(--border);
  }}
  .resumen {{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:14px; margin:16px 0;
  }}
  .metric {{
    background:var(--soft); border-radius:10px; padding:14px 18px;
    border:1px solid var(--border);
  }}
  .metric .label {{
    color:var(--muted); font-size:.78rem;
    text-transform:uppercase; letter-spacing:.05em;
  }}
  .metric .value {{
    font-size:1.4rem; font-weight:700; margin-top:4px; color:#3A63A8;
  }}
  .formula {{
    background:var(--soft); border-left:3px solid var(--accent);
    border-radius:0 6px 6px 0;
    padding:14px 18px; margin:14px 0;
    text-align:center;
    color:#2E3440;
    overflow-x:auto;
  }}
  .formula .katex {{ font-size:1.05em; }}
  .pdflink {{
    display:inline-block; background:var(--accent); color:white;
    padding:10px 18px; border-radius:8px; text-decoration:none;
    font-weight:600; margin:10px 0;
  }}
  .pdflink:hover {{ background:#3A63A8; }}
</style>
</head>
<body>

<header>
  <h1>Análisis y Visualización de Datos — Parte 2</h1>
  <div class="sub">Diplomatura en Ciencia de Datos 2026 · FAMAF, UNC</div>
  <div class="sub">Alumno: Rubén Rasi · Docente: Fredy Alexander Restrepo Blandon</div>
  <div class="sub">Inferencia sobre la diferencia de medias del sueldo NETO entre varones cis y mujeres cis</div>
</header>

<main>

<div class="card">
  <h3>0.  Enfoque general y continuidad con parte 1</h3>
  <p>Este informe retoma el dataset Sysarmy 2026 ya trabajado en la
  parte 1 y avanza hacia la <b>inferencia</b>: estimación puntual y
  por intervalo de la diferencia de medias, test de hipótesis sobre
  esa diferencia y comunicación del resultado en un formato acorde a
  lo que el análisis permite afirmar con honestidad. Los grupos
  analíticos son los que pide la consigna: <b>Varón cis</b> y
  <b>Mujer cis</b>.</p>
  <div class="nota">
    <b>Vocabulario inferencial usado a lo largo del informe.</b> Se
    evita decir que los datos <i>prueban</i> o <i>confirman</i> nada.
    Se usan expresiones como <i>"los datos son incompatibles con H₀"</i>,
    <i>"el IC del 95 % del procedimiento cubre el parámetro en el 95 % de
    las muestras"</i> y <i>"el p-valor es la probabilidad de observar
    una diferencia tan o más extrema bajo H₀"</i>. La distinción importa
    porque preserva el alcance real de las conclusiones.
  </div>
</div>

<h2>1.  Filtrado y grupos analíticos</h2>

<div class="card">
  <h3>1.1  Filtros heredados de parte 1 y ajuste propio de parte 2</h3>
  <p>Se reutilizan los filtros <b>F1, F2, F3 y F5</b> de parte 1 para
  mantener la misma base muestral. Se agrega un <b>techo simétrico</b>
  de 15 000 000 ARS aplicado a <u>ambos grupos</u>: la consigna lo
  aplica sólo a <code>groupA</code> (varones), lo que contaminaría la
  diferencia de medias con un recorte asimétrico. Se omite el filtro
  F4 de parte 1 (Tukey 1,5·IQR estratificado por moneda) porque los
  tests necesitan ver la varianza legítima de la cola para calibrar
  correctamente el IC y los p-valores: recortarla sería esconder
  información al procedimiento.</p>
  {tabla_filtros_html()}
  <div class="nota">
    <b>Piso SMVM.</b> El piso de 300 000 ARS reemplaza al piso de 100 000
    que usa la consigna. El valor 100 000 está por debajo del salario
    mínimo argentino 2026 y captura mayoritariamente respuestas
    erróneas o casos mal clasificados como Full-Time.
  </div>
</div>

<div class="resumen">
  <div class="metric"><div class="label">N inicial</div><div class="value">{N_INICIAL}</div></div>
  <div class="metric"><div class="label">N final (filtrado)</div><div class="value">{N_FINAL}</div></div>
  <div class="metric"><div class="label">n_A Varón cis</div><div class="value">{nA}</div></div>
  <div class="metric"><div class="label">n_B Mujer cis</div><div class="value">{nB}</div></div>
</div>

<div class="card">
  <h3>1.2  Estadísticos descriptivos por grupo</h3>
  <p>Primer vistazo a los dos grupos antes de entrar al procedimiento
  inferencial. Las medianas se reportan para que el lector compare
  contra las medias y detecte asimetrías.</p>
  {tabla_descriptivos_html()}
</div>

<div class="chart">{fig_div(fig_g1)}<div class="chart-id">G1</div></div>
<div class="chart">{fig_div(fig_g2)}<div class="chart-id">G2</div></div>

<h2>2.  Ejercicio 1 — Estimación puntual e intervalo de confianza</h2>

<div class="card">
  <h3>2.1  Estimador puntual</h3>
  <p>El estimador puntual para la diferencia de medias poblacionales
  es la diferencia de medias muestrales (Clase 03 — Estimación
  puntual):</p>
  <div class="formula">$$\\widehat{{\\Delta}} = \\bar{{X}}_A - \\bar{{X}}_B$$</div>
  <p>Es insesgado y de mínima varianza para estimar la diferencia
  de medias poblacionales. En esta muestra el estimador puntual
  toma el valor <b>{fmt_ars(delta_hat)}</b>, computado como
  {fmt_ars(mediaA)} − {fmt_ars(mediaB)}.</p>
</div>

<div class="card">
  <h3>2.2  Intervalo de confianza por Welch</h3>
  <p>Dado que los dos grupos tienen tamaños muestrales muy distintos
  (<i>n<sub>A</sub></i> = {nA}, <i>n<sub>B</sub></i> = {nB}) y
  varianzas muestrales también distintas
  (<i>s<sub>A</sub></i> = {fmt_ars(sA)},
  <i>s<sub>B</sub></i> = {fmt_ars(sB)}), el IC se construye con el
  procedimiento de <b>Welch</b> usando los grados de libertad de
  <b>Satterthwaite</b>:</p>
  <div class="formula">$$\\widehat{{\\Delta}} \\pm t_{{\\alpha/2,\\;\\nu_W}}\\,\\sqrt{{\\frac{{s_A^2}}{{n_A}} + \\frac{{s_B^2}}{{n_B}}}}$$</div>
  <div class="formula">$$\\nu_W = \\frac{{\\left(s_A^2/n_A + s_B^2/n_B\\right)^2}}{{\\dfrac{{(s_A^2/n_A)^2}}{{n_A-1}} + \\dfrac{{(s_B^2/n_B)^2}}{{n_B-1}}}}$$</div>
  <p>La elección de Welch sobre el t de Student pooled sigue la
  recomendación del link del propio profesor (Lakens, 2015): usar
  Welch por defecto salvo que haya razones fuertes para asumir
  igualdad de varianzas.</p>
</div>

<div class="card">
  <h3>2.3  IC por bootstrap percentil (verificación de robustez)</h3>
  <p>Como control de robustez se calcula también un IC del 95 % por
  <b>bootstrap percentil</b>: 10 000 resamples con reposición de cada
  grupo (semilla fija para reproducibilidad), se computa la diferencia
  de medias en cada remuestreo y el IC son los percentiles 2,5 y 97,5
  de la distribución empírica. Si el IC paramétrico y el bootstrap son
  similares, la aproximación de Welch es razonable para estos tamaños
  muestrales.</p>
  {tabla_ic_html()}
  <div class="nota">
    La similitud entre ambos IC indica que la aproximación a la t de
    Student usada por Welch es adecuada para estos tamaños. El
    bootstrap se reporta como <b>verificación</b>, no como reemplazo.
  </div>
</div>

<div class="chart">{fig_div(fig_g4)}<div class="chart-id">G4</div></div>

<div class="card">
  <h3>2.4  Relación IC ↔ test de hipótesis</h3>
  <p>Un IC del (1 − α) para la diferencia de medias poblacionales
  está en <b>dualidad exacta</b> con el test bilateral al nivel α
  para la hipótesis nula de igualdad de medias. Concretamente:</p>
  <div class="formula">$$0 \\notin \\text{{IC}}_{{1-\\alpha}} \\;\\;\\Longleftrightarrow\\;\\; \\text{{se rechaza }} H_0 \\text{{ al nivel }} \\alpha$$</div>
  <p>En este caso el IC del 95 % de Welch es
  <b>[{fmt_ars(ic_welch_low)} , {fmt_ars(ic_welch_high)}]</b> y
  <b>no contiene el 0</b>, por lo que el test bilateral al 5 % del
  ejercicio 2 <b>rechaza</b> <i>H</i><sub>0</sub>. El ejercicio 2
  verifica esta equivalencia numéricamente.</p>
</div>

<h2>3.  Ejercicio 2 — Test de hipótesis</h2>

<h3>3.1  Formalización</h3>

<div class="card">
  <p>Se describe formalmente un test para contrastar si la distribución
  del sueldo NETO difiere entre <code>groupA</code> (Varón cis) y
  <code>groupB</code> (Mujer cis), centrado en la diferencia de
  medias poblacionales:</p>
  <table class="filtros">
    <thead><tr>
      <th>Componente</th><th>Especificación</th>
    </tr></thead>
    <tbody>
      <tr><td>Hipótesis nula</td><td>\\(H_0:\\;\\mu_A - \\mu_B = 0\\) — las medias poblacionales son iguales</td></tr>
      <tr><td>Hipótesis alternativa</td><td>\\(H_1:\\;\\mu_A - \\mu_B \\neq 0\\) — bilateral, sin asumir dirección a priori</td></tr>
      <tr><td>Estadístico (pivote)</td><td>\\(T = \\dfrac{{\\bar{{X}}_A - \\bar{{X}}_B}}{{\\sqrt{{s_A^2/n_A + s_B^2/n_B}}}}\\)</td></tr>
      <tr><td>Distribución bajo \\(H_0\\)</td><td>\\(T \\sim t_{{\\nu_W}}\\) con \\(\\nu_W\\) grados de libertad de Welch–Satterthwaite</td></tr>
      <tr><td>Nivel de significancia</td><td>\\(\\alpha = 0{{,}}05\\) <i>(la consigna lo fija)</i></td></tr>
      <tr><td>Zona de rechazo</td><td>\\(\\{{\\,|T| > t_{{\\alpha/2,\\,\\nu_W}}\\,\\}}\\) — bilateral</td></tr>
    </tbody>
  </table>
  <div class="nota">
    <b>Por qué bilateral.</b> La consigna pregunta si la distribución
    es <i>distinta</i>, sin prejuzgar la dirección. Un test unilateral
    ganaría potencia a costa de no poder detectar sesgos en sentido
    contrario; el bilateral es metodológicamente más honesto cuando no
    hay hipótesis previa.
  </div>
</div>

<div class="chart">{fig_div(fig_g3)}<div class="chart-id">G3</div></div>

<div class="card">
  <p>Los QQ-plots muestran apartamientos de la normal en las colas —
  típico de distribuciones de ingreso—. Por ese motivo el ejercicio
  2.2 suma un test <b>no paramétrico</b> (Mann-Whitney U) como
  verificación de robustez que no depende del supuesto de normalidad.</p>
</div>

<h3>3.2  P-valor, decisión y verificación no paramétrica</h3>

<div class="card">
  {tabla_test_html()}
  <div class="formula">$$\\text{{p-valor bilateral (Welch)}} = {p_bilateral:.3e}$$</div>
  <div class="nota">
    <b>Interpretación cuidada del p-valor.</b> Bajo <i>H</i><sub>0</sub> (medias
    poblacionales iguales), la probabilidad de observar una diferencia
    de medias <b>tan o más extrema</b> que la observada en esta
    muestra es <i>p</i> ≈ {p_bilateral:.2e}. El valor es enormemente
    inferior al nivel α = 0,05 fijado, por lo que los datos
    son <b>incompatibles</b> con <i>H</i><sub>0</sub> al nivel elegido y la hipótesis
    nula se <b>rechaza</b>.
  </div>
  <div class="nota">
    <b>Robustez al supuesto de normalidad.</b> El test de Mann-Whitney
    U —que no asume normalidad— arroja la <b>misma decisión</b> que el
    Welch (<i>p</i> ≈ {p_mwu:.2e}), lo que indica que el resultado no
    es artefacto del supuesto distribucional. Dos procedimientos
    distintos llegan a la misma conclusión cualitativa sobre estos
    datos.
  </div>
</div>

<h3>3.3  Potencia del test</h3>

<div class="card">
  <p>Se calcula el tamaño del efecto (<b>Cohen's d</b>) con desvío
  pooled y se resuelve el tamaño muestral <i>n<sub>A</sub></i> necesario para
  alcanzar potencias convencionales, manteniendo el mismo ratio
  <i>n<sub>B</sub></i>/<i>n<sub>A</sub></i> observado:</p>
  <div class="formula">$$d = \\frac{{\\bar{{X}}_A - \\bar{{X}}_B}}{{s_\\text{{pooled}}}} \\;,\\quad s_\\text{{pooled}} = \\sqrt{{\\frac{{(n_A-1)s_A^2 + (n_B-1)s_B^2}}{{n_A + n_B - 2}}}}$$</div>
  {tabla_potencia_html()}
</div>

<div class="chart">{fig_div(fig_g5)}<div class="chart-id">G5</div></div>

<div class="card">
  <h3>3.4  Interpretación de la potencia</h3>
  <p>La potencia 1 − β es la probabilidad de <b>rechazar <i>H</i><sub>0</sub>
  cuando <i>H</i><sub>1</sub> es cierta</b> (es decir, detectar una diferencia real
  del tamaño asumido). Una potencia alta implica baja probabilidad de
  falso negativo.</p>
  <div class="nota">
    <b>Cuidado con la interpretación inversa.</b> Un test con baja
    potencia que <i>no rechaza</i> <i>H</i><sub>0</sub> <b>no es evidencia de
    igualdad</b>: puede reflejar simplemente que el tamaño muestral es insuficiente
    para detectar la diferencia existente.
  </div>
  <h3>¿Es esta muestra suficiente?</h3>
  <p><b>Para describir una tendencia general</b> en la encuesta: <b>sí,
  con margen</b>. El <i>n<sub>A</sub></i> real ({nA}) supera varias veces el
  necesario para cualquier umbral convencional de potencia. La
  potencia observada al effect size real es prácticamente 1.</p>
  <p><b>Para una causa legal contra una empresa por discriminación
  salarial: no alcanza.</b> En ese contexto harían falta:</p>
  <ol>
    <li><b>Potencia ≥ 0,95</b> y control estricto del error tipo I
    (α ≤ 0,01 o corrección por comparaciones múltiples).</li>
    <li><b>Análisis multivariado</b> que controle por experiencia,
    seniority, especialización, provincia y otras variables
    correlacionadas, para separar el efecto del género del de los
    confounders.</li>
    <li><b>Marco metodológico formal</b>: protocolo preregistrado,
    auditoría de datos, expertos independientes, replicación.</li>
  </ol>
  <p>El test bivariado presentado describe una <b>diferencia en la
  muestra</b>: no establece <b>causalidad por género</b> y no debería
  usarse de manera aislada como prueba en un proceso legal.</p>
</div>

<h2>2.4  Extensión natural a tres grupos analíticos — ANOVA y Kruskal-Wallis</h2>

<div class="card">
  <h3>2.4.1  Justificación de la extensión</h3>
  <p>Hasta acá el contraste se hizo entre los <b>dos grupos</b> que pide
  la consigna (Varón cis vs Mujer cis) usando t de Welch y, como
  verificación no paramétrica, Mann-Whitney U. El docente sumó al
  notebook 05 y a las slides de Test de Hipótesis dos tests para
  <b>k > 2 grupos</b>: <b>ANOVA</b> de un factor (paramétrico) y
  <b>Kruskal-Wallis</b> (no paramétrico, contraparte de Mann-Whitney
  para más de dos grupos).</p>
  <p>Para incorporar ese material de forma honesta —sin reemplazar el
  contenido obligatorio de la consigna— se agrega un tercer grupo
  analítico, <b>Diversidades</b>, que reúne las identidades de género
  minoritarias del formulario (<i>No binarie, Trans, Queer, Lesbiana,
  Agénero, Prefiero no decir</i>) siguiendo la misma agrupación
  respetuosa que se usó en parte 1 (ej 2d / G11). Sobre los <b>tres</b>
  grupos se aplican ANOVA y Kruskal-Wallis como tests <b>omnibus</b>:
  contrastan si <i>alguna</i> diferencia entre los grupos existe, sin
  identificar cuál par difiere.</p>
  <div class="nota">
    <b>Por qué no aplicar KW sobre 2 grupos.</b> Para 2 grupos,
    Kruskal-Wallis es matemáticamente equivalente a Mann-Whitney U y
    ANOVA es matemáticamente equivalente al t de Student pooled. Sumar
    un tercer grupo (Diversidades) es lo que justifica realmente usar
    estos métodos.
  </div>
</div>

<div class="card">
  <h3>2.4.2  Estadísticos descriptivos sobre los tres grupos</h3>
  <table class="filtros">
    <thead><tr>
      <th>Grupo</th><th>n</th><th>media</th><th>mediana</th><th>desvío std</th>
    </tr></thead>
    <tbody>
      <tr><td>groupA — Varón cis</td>
          <td class="num">{nA}</td>
          <td class="num">{fmt_ars(mediaA)}</td>
          <td class="num">{fmt_ars(medianaA)}</td>
          <td class="num">{fmt_ars(sA)}</td></tr>
      <tr><td>groupB — Mujer cis</td>
          <td class="num">{nB}</td>
          <td class="num">{fmt_ars(mediaB)}</td>
          <td class="num">{fmt_ars(medianaB)}</td>
          <td class="num">{fmt_ars(sB)}</td></tr>
      <tr><td>groupD — Diversidades</td>
          <td class="num">{nD}</td>
          <td class="num">{fmt_ars(mediaD)}</td>
          <td class="num">{fmt_ars(medianaD)}</td>
          <td class="num">{fmt_ars(sD)}</td></tr>
    </tbody>
  </table>
</div>

<div class="card">
  <h3>2.4.3  ANOVA de un factor (paramétrico)</h3>
  <p>Hipótesis y formalización:</p>
  <ul>
    <li><b>H<sub>0</sub></b>: μ<sub>A</sub> = μ<sub>B</sub> = μ<sub>D</sub>
    — las tres medias poblacionales son iguales</li>
    <li><b>H<sub>1</sub></b>: al menos una de las medias difiere de las
    otras (sin especificar cuál)</li>
    <li><b>Estadístico</b>: F de Snedecor — cociente entre la varianza
    <i>entre</i> grupos y la varianza <i>dentro</i> de los grupos</li>
  </ul>
  <div class="formula">$$F = \\frac{{\\text{{MSB}}}}{{\\text{{MSW}}}} \\;\\;\\sim\\;\\; F_{{(k-1,\\;N-k)}} \\text{{ bajo }} H_0$$</div>
  <table class="filtros">
    <thead><tr><th>Métrica</th><th>Valor</th></tr></thead>
    <tbody>
      <tr><td>k (grupos)</td><td class="num">3</td></tr>
      <tr><td>N total</td><td class="num">{N_total_3g}</td></tr>
      <tr><td>grados de libertad ν<sub>1</sub> = k − 1</td><td class="num">{gl_entre}</td></tr>
      <tr><td>grados de libertad ν<sub>2</sub> = N − k</td><td class="num">{gl_dentro}</td></tr>
      <tr><td>F observado</td><td class="num"><b>{F_anova:.4f}</b></td></tr>
      <tr><td>P-valor</td><td class="num"><b>{p_anova:.3e}</b></td></tr>
      <tr><td>Decisión al α = 0,05</td>
          <td class="num"><b style="color:#C96C6C">se rechaza H<sub>0</sub></b></td></tr>
    </tbody>
  </table>
</div>

<div class="card">
  <h3>2.4.4  Kruskal-Wallis (no paramétrico)</h3>
  <p>Test no paramétrico análogo a Mann-Whitney U para más de dos
  grupos. Trabaja sobre <b>rangos</b>, no sobre los valores en sí, por
  lo que no asume normalidad. Bajo el supuesto adicional de que las
  distribuciones de los grupos tienen la misma forma, el test contrasta
  si las <b>medianas</b> son iguales (es el framing que usa el docente
  en el notebook 05).</p>
  <ul>
    <li><b>H<sub>0</sub></b>: las distribuciones (o, equivalentemente,
    las medianas) de los tres grupos son iguales</li>
    <li><b>H<sub>1</sub></b>: al menos un grupo presenta una
    distribución estocásticamente distinta</li>
  </ul>
  <table class="filtros">
    <thead><tr><th>Métrica</th><th>Valor</th></tr></thead>
    <tbody>
      <tr><td>k (grupos)</td><td class="num">3</td></tr>
      <tr><td>H observado (estadístico de Kruskal-Wallis)</td>
          <td class="num"><b>{H_kw:.4f}</b></td></tr>
      <tr><td>grados de libertad k − 1</td><td class="num">{gl_entre}</td></tr>
      <tr><td>P-valor</td><td class="num"><b>{p_kw:.3e}</b></td></tr>
      <tr><td>Decisión al α = 0,05</td>
          <td class="num"><b style="color:#C96C6C">se rechaza H<sub>0</sub></b></td></tr>
    </tbody>
  </table>
</div>

<div class="chart">{fig_div(fig_g6)}<div class="chart-id">G6</div></div>

<div class="card">
  <h3>2.4.5  Lectura conjunta y limitaciones del enfoque omnibus</h3>
  <p><b>Ambos tests rechazan H<sub>0</sub> al nivel α = 0,05</b>, lo que
  refuerza el resultado por dos vías independientes: una paramétrica
  (ANOVA, sensible a diferencias de medias y dependiente del supuesto
  de normalidad) y una no paramétrica (Kruskal-Wallis, basada en
  rangos, sin supuestos distribucionales). El patrón es el mismo que
  se observó en la sección 2.2 con Welch y Mann-Whitney sobre dos
  grupos: dos procedimientos distintos arrojan la misma decisión
  cualitativa, lo que indica que el resultado es robusto al supuesto
  de normalidad.</p>
  <div class="nota">
    <b>Tests omnibus: lo que SÍ y lo que NO dicen.</b> ANOVA y
    Kruskal-Wallis son tests <i>omnibus</i>: rechazar H<sub>0</sub>
    significa que <i>alguna</i> diferencia entre los k grupos existe,
    pero <b>no</b> identifican cuál par difiere. Para responder eso
    haría falta aplicar tests <i>post-hoc</i> (Tukey HSD para ANOVA,
    Dunn para Kruskal-Wallis, con corrección de Bonferroni o Holm).
    El material de la materia <b>no incluye</b> tests post-hoc, por lo
    que no se aplican aquí: la identificación de los pares se hace
    cualitativamente comparando las medias y medianas de la tabla
    2.4.2, y para el par específico Varón cis vs Mujer cis ya tenemos
    el contraste directo del test de Welch en 2.2.
  </div>
  <div class="nota">
    <b>Cuidado con las medianas observadas.</b> En la muestra, la
    media del grupo Diversidades ({fmt_ars(mediaD)}) es <i>mayor</i>
    que la de Varón cis ({fmt_ars(mediaA)}), y la de Mujer cis es la
    más baja. La interpretación de esa observación requeriría
    considerar el bajo n del grupo Diversidades (n = {nD}), la
    composición interna de la categoría (donde <i>Prefiero no decir</i>
    es el componente más numeroso) y posibles confounders sobre los
    cuales este análisis bivariado no controla.
  </div>
</div>

<h2>4.  Ejercicio 3 — Comunicación y visualización</h2>

<div class="card">
  <h3>4.1  Elección del medio: reporte técnico / publicación científica</h3>
  <p>La elección del medio no es por gusto sino por
  <b>compatibilidad entre lo que el informe puede afirmar con
  honestidad y lo que cada medio típicamente hace con las cifras</b>.
  Las tres alternativas que plantea la consigna se evalúan abajo:</p>
  {tabla_eleccion_ej3_html()}
  <div class="nota">
    <b>La opción 2 es la única que permite comunicar exactamente lo
    que los datos soportan, sin exagerar ni subestimar.</b> Las otras
    dos forzarían distorsión para encajar en sus convenciones: la
    primera tiende a reducir un resultado bivariado a una
    generalización causal ("las mujeres ganan X % menos"), y la
    segunda tiende a subordinar las limitaciones técnicas al mensaje
    movilizador. Un reporte técnico celebra las limitaciones en vez
    de castigarlas.
  </div>
</div>

<div class="card">
  <h3>4.2  PDF del ejercicio 3</h3>
  <p>El PDF entregado es una página A4 autocontenida en formato
  reporte técnico. Contiene:</p>
  <ul>
    <li><b>Título y resumen</b> con la cifra central (Δ̂,
    IC 95 %, p-valor, tamaño del efecto).</li>
    <li><b>Figura principal</b>: forest plot con la diferencia estimada
    y los dos intervalos (Welch y bootstrap) lado a lado.</li>
    <li><b>Tabla técnica</b> con <i>n</i>, medias, desvíos, <i>t</i>, ν,
    p-valor, Mann-Whitney <i>U</i>, Cohen's d y potencia.</li>
    <li><b>Limitaciones</b> con cuatro bullets: análisis bivariado,
    sesgo de autoselección, filtros declarados, implicancia legal.</li>
    <li><b>Oración con énfasis</b> que resume el mensaje central
    respetando el alcance real del análisis.</li>
  </ul>
  <p><a class="pdflink" href="comunicacion_ej3.pdf" target="_blank">📄 Abrir comunicacion_ej3.pdf</a></p>
</div>

<h2>5.  Conclusiones</h2>

<div class="card">
  <ol>
    <li>Sobre la muestra filtrada (n_A = {nA} varones cis, n_B = {nB}
    mujeres cis) con los filtros F1–F6 declarados, se estima una
    diferencia de medias del sueldo NETO mensual de
    <b>{fmt_ars(delta_hat)}</b> con IC 95 % de Welch
    <b>[{fmt_ars(ic_welch_low)} , {fmt_ars(ic_welch_high)}]</b>. El IC
    por bootstrap percentil arroja un resultado prácticamente
    idéntico, lo que respalda la adecuación del procedimiento
    paramétrico a estos tamaños muestrales.</li>

    <li>El test de Welch rechaza <i>H</i><sub>0</sub>: <i>μ<sub>A</sub></i> = <i>μ<sub>B</sub></i> al nivel
    α = 0,05 con un p-valor bilateral de
    ≈ {p_bilateral:.2e}. El test no paramétrico de
    Mann-Whitney U llega a la misma decisión cualitativa, lo que
    indica que el resultado es robusto al supuesto de normalidad. El
    IC del 95 % no contiene el valor 0, en línea con la dualidad
    exacta entre IC y test bilateral.</li>

    <li>El tamaño del efecto Cohen's d = {cohens_d:.3f} describe una
    diferencia moderada. La potencia observada con el <i>n<sub>A</sub></i> real es
    prácticamente 1: la muestra es holgada para describir la tendencia
    general en la encuesta.</li>

    <li>El resultado describe una <b>diferencia en esta muestra</b>
    entre los dos grupos considerados: no establece causalidad por
    género y no controla por variables correlacionadas (experiencia,
    seniority, especialización, provincia). Un análisis multivariado
    excedería el alcance metodológico de este entregable y se reserva
    como trabajo futuro.</li>

    <li>La comunicación del resultado se hace en formato reporte
    técnico (opción 2 de la consigna) porque es el único medio que
    permite incluir las limitaciones explícitas que el informe
    sostiene, sin reducirlas a un slogan ni subordinarlas a una
    narrativa movilizadora.</li>
  </ol>
</div>

</main>

<footer>
  Generado con Python · Plotly · KaTeX ·
  código en <code>generar_informe.py</code>
</footer>

</body>
</html>
"""

OUTPUT_HTML.write_text(html, encoding='utf-8')

print(f'\n=== HTML generado ' + '=' * 55)
print(f'archivo: {OUTPUT_HTML}')
print(f'tamaño:  {OUTPUT_HTML.stat().st_size / 1024:.1f} KB')
