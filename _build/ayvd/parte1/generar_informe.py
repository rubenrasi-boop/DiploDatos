#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entregable AyVD — Parte 1
Diplomatura en Ciencia de Datos 2026 — FAMAF, UNC

Alumno:  Rubén Rasi
Docente: Fredy Alexander Restrepo Blandon

Ejercicios cubiertos:
    1.  ¿Cuáles son los lenguajes de programación asociados a los mejores
        salarios?
    2a. Densidad conjunta con 3 numéricas y 2 categóricas.
    2b. Asociación: correlación entre sueldo BRUTO y sueldo NETO.
    2c. Densidad condicional: sueldo según nivel de estudio.
    2d. Densidad conjunta condicional: experiencia vs sueldo coloreada
        por categoría (seniority, género).

Uso:
    python generar_informe.py
        Imprime por consola los cuadros y estadísticos que se muestran
        en el informe HTML, y escribe informe_parte1.html en el mismo
        directorio.
"""

from __future__ import annotations

import colorsys
import math
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pd.set_option('display.width', 130)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 60)


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'sysarmy_survey_2026_processed.csv'
OUTPUT_HTML = BASE_DIR / 'informe_parte1.html'

# Umbral mínimo de observaciones para mostrar un lenguaje en el ranking.
# Regla práctica convencional: con n ≥ 30 cada cuartil (Q1, Q3) contiene
# ~7-8 observaciones y resulta razonablemente estable. No descarta datos:
# es una exclusión de visualización (ver sección 1.5).
N_MIN_LENGUAJE = 30

# Paleta clara con contraste suave pero perceptible
PALETA = ['#5B8DEF', '#6BBF80', '#E8A04F', '#C96C6C',
          '#9673C0', '#4BAFB0', '#C78EB0', '#8C99AD',
          '#D6A35C', '#70A9A1', '#A4B8D3', '#B8868B']
COLOR_BASE = '#5B8DEF'
COLOR_GRID = '#E6E8EF'
COLOR_TEXTO = '#2E3440'
BG_PLOT = '#FAFBFC'


def tonalidad_oscura(color_hex: str, factor: float = 0.42) -> str:
    """Versión más oscura del color (reduce lightness en HLS).
    Se usa para los puntos del violin plot G2 para que contrasten
    contra el violin semi-transparente y el fondo blanco."""
    rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) / 255
                for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l_nueva = max(0.0, l * (1 - factor))
    r, g, b = colorsys.hls_to_rgb(h, l_nueva, s)
    return '#{:02x}{:02x}{:02x}'.format(
        int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
    )


PALETA_OSCURA = [tonalidad_oscura(c) for c in PALETA]


def titulo(texto: str) -> None:
    print(f'\n=== {texto} ' + '=' * max(0, 70 - len(texto)))


# ============================================================
# 1.0  Carga del conjunto de datos
# ============================================================

df = pd.read_csv(DATA_PATH)
N_INICIAL = len(df)

titulo('1.0  Carga')
print(f'archivo:          {DATA_PATH.name}')
print(f'filas iniciales:  {N_INICIAL}')
print(f'columnas totales: {len(df.columns)}')


# ============================================================
# 1.1  Selección de columnas relevantes
# ============================================================
# Se retienen únicamente las variables necesarias para el ejercicio.

COLUMNAS_RELEVANTES = [
    'tools_programming_languages',   # variable explicativa ej 1
    'salary_monthly_NETO',           # variable respuesta principal
    'salary_monthly_BRUTO',          # segunda variable de sueldo (2b)
    'salary_in_usd',                 # tipo de dolarización (ej 1)
    'work_dedication',               # filtro de homogeneidad
    'work_contract_type',            # filtro de homogeneidad
    'profile_years_experience',      # ej 2a, 2d
    'profile_age',                   # ej 2a
    'work_seniority',                # ej 2a, 2d
    'profile_studies_level',         # ej 2c
    'profile_studies_level_state',   # ej 2c
    'profile_gender',                # ej 2a, 2d
]
df = df[COLUMNAS_RELEVANTES].copy()

titulo('1.1  Columnas retenidas')
print(pd.DataFrame({'columna': COLUMNAS_RELEVANTES}))


# ============================================================
# 1.2  Análisis de la variable sueldo y su dolarización
# ============================================================
# Se ejecuta antes del filtrado: define cómo interpretar la columna
# respuesta y cómo se estratifica el análisis por grupo de moneda.

# Se preserva el valor literal de salary_in_usd. Los NaN representan a
# respondentes que no declararon ninguna forma de dolarización; la
# columna booleana sueldo_dolarizado del dataset los codifica como
# False (coincidencia exacta con los NaN). Por lo tanto el grupo NaN
# se interpreta como "cobra 100 % en pesos" y se etiqueta como
# 'Cobro en pesos (NaN)'.
df['moneda_categoria'] = df['salary_in_usd'].fillna('Cobro en pesos (NaN)')

orden_cats = [
    'Cobro en pesos (NaN)',
    'Mi sueldo está dolarizado (pero cobro en moneda local)',
    'Cobro parte del salario en dólares',
    'Cobro todo el salario en dólares',
]
resumen_moneda = (
    df.groupby('moneda_categoria')['salary_monthly_NETO']
    .agg(n='count',
         mediana='median',
         q1=lambda x: x.quantile(.25),
         q3=lambda x: x.quantile(.75))
    .reindex(orden_cats)
    .round(0)
)

titulo('1.2  Sueldo NETO por valor literal de salary_in_usd')
print(resumen_moneda)

# Grupos analíticos derivados: ARS, USD parcial, USD total. No son
# valores del dataset sino etiquetas para agrupar los 4 estados
# literales en 3 subpoblaciones según la moneda efectiva de cobro.
MAPEO_GRUPO = {
    'Cobro en pesos (NaN)':                                     'ARS',
    'Mi sueldo está dolarizado (pero cobro en moneda local)':   'ARS',
    'Cobro parte del salario en dólares':                       'USD parcial',
    'Cobro todo el salario en dólares':                         'USD total',
}
df['moneda_grupo'] = df['moneda_categoria'].map(MAPEO_GRUPO)

titulo('1.2  Grupos de moneda derivados')
print(df['moneda_grupo'].value_counts().to_frame('n'))


# ============================================================
# 1.3  Limpieza y filtrado progresivo
# ============================================================

filtros_aplicados: List[Dict] = []


def aplicar_filtro(dataframe: pd.DataFrame, nombre: str,
                   motivo: str, mascara: pd.Series) -> pd.DataFrame:
    n_antes = len(dataframe)
    nuevo = dataframe[mascara].copy()
    n_despues = len(nuevo)
    # Kurtosis (Fisher) del sueldo NETO después del filtro — sirve
    # para monitorear la forma de la distribución y verificar que
    # los filtros no alteran significativamente las colas (salvo F4
    # y F5 que sí deben reducirla por diseño).
    kurt = None
    if 'salary_monthly_NETO' in nuevo.columns and len(nuevo) > 3:
        try:
            kurt = round(float(nuevo['salary_monthly_NETO'].kurt()), 2)
        except Exception:
            kurt = None
    filtros_aplicados.append({
        'filtro': nombre,
        'motivo': motivo,
        'n_antes': n_antes,
        'n_despues': n_despues,
        'recorte': n_antes - n_despues,
        'pct': round(100 * (n_antes - n_despues) / n_antes, 1) if n_antes else 0,
        'kurtosis': kurt,
    })
    return nuevo


# Kurtosis basal del sueldo NETO (sin filtros) para la narrativa
kurtosis_inicial = round(
    float(df['salary_monthly_NETO'].dropna().kurt()), 2
)


# F1 — sin lenguaje declarado o sin sueldo NETO
df = aplicar_filtro(
    df,
    'F1 - sin lenguaje o sin sueldo NETO',
    'observaciones sin alguna de las dos variables principales no aportan.',
    df['tools_programming_languages'].notna() & df['salary_monthly_NETO'].notna(),
)

# F2 — solo jornada Full-Time
df = aplicar_filtro(
    df,
    'F2 - solo jornada Full-Time',
    'jornada reducida no es comparable con jornada completa.',
    df['work_dedication'] == 'Full-Time',
)

# F3 — contratos cuyo ingreso es un sueldo mensual
# Se retienen las tres modalidades en las que el respondente cobra un
# sueldo mensual. Se descartan Freelance y Cooperativa porque facturan
# por honorarios, monotributo o participación societaria.
CONTRATOS_VALIDOS = [
    'Staff (planta permanente)',
    'Contractor',
    'Tercerizado (trabajo a través de consultora o agencia)',
]
df = aplicar_filtro(
    df,
    'F3 - contratos con ingreso en forma de sueldo mensual',
    'Se conservan los valores literales "Staff (planta permanente)", '
    '"Contractor" y "Tercerizado (trabajo a través de consultora o '
    'agencia)" de work_contract_type, cuyo ingreso es un sueldo '
    'mensual. Se descartan "Freelance" y "Participación societaria en '
    'una cooperativa" porque facturan por honorarios o participación, '
    'y su ingreso no es directamente comparable con un sueldo NETO.',
    df['work_contract_type'].isin(CONTRATOS_VALIDOS),
)


# F4 — regla de Tukey 1,5·IQR aplicada dentro de cada grupo de moneda
# Para cada grupo se calculan Q1 y Q3 del sueldo NETO y se descartan
# las observaciones fuera de [Q1 − 1,5·IQR, Q3 + 1,5·IQR]. La
# estratificación es necesaria porque ARS, USD parcial y USD total
# tienen medianas naturalmente distintas: un IQR calculado sobre el
# conjunto completo no separaría correctamente los atípicos de cada
# subpoblación.
def mascara_iqr_por_grupo(dframe: pd.DataFrame, col: str, grupo: str) -> pd.Series:
    mask = pd.Series(False, index=dframe.index)
    for _, sub in dframe.groupby(grupo):
        q1, q3 = sub[col].quantile([.25, .75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask.loc[sub.index] = sub[col].between(lo, hi)
    return mask


df = aplicar_filtro(
    df,
    'F4 - valores atípicos con regla 1,5·IQR por grupo de moneda',
    'Se aplica la regla clásica de Tukey [Q1 − 1,5·IQR, Q3 + 1,5·IQR] '
    'al sueldo NETO, calculando Q1, Q3 e IQR por separado dentro de '
    'cada grupo de moneda (ARS, USD parcial, USD total). Un único '
    'cálculo combinado produciría límites demasiado amplios para el '
    'grupo ARS y demasiado estrechos para los grupos USD; la '
    'estratificación permite evaluar cada observación contra el rango '
    'natural de su propia subpoblación.',
    mascara_iqr_por_grupo(df, 'salary_monthly_NETO', 'moneda_grupo'),
)


# F5 — piso de sueldo implausible
PISO_SUELDO_MINIMO = 300_000  # ARS mensuales, orden del SMVM argentino
df = aplicar_filtro(
    df,
    'F5 - piso de sueldo implausible (300.000 ARS)',
    'Se descartan respondentes con sueldo NETO inferior a 300.000 ARS '
    'mensuales. Este umbral es del orden del Salario Mínimo Vital y '
    'Móvil (SMVM) argentino, por debajo del cual un sueldo de tiempo '
    'completo en el sector IT resulta implausible y casi con certeza '
    'corresponde a un error de carga del formulario o una lectura '
    'errónea de la unidad. La regla IQR del F4 no captura estos '
    'valores porque el límite inferior Q1 − 1,5·IQR del grupo ARS '
    'puede caer en valores muy bajos o incluso negativos, y no opera '
    'como piso efectivo.',
    df['salary_monthly_NETO'] >= PISO_SUELDO_MINIMO,
)

N_FINAL = len(df)
df_filtros = pd.DataFrame(filtros_aplicados)

titulo('1.3  Secuencia de filtros aplicados')
print(df_filtros[['filtro', 'n_antes', 'n_despues', 'recorte', 'pct']]
      .to_string(index=False))
print(f'\nN inicial: {N_INICIAL}  →  N final: {N_FINAL}  '
      f'(recorte total {100*(N_INICIAL-N_FINAL)/N_INICIAL:.1f} %)')


# ============================================================
# 1.4  Desanidado de la lista de lenguajes
# ============================================================
# Cada respondente declara una lista separada por comas. Se pasa a
# formato largo: una fila por (persona, lenguaje). Una persona que
# usa N lenguajes contribuye a N grupos distintos.

df_long = df.assign(
    lenguaje=df['tools_programming_languages'].str.split(',')
).explode('lenguaje')
df_long['lenguaje'] = df_long['lenguaje'].str.strip()
df_long = df_long[df_long['lenguaje'].astype(bool)]

PROMEDIO_LENGS = len(df_long) / max(len(df), 1)
freq = df_long['lenguaje'].value_counts()

titulo('1.4  Frecuencias después del desanidado')
print(f'filas tras desanidar:               {len(df_long)}')
print(f'lenguajes por respondente (prom.):  {PROMEDIO_LENGS:.2f}')
print(f'lenguajes únicos detectados:        {len(freq)}')
print('\ntop 15 por frecuencia:')
print(freq.head(15).to_frame('n'))


# ============================================================
# 1.5  Umbral de frecuencia mínima (exclusión de visualización)
# ============================================================
# Es una exclusión de visualización, no un filtro sobre los datos:
# los lenguajes con n < N_MIN_LENGUAJE siguen en df_long.

lenguajes_mostrables = sorted(freq[freq >= N_MIN_LENGUAJE].index.tolist())
n_excluidos = int((freq < N_MIN_LENGUAJE).sum())

titulo(f'1.5  Umbral de visualización (n ≥ {N_MIN_LENGUAJE})')
print(f'incluidos en el ranking:  {len(lenguajes_mostrables)}')
print(f'excluidos de la vista:    {n_excluidos}')

df_rank = df_long[df_long['lenguaje'].isin(lenguajes_mostrables)].copy()


# ============================================================
# 1.6  Coeficiente de variación robusto (clase 02)
# ============================================================
# Extensión robusta del coeficiente de variación definido en la
# filmina de clase 02 ("std/mean, comparable entre distintas v.a.").
# Reemplazando std por IQR y mean por mediana:
#
#   CV_robusto_i  =  100 · IQR_i / mediana_i    [%]
#
# Se utiliza como indicador descriptivo de la dispersión relativa
# del 50 % central respecto al valor central, adaptado a
# distribuciones asimétricas como los sueldos.
#
# Umbral por la regla de Tukey 1,5·IQR (clase 02) aplicada sobre la
# distribución de CV robusto del propio conjunto de lenguajes:
#
#   lenguaje marcado  ⇔  CV_robusto_i  >  Q3(CV) + 1,5 · IQR(CV)
#
# Ambos elementos (CV y regla 1,5·IQR) son citables directamente de
# clase 02 sin introducir herramientas de parte 2.

def resumen_robusto(serie: pd.Series) -> pd.Series:
    q1, mediana, q3 = serie.quantile([.25, .5, .75])
    n = int(serie.count())
    iqr = q3 - q1
    cv_robusto = 100 * iqr / mediana if mediana else np.nan
    return pd.Series({
        'n': n,
        'mediana': mediana,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
        'cv_robusto': cv_robusto,
    })


resumen_global = (
    df_rank.groupby('lenguaje')['salary_monthly_NETO']
    .apply(resumen_robusto).unstack()
    .sort_values('mediana', ascending=False)
)

# Umbral Tukey sobre la distribución de CV robusto del conjunto
cv_q1_set = resumen_global['cv_robusto'].quantile(.25)
cv_q3_set = resumen_global['cv_robusto'].quantile(.75)
cv_iqr_set = cv_q3_set - cv_q1_set
UMBRAL_CV = cv_q3_set + 1.5 * cv_iqr_set
resumen_global['estable'] = resumen_global['cv_robusto'] <= UMBRAL_CV

titulo('1.6  Resumen por lenguaje y CV robusto')
print(f'Q1 CV del conjunto:          {cv_q1_set:.2f} %')
print(f'Q3 CV del conjunto:          {cv_q3_set:.2f} %')
print(f'umbral Tukey (Q3 + 1,5·IQR): {UMBRAL_CV:.2f} %')
print(f'lenguajes marcados:          '
      f'{(~resumen_global["estable"]).sum()}\n')

vista = resumen_global.copy()
for c in ('mediana', 'q1', 'q3', 'iqr'):
    vista[c] = '$ ' + (vista[c] / 1e6).round(2).astype(str) + ' M'
vista['cv_robusto'] = vista['cv_robusto'].round(2).astype(str) + ' %'
vista['estable'] = vista['estable'].map({True: 'sí', False: 'no'})
print(vista.to_string())

marcados = resumen_global[~resumen_global['estable']]

# Resumen segmentado por grupo de moneda (para el gráfico G3)
resumen_por_grupo = (
    df_rank.groupby(['moneda_grupo', 'lenguaje'])['salary_monthly_NETO']
    .agg(n='count', mediana='median').reset_index()
)
resumen_por_grupo = resumen_por_grupo[resumen_por_grupo['n'] >= 10]

titulo('1.6  Mediana por grupo de moneda × lenguaje (n ≥ 10)')
print(resumen_por_grupo
      .sort_values(['moneda_grupo', 'mediana'], ascending=[True, False])
      .to_string(index=False))


# ============================================================
# 1.7  Gráficos (Plotly)
# ============================================================

def layout_claro(fig: go.Figure, titulo_fig: str, alto: int = 460) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo_fig, font=dict(size=15, color=COLOR_TEXTO)),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor='white',
        font=dict(family='-apple-system, Segoe UI, Inter, sans-serif',
                  size=12, color=COLOR_TEXTO),
        margin=dict(l=80, r=40, t=60, b=80),
        height=alto,
    )
    fig.update_xaxes(gridcolor=COLOR_GRID, linecolor=COLOR_GRID, zerolinecolor=COLOR_GRID)
    fig.update_yaxes(gridcolor=COLOR_GRID, linecolor=COLOR_GRID, zerolinecolor=COLOR_GRID)
    return fig


orden_lenguajes = resumen_global.index.tolist()
estables = resumen_global['estable'].to_dict()

# Paleta desaturada para las barras de grupo de moneda (G3)
COLORES_MONEDA = {
    'ARS':         '#7B96C9',   # azul polvo
    'USD parcial': '#D4A574',   # arena
    'USD total':   '#8FB39E',   # salvia
}

# G1 — Ranking por mediana. Los lenguajes con dispersión alta llevan
# asterisco y opacidad reducida.
etiquetas_y = [f'{l} *' if not estables[l] else l for l in orden_lenguajes]
opacidades = [0.45 if not estables[l] else 1.0 for l in orden_lenguajes]
max_mediana_m = float(resumen_global['mediana'].max() / 1e6)
fig_rank = go.Figure(go.Bar(
    x=resumen_global['mediana'] / 1e6,
    y=etiquetas_y,
    orientation='h',
    marker=dict(
        color=resumen_global['mediana'],
        colorscale=[[0, '#CBD9EE'], [1, '#3A63A8']],
        line=dict(color='white', width=1),
        opacity=opacidades,
    ),
    text=[f'$ {v/1e6:.2f} M  (n={int(n)}, CV {cv:.0f} %)'
          for v, n, cv in zip(resumen_global['mediana'],
                              resumen_global['n'],
                              resumen_global['cv_robusto'])],
    textposition='outside',
    hovertemplate=('<b>%{y}</b><br>'
                   'Mediana: $ %{x:.2f} M ARS<extra></extra>'),
))
fig_rank.update_layout(yaxis=dict(autorange='reversed'))
layout_claro(fig_rank,
             'Ranking de lenguajes por sueldo NETO mediano',
             alto=max(420, 32 * len(orden_lenguajes) + 180))
fig_rank.update_xaxes(title='Sueldo NETO mediano (millones de ARS)',
                      range=[0, max_mediana_m * 1.55])
fig_rank.update_yaxes(title='')
_n_marcados_g1 = int((~resumen_global['estable']).sum())
if _n_marcados_g1 > 0:
    _anot_g1 = (f'*  CV robusto (IQR/mediana) atípico en el ranking: '
                f'supera {UMBRAL_CV:.0f} % (regla Tukey 1,5·IQR)')
else:
    _anot_g1 = (f'Criterio aplicado: CV robusto (IQR/mediana) con umbral '
                f'Tukey = {UMBRAL_CV:.0f} %. Ningún lenguaje supera el umbral.')
fig_rank.add_annotation(
    text=_anot_g1,
    xref='paper', yref='paper', x=0, y=-0.08, showarrow=False,
    font=dict(size=10, color='#5E6472'), xanchor='left',
)

# G2 — Violin plot horizontal por lenguaje con tres capas visuales
# coexistiendo en el mismo eje:
#   1) Violin    → densidad (KDE) completa del sueldo por lenguaje
#   2) Puntos    → TODAS las observaciones, con jitter vertical
#   3) Box       → Q1, mediana y Q3, relleno transparente y borde
#                  oscuro — dibujado en un trace SEPARADO go.Box
#                  después del violin para que sus líneas queden
#                  POR DELANTE de los puntos (en una sola trace
#                  go.Violin, Plotly dibuja los puntos encima del
#                  box interno, que es lo contrario de lo que
#                  queremos).
fig_box = go.Figure()

# Capa 1+2: violin con puntos (sin box interno)
# Los puntos usan la paleta oscura (tonalidad_oscura) para contrastar
# con el relleno claro del violin y con el fondo blanco donde caen
# los atípicos, manteniendo la identidad de color de cada lenguaje.
for i, lang in enumerate(orden_lenguajes):
    vals = df_rank[df_rank['lenguaje'] == lang]['salary_monthly_NETO'] / 1e6
    color = PALETA[i % len(PALETA)]
    color_punto = PALETA_OSCURA[i % len(PALETA_OSCURA)]
    es_estable = estables[lang]
    name = lang if es_estable else f'{lang} *'
    fig_box.add_trace(go.Violin(
        x=vals,
        name=name,
        orientation='h',
        line=dict(width=1.2, color=color),
        fillcolor=color,
        opacity=0.40 if es_estable else 0.20,

        # Box interno del violin DESACTIVADO — se dibuja aparte para
        # controlar el z-order.
        box_visible=False,

        # TODOS los puntos individuales, no solo atípicos, en
        # tonalidad más oscura para que contrasten.
        points='all',
        pointpos=0,
        jitter=0.55,
        marker=dict(
            color=color_punto,
            size=5,
            opacity=0.55,
            line=dict(color='white', width=0.3),
        ),

        meanline_visible=False,
        spanmode='hard',
        hoveron='violins+points',
        scalemode='width',
        showlegend=False,
    ))

# Capa 3: box como trace separado go.Box, dibujado DESPUÉS del violin
# (y por lo tanto con z-order superior). Relleno transparente y borde
# gris oscuro (suave pero contrastante, equivalente al contraste de
# los puntos contra el violin).
COLOR_BOX_G2 = '#5E6472'  # gris pizarra
for i, lang in enumerate(orden_lenguajes):
    vals = df_rank[df_rank['lenguaje'] == lang]['salary_monthly_NETO'] / 1e6
    es_estable = estables[lang]
    name = lang if es_estable else f'{lang} *'
    fig_box.add_trace(go.Box(
        x=vals,
        name=name,
        orientation='h',
        boxpoints=False,
        fillcolor='rgba(0,0,0,0)',
        line=dict(color=COLOR_BOX_G2, width=1.5),
        width=0.32,
        hoverinfo='skip',
        showlegend=False,
    ))

fig_box.update_layout(
    yaxis=dict(autorange='reversed'),
    violingap=0.12,
    boxgap=0.68,
)
layout_claro(fig_box,
             'Distribución de sueldos NETO por lenguaje',
             alto=max(550, 46 * len(orden_lenguajes) + 160))
fig_box.update_xaxes(title='Sueldo NETO (millones de ARS)')
fig_box.update_yaxes(title='')

# G3 — Mediana por lenguaje y grupo de moneda
pivot = (resumen_por_grupo
         .pivot(index='lenguaje', columns='moneda_grupo', values='mediana')
         .reindex(orden_lenguajes))

fig_grupo = go.Figure()
grupos_orden = [g for g in ['ARS', 'USD parcial', 'USD total']
                if g in pivot.columns]
for g in grupos_orden:
    fig_grupo.add_trace(go.Bar(
        x=pivot.index, y=pivot[g] / 1e6, name=g,
        marker_color=COLORES_MONEDA.get(g, COLOR_BASE),
        marker_line=dict(color='white', width=1),
    ))
fig_grupo.update_layout(
    barmode='group',
    legend=dict(title='Grupo de moneda', orientation='h',
                yanchor='bottom', y=1.02, xanchor='right', x=1),
)
layout_claro(fig_grupo,
             'Sueldo NETO mediano por lenguaje y grupo de moneda',
             alto=480)
fig_grupo.update_yaxes(title='Mediana (millones de ARS)')
fig_grupo.update_xaxes(title='', tickangle=-30)

# G4 — Frecuencia vs mediana, tamaño proporcional al IQR.
etiquetas_g4 = [f'{l} *' if not estables[l] else l for l in resumen_global.index]
fig_nm = go.Figure(go.Scatter(
    x=resumen_global['n'],
    y=resumen_global['mediana'] / 1e6,
    mode='markers+text',
    text=etiquetas_g4,
    textposition='top center',
    textfont=dict(size=10, color=COLOR_TEXTO),
    marker=dict(
        size=np.sqrt(resumen_global['iqr'] / 1e5) * 4 + 8,
        color=resumen_global['mediana'],
        colorscale=[[0, '#CBD9EE'], [1, '#3A63A8']],
        line=dict(color='white', width=1),
        opacity=[1.0 if c else 0.5 for c in resumen_global['estable']],
        showscale=False,
    ),
    hovertemplate=('<b>%{text}</b><br>'
                   'N: %{x}<br>'
                   'Mediana: $ %{y:.2f} M ARS<extra></extra>'),
))
layout_claro(fig_nm,
             'Frecuencia vs sueldo mediano  (tamaño = dispersión IQR)',
             alto=500)
fig_nm.update_xaxes(title='Cantidad de respondentes (escala logarítmica)', type='log')
fig_nm.update_yaxes(title='Sueldo NETO mediano (millones de ARS)')

# G4b — Sueldo NETO según cantidad de lenguajes declarados (nivel persona).
df['n_lenguajes'] = (
    df['tools_programming_languages']
    .fillna('')
    .str.split(',')
    .apply(lambda lst: sum(1 for l in lst if l.strip()))
)
resumen_n_lang = (
    df[df['n_lenguajes'] >= 1]
    .groupby('n_lenguajes')['salary_monthly_NETO']
    .agg(n='count', mediana='median',
         q1=lambda x: x.quantile(.25),
         q3=lambda x: x.quantile(.75))
    .reset_index()
    .sort_values('n_lenguajes')
)
corr_n_lang_pearson = df[['n_lenguajes', 'salary_monthly_NETO']].corr(
    method='pearson').iloc[0, 1]
corr_n_lang_spearman = df[['n_lenguajes', 'salary_monthly_NETO']].corr(
    method='spearman').iloc[0, 1]

n_lang_plot_keys = resumen_n_lang[resumen_n_lang['n'] >= 15]['n_lenguajes'].tolist()
fig_nlang = go.Figure()
for k in n_lang_plot_keys:
    vals = df.loc[df['n_lenguajes'] == k, 'salary_monthly_NETO'].values / 1e6
    fig_nlang.add_trace(go.Box(
        y=vals,
        x=[k] * len(vals),
        name=f'{k}',
        boxpoints=False,
        marker=dict(color='#5B8DEF'),
        line=dict(color='#3A63A8'),
        fillcolor='rgba(91, 141, 239, 0.35)',
        hovertemplate=('n lenguajes: %{x}<br>'
                       'NETO: $ %{y:.2f} M<extra></extra>'),
        showlegend=False,
    ))
medianas_k = [float(np.median(
    df.loc[df['n_lenguajes'] == k, 'salary_monthly_NETO'] / 1e6))
    for k in n_lang_plot_keys]
fig_nlang.add_trace(go.Scatter(
    x=n_lang_plot_keys, y=medianas_k,
    mode='lines+markers',
    line=dict(color='#C96C6C', width=2),
    marker=dict(size=7, color='#C96C6C'),
    name='mediana por conteo',
    hovertemplate=('n lenguajes: %{x}<br>'
                   'mediana: $ %{y:.2f} M<extra></extra>'),
))
layout_claro(fig_nlang,
             'Sueldo NETO según cantidad de lenguajes declarados',
             alto=460)
fig_nlang.update_xaxes(
    title='Cantidad de lenguajes declarados por el respondente',
    tickmode='array', tickvals=n_lang_plot_keys)
fig_nlang.update_yaxes(title='Sueldo NETO (millones de ARS)')

titulo('1.7  Gráficos generados')
print('G1  Ranking de lenguajes por sueldo NETO mediano')
print('G2  Distribución de sueldos NETO por lenguaje')
print('G3  Mediana por lenguaje y grupo de moneda')
print('G4  Frecuencia vs sueldo mediano')
print('G4b Sueldo NETO vs cantidad de lenguajes declarados')
print(f'    corr Pearson: {corr_n_lang_pearson:.3f}  ·  '
      f'Spearman: {corr_n_lang_spearman:.3f}')


# ============================================================
# 1.8  Conclusiones
# ============================================================

top3 = resumen_global.head(3)
mediana_global = resumen_global['mediana'].median()
premio_top = 100 * (top3['mediana'].iloc[0] / mediana_global - 1)

conclusiones = [
    f'Los tres lenguajes con mejor sueldo NETO mediano son: '
    f'{", ".join(top3.index)}.',

    f'{top3.index[0]} encabeza el ranking con una mediana de '
    f'{top3["mediana"].iloc[0]/1e6:.2f} millones de ARS, un '
    f'{premio_top:.0f} % por encima de la mediana del conjunto de '
    f'lenguajes analizados.',

    'El análisis preliminar de la variable sueldo aparenta que la columna '
    'salary_monthly_NETO contiene el total pesificado del sueldo para todos '
    'los respondentes, lo que habilita un ranking único sobre una variable '
    'coherente.',

    'Dentro de cada grupo de moneda el orden entre lenguajes se mantiene '
    'razonablemente estable, pero el salto de ARS a USD total es mayor que '
    'casi cualquier diferencia entre lenguajes dentro del mismo grupo. '
    'Parte del premio observado para algunos lenguajes proviene de la '
    'proporción de sueldos dolarizados en esa población.',

    (f'Aplicando el criterio del coeficiente de variación robusto '
     f'(IQR/mediana) con umbral Tukey sobre el conjunto de lenguajes, '
     f'{len(marcados)} lenguajes del ranking quedan marcados como atípicos '
     f'en dispersión. '
     + ('El conjunto es homogéneo en términos de dispersión relativa: '
        'todos los lenguajes tienen una variabilidad interna comparable '
        'dentro del rango esperable del ranking.'
        if len(marcados) == 0 else
        'Sus posiciones en el ranking deben leerse con reserva porque la '
        'mediana no es representativa del 50 % central.')),
]

titulo('1.8  Conclusiones')
for i, c in enumerate(conclusiones, 1):
    print(f'{i}. {c}')


# ============================================================
# EJERCICIO 2 — Análisis y figuras
# ============================================================
# Se reutiliza df (nivel persona, N = N_FINAL) del ejercicio 1.
# No se desanida la lista de lenguajes.

titulo('2.0  Variables seleccionadas para el ejercicio 2')

VARS_NUMERICAS = ['salary_monthly_NETO',
                  'profile_years_experience',
                  'profile_age']
VARS_CATEGORICAS = ['work_seniority', 'profile_gender']

# Grupos analíticos de género: Hombre Cis, Mujer Cis y una agrupación
# "Diversidades" que reúne las categorías con baja cobertura muestral
# individual (No binarie, Trans, Queer, Agénero, Prefiero no decir).
GENEROS_CIS = ['Hombre Cis', 'Mujer Cis']
CATEGORIAS_DIVERSIDADES = [
    'No binarie', 'Trans', 'Queer', 'Agénero', 'Prefiero no decir',
]
GRUPOS_GENERO = ['Hombre Cis', 'Mujer Cis', 'Diversidades']

ORDEN_ESTUDIOS = [
    'Secundario',
    'Terciario',
    'Universitario',
    'Posgrado/Especialización',
    'Maestría',
    'Doctorado',
    'Posdoctorado',
]

print(f'  numéricas:   {VARS_NUMERICAS}')
print(f'  categóricas: {VARS_CATEGORICAS}')


# --- 2.0.1  Filtro local de edad biológica (sólo ej 2) ---
# profile_age trae algunos valores implausibles (p.ej. 999 años) que
# no fueron removidos en F1-F5 porque la edad no participaba del
# ejercicio 1. Para el ej 2, donde sí se usa como numérica, se aplica
# un filtro LOCAL al tramo laboralmente plausible [15, 80]. El filtro
# NO se propaga al ej 1: el ranking de lenguajes ya está calculado
# sobre df completo.
EDAD_MIN_EJ2 = 15
EDAD_MAX_EJ2 = 80
mask_edad_ej2 = df['profile_age'].between(EDAD_MIN_EJ2, EDAD_MAX_EJ2)
n_antes_ej2 = len(df)
df_ej2 = df[mask_edad_ej2].copy()
n_despues_ej2 = len(df_ej2)
n_descartados_ej2 = n_antes_ej2 - n_despues_ej2
edades_descartadas_ej2 = (
    df.loc[~mask_edad_ej2, 'profile_age']
    .dropna().sort_values(ascending=False).unique().tolist()
)
titulo('2.0.1  Filtro local de edad biológica (sólo ej 2)')
print(f'  tramo retenido: [{EDAD_MIN_EJ2}, {EDAD_MAX_EJ2}] años')
print(f'  N antes:  {n_antes_ej2}')
print(f'  N después:{n_despues_ej2}  ({n_descartados_ej2} descartados)')
if edades_descartadas_ej2:
    print(f'  ejemplos de edades descartadas: '
          + ', '.join(str(int(x)) for x in edades_descartadas_ej2[:6]))


# --- 2.a  Estadísticos y correlaciones ---
describe_num = (
    df_ej2[VARS_NUMERICAS]
    .describe(percentiles=[.10, .25, .50, .75, .90]).round(2)
)
corr_pearson = df_ej2[VARS_NUMERICAS].corr(method='pearson').round(3)
corr_spearman = df_ej2[VARS_NUMERICAS].corr(method='spearman').round(3)

seniority_counts = df['work_seniority'].value_counts().reindex(
    ['Junior', 'Semi-Senior', 'Senior'])
gender_counts = df['profile_gender'].value_counts()

titulo('2.a  Estadísticos de numéricas y correlaciones')
print(describe_num.to_string())
print('\ncorrelación de Spearman:')
print(corr_spearman.to_string())


# --- 2.b  Bruto vs Neto + columna DESCUENTOS (clase 03) ---
bn = df[['salary_monthly_BRUTO', 'salary_monthly_NETO']].dropna()
bn = bn[(bn['salary_monthly_BRUTO'] > 0) & (bn['salary_monthly_NETO'] > 0)]
bn['ratio_neto_bruto'] = bn['salary_monthly_NETO'] / bn['salary_monthly_BRUTO']
# Columna derivada tal como se enseña en el práctico de la clase 03
bn['descuentos'] = bn['salary_monthly_BRUTO'] - bn['salary_monthly_NETO']
bn['descuentos_pct'] = 100 * bn['descuentos'] / bn['salary_monthly_BRUTO']

p_bn = bn[['salary_monthly_BRUTO', 'salary_monthly_NETO']].corr(
    method='pearson').iloc[0, 1]
s_bn = bn[['salary_monthly_BRUTO', 'salary_monthly_NETO']].corr(
    method='spearman').iloc[0, 1]
ratio_mediana = bn['ratio_neto_bruto'].median()
ratio_media = bn['ratio_neto_bruto'].mean()
coef_reg = np.polyfit(bn['salary_monthly_BRUTO'],
                      bn['salary_monthly_NETO'], 1)

desc_mediano = bn['descuentos'].median()
desc_pct_mediano = bn['descuentos_pct'].median()
desc_pct_q1 = bn['descuentos_pct'].quantile(.25)
desc_pct_q3 = bn['descuentos_pct'].quantile(.75)

titulo('2.b  Asociación Bruto vs Neto')
print(f'  n válidos:       {len(bn)}')
print(f'  Pearson:         {p_bn:.4f}')
print(f'  Spearman:        {s_bn:.4f}')
print(f'  ratio mediano:   {ratio_mediana:.4f}')
print(f'  descuentos mediano:         ${desc_mediano:,.0f}'.replace(',', '.'))
print(f'  descuento % mediano:        {desc_pct_mediano:.2f} %')
print(f'  descuento % Q1 - Q3:        {desc_pct_q1:.2f} % - '
      f'{desc_pct_q3:.2f} %')


# --- 2.c  Sueldo por nivel de estudio y subpoblaciones seleccionadas ---
df_estudios = df[df['profile_studies_level'].notna()].copy()
niveles_presentes = [n for n in ORDEN_ESTUDIOS
                     if n in df_estudios['profile_studies_level'].unique()]
describe_estudios = (
    df_estudios.groupby('profile_studies_level')['salary_monthly_NETO']
    .agg(n='count', mediana='median',
         q1=lambda x: x.quantile(.25),
         q3=lambda x: x.quantile(.75))
    .reindex(niveles_presentes)
    .round(0)
)

# Selección de las 2 subpoblaciones más numerosas (consigna literal)
n_por_nivel = (
    df_estudios['profile_studies_level']
    .value_counts()
    .reindex(niveles_presentes)
)
SUBPOB_SELECCIONADAS = (
    n_por_nivel.sort_values(ascending=False).head(2).index.tolist()
)

# Medidas de centralización y dispersión por subpoblación
medidas_subpob = {}
for nivel in SUBPOB_SELECCIONADAS:
    sub = df_estudios[
        df_estudios['profile_studies_level'] == nivel]['salary_monthly_NETO']
    q1, mediana, q3 = sub.quantile([.25, .5, .75])
    medidas_subpob[nivel] = {
        'n':       int(sub.count()),
        'media':   round(sub.mean(), 0),
        'mediana': round(mediana, 0),
        'std':     round(sub.std(), 0),
        'Q1':      round(q1, 0),
        'Q3':      round(q3, 0),
        'IQR':     round(q3 - q1, 0),
    }
tabla_medidas_subpob = pd.DataFrame(medidas_subpob).T


def _fmt_ars(v):
    return f'$ {v:,.0f}'.replace(',', '.')


def _fmt_int(v):
    return f'{int(v)}'


# Tablas HTML con formato correcto: $ sólo en columnas monetarias,
# enteros sin decimal en las columnas de conteo. Se limpia el nombre
# del índice para que pandas no agregue una fila extra con el nombre
# de la columna original (profile_studies_level).
describe_estudios_html = (
    describe_estudios
    .rename_axis(None)
    .to_html(
        classes='datos', border=0,
        formatters={
            'n':       _fmt_int,
            'mediana': _fmt_ars,
            'q1':      _fmt_ars,
            'q3':      _fmt_ars,
        },
    )
)

# Para la tabla de medidas por subpoblación: $ en todas las columnas
# monetarias (media, mediana, std, Q1, Q3, IQR) y entero en 'n'.
# La columna std tiene unidades de ARS (es el desvío estándar de un
# monto en pesos), por lo que también lleva el símbolo $.
tabla_medidas_subpob_html = tabla_medidas_subpob.to_html(
    classes='datos', border=0,
    formatters={
        'n':       _fmt_int,
        'media':   _fmt_ars,
        'mediana': _fmt_ars,
        'std':     _fmt_ars,
        'Q1':      _fmt_ars,
        'Q3':      _fmt_ars,
        'IQR':     _fmt_ars,
    },
)


# Análisis de independencia vía probabilidad condicional (clase 01)
#   A = sueldo NETO > mediana global del subset con estudios declarados
#   B_i = nivel de estudio = subpoblación seleccionada i
# Si fueran independientes, P(A|B_i) ≈ P(A).
sal_todos_est = df_estudios['salary_monthly_NETO']
umbral_mediana_est = sal_todos_est.median()
P_A_est = (sal_todos_est > umbral_mediana_est).mean()

p_cond_subpob = {}
for nivel in SUBPOB_SELECCIONADAS:
    sub = df_estudios[
        df_estudios['profile_studies_level'] == nivel]['salary_monthly_NETO']
    p_cond_subpob[nivel] = (sub > umbral_mediana_est).mean()

titulo('2.c  Sueldo NETO por nivel de estudio')
print(f'  cobertura: {len(df_estudios)}/{len(df)} '
      f'({100*len(df_estudios)/len(df):.1f} %)')
print(describe_estudios.to_string())
print(f'\n  subpoblaciones más numerosas: {SUBPOB_SELECCIONADAS}')
print(f'  P(A) marginal (sueldo > mediana global): {P_A_est:.4f}')
for nivel, p in p_cond_subpob.items():
    print(f'  P(A | {nivel}): {p:.4f}   '
          f'(distancia a P(A): {abs(p - P_A_est):.4f})')


# --- 2.d  Por seniority y por género ---
seniority_stats = (
    df.groupby('work_seniority')['salary_monthly_NETO']
    .agg(n='count', mediana='median',
         q1=lambda x: x.quantile(.25),
         q3=lambda x: x.quantile(.75))
    .reindex(['Junior', 'Semi-Senior', 'Senior'])
    .round(0)
)

def clasificar_genero_analitico(valor):
    if valor in GENEROS_CIS:
        return valor
    if pd.isna(valor):
        return None
    return 'Diversidades'


df_gender = df.copy()
df_gender['genero_grupo'] = df_gender['profile_gender'].apply(
    clasificar_genero_analitico)
df_gender = df_gender[df_gender['genero_grupo'].notna()].copy()

gender_stats = (
    df_gender.groupby('genero_grupo')['salary_monthly_NETO']
    .agg(n='count', mediana='median',
         q1=lambda x: x.quantile(.25),
         q3=lambda x: x.quantile(.75))
    .reindex(GRUPOS_GENERO)
    .round(0)
)

med_hombre = gender_stats.loc['Hombre Cis', 'mediana']
med_mujer = gender_stats.loc['Mujer Cis', 'mediana']
med_diversidades = gender_stats.loc['Diversidades', 'mediana']
ratio_mujer = med_mujer / med_hombre
ratio_diversidades = med_diversidades / med_hombre

titulo('2.d  Seniority y género')
print('por seniority:')
print(seniority_stats.to_string())
print('\npor grupo de género (con "Diversidades" agrupando minorías):')
print(gender_stats.to_string())
print(f'\nbrecha Mujer Cis vs Hombre Cis:   {100*(1-ratio_mujer):.1f} %')
print(f'brecha Diversidades vs Hombre Cis: {100*(1-ratio_diversidades):.1f} %')


# ============================================================
# Figuras del ejercicio 2 (Plotly)
# ============================================================

# --- G5  Histogramas de las 3 numéricas (subplots 1x3) ---
# Edad (años) acotada a [15, 80] porque es edad humana en contexto
# laboral. Nº de bins calibrado por variable para mayor granularidad.
fig_g5 = make_subplots(rows=1, cols=3,
                       subplot_titles=(
                           'Sueldo NETO (millones de ARS)',
                           'Años de experiencia',
                           'Edad (años)'))
fig_g5.add_trace(go.Histogram(
    x=df_ej2['salary_monthly_NETO'] / 1e6, nbinsx=50,
    marker_color='#5B8DEF', marker_line=dict(color='white', width=0.4),
    opacity=0.85, showlegend=False), row=1, col=1)
fig_g5.add_trace(go.Histogram(
    x=df_ej2['profile_years_experience'], nbinsx=40,
    marker_color='#6BBF80', marker_line=dict(color='white', width=0.4),
    opacity=0.85, showlegend=False), row=1, col=2)
fig_g5.add_trace(go.Histogram(
    x=df_ej2['profile_age'], nbinsx=30,
    xbins=dict(start=15, end=80, size=2.2),
    marker_color='#E8A04F', marker_line=dict(color='white', width=0.4),
    opacity=0.85, showlegend=False), row=1, col=3)
layout_claro(fig_g5,
             'Distribución marginal de las 3 variables numéricas',
             alto=360)
fig_g5.update_yaxes(title='frecuencia', row=1, col=1)
fig_g5.update_xaxes(range=[15, 80], row=1, col=3)


# --- G6  Heatmap de correlación (Pearson, coherente con clase 03) ---
# Eje Y invertido para que la diagonal de 1 quede ascendente
# (abajo-izquierda a arriba-derecha), más natural para lectura
# matemática occidental.
corr_pearson_flip = corr_pearson.iloc[::-1]
fig_g6 = go.Figure(go.Heatmap(
    z=corr_pearson_flip.values,
    x=corr_pearson_flip.columns, y=corr_pearson_flip.index,
    colorscale=[[0, '#C96C6C'], [0.5, '#F5F7FB'], [1, '#3A63A8']],
    zmin=-1, zmax=1,
    text=corr_pearson_flip.round(2).values,
    texttemplate='%{text}',
    textfont=dict(size=13, color='#2E3440'),
    colorbar=dict(title='r Pearson'),
))
layout_claro(fig_g6,
             'Matriz de correlación (Pearson) entre numéricas',
             alto=420)
fig_g6.update_xaxes(tickangle=-20)


# --- G7  Distribución de las categóricas (subplots 1x2) ---
# Para género se muestran los tres grupos analíticos definidos en
# 2.d (Hombre Cis, Mujer Cis y Diversidades), coherente con G11.
gender_grupos_counts = (
    df_gender['genero_grupo'].value_counts().reindex(GRUPOS_GENERO)
)
COL_G_GRUPOS = {
    'Hombre Cis':   '#5B8DEF',
    'Mujer Cis':    '#C96C6C',
    'Diversidades': '#9673C0',
}

fig_g7 = make_subplots(rows=1, cols=2,
                       subplot_titles=('Nivel de seniority',
                                       'Grupo de género'))
fig_g7.add_trace(go.Bar(
    x=seniority_counts.index, y=seniority_counts.values,
    marker_color=['#5B8DEF', '#6BBF80', '#E8A04F'],
    marker_line=dict(color='white', width=1),
    showlegend=False,
), row=1, col=1)
fig_g7.add_trace(go.Bar(
    x=gender_grupos_counts.index,
    y=gender_grupos_counts.values,
    marker_color=[COL_G_GRUPOS[g] for g in gender_grupos_counts.index],
    marker_line=dict(color='white', width=1),
    showlegend=False,
), row=1, col=2)
layout_claro(fig_g7,
             'Distribución de las variables categóricas',
             alto=400)


# --- G8  Scatter BRUTO vs NETO con línea de identidad y regresión ---
bn_plot = bn[['salary_monthly_BRUTO', 'salary_monthly_NETO']] / 1e6
lim_g8 = float(bn_plot.values.max()) * 1.02
fig_g8 = go.Figure()
fig_g8.add_trace(go.Scatter(
    x=bn_plot['salary_monthly_BRUTO'], y=bn_plot['salary_monthly_NETO'],
    mode='markers',
    marker=dict(size=5, color='#5B8DEF', opacity=0.35,
                line=dict(width=0)),
    name='observaciones',
    hovertemplate=('BRUTO: %{x:.2f} M<br>'
                   'NETO: %{y:.2f} M<extra></extra>'),
))
fig_g8.add_trace(go.Scatter(
    x=[0, lim_g8], y=[0, lim_g8], mode='lines',
    line=dict(color='#8C99AD', dash='dash', width=1),
    name='identidad (neto = bruto)',
))
xs = np.linspace(0, lim_g8, 100)
fig_g8.add_trace(go.Scatter(
    x=xs, y=coef_reg[0] * xs + coef_reg[1] / 1e6,
    mode='lines', line=dict(color='#C96C6C', width=2),
    name=f'regresión: neto = {coef_reg[0]:.3f} · bruto',
))
layout_claro(fig_g8,
             'Asociación entre sueldo BRUTO y sueldo NETO',
             alto=520)
fig_g8.update_xaxes(title='Sueldo BRUTO mensual (millones de ARS)',
                    range=[0, lim_g8])
fig_g8.update_yaxes(title='Sueldo NETO mensual (millones de ARS)',
                    range=[0, lim_g8])


# --- G9  Histogramas comparativos de 2 subpoblaciones (consigna 2c) ---
# Respuesta literal a la consigna: dos subpoblaciones numerosas,
# histogramas comparativos. Técnica tomada de la clase 03.
col_subpob_g9 = {
    SUBPOB_SELECCIONADAS[0]: '#5B8DEF',
    SUBPOB_SELECCIONADAS[1]: '#C96C6C',
}
fig_g9 = go.Figure()
for nivel in SUBPOB_SELECCIONADAS:
    sub_m = (df_estudios[df_estudios['profile_studies_level'] == nivel]
             ['salary_monthly_NETO'] / 1e6)
    fig_g9.add_trace(go.Histogram(
        x=sub_m,
        name=f'{nivel} (n={len(sub_m)})',
        marker_color=col_subpob_g9[nivel],
        marker_line=dict(color='white', width=0.4),
        opacity=0.55,
        histnorm='probability density',
        nbinsx=30,
    ))
    # marca de mediana de cada subpoblación
    fig_g9.add_vline(
        x=float(sub_m.median()),
        line=dict(color=col_subpob_g9[nivel], width=1.5, dash='dash'),
    )
fig_g9.update_layout(
    barmode='overlay',
    legend=dict(title='subpoblación (línea = mediana)'),
)
layout_claro(fig_g9,
             'Histogramas comparativos del sueldo NETO por nivel de estudio',
             alto=480)
fig_g9.update_yaxes(title='densidad')
fig_g9.update_xaxes(title='Sueldo NETO (millones de ARS)')


# --- G10  Scatter exp vs sueldo con color = seniority + mediana por año ---
# La línea negra conecta la mediana del sueldo para cada año entero
# de experiencia, como una "mediana móvil" descriptiva de la
# tendencia central.
fig_g10 = go.Figure()
col_seniority = {'Junior': '#6BBF80',
                 'Semi-Senior': '#E8A04F',
                 'Senior': '#C96C6C'}
for nivel in ['Junior', 'Semi-Senior', 'Senior']:
    sub = df[df['work_seniority'] == nivel]
    fig_g10.add_trace(go.Scatter(
        x=sub['profile_years_experience'],
        y=sub['salary_monthly_NETO'] / 1e6,
        mode='markers',
        marker=dict(size=6, color=col_seniority[nivel], opacity=0.45,
                    line=dict(width=0)),
        name=f'{nivel} (n={len(sub)})',
        hovertemplate=('Exp: %{x} años<br>NETO: %{y:.2f} M<extra></extra>'),
    ))

# Línea de mediana por año de experiencia
mediana_por_exp_g10 = (
    df.groupby('profile_years_experience')['salary_monthly_NETO']
    .agg(['median', 'count'])
    .reset_index()
)
mediana_por_exp_g10 = mediana_por_exp_g10[mediana_por_exp_g10['count'] >= 5]
fig_g10.add_trace(go.Scatter(
    x=mediana_por_exp_g10['profile_years_experience'],
    y=mediana_por_exp_g10['median'] / 1e6,
    mode='lines+markers',
    line=dict(color='#5E6472', width=1.8),
    marker=dict(size=4.5, color='#5E6472'),
    name='Mediana por año (n ≥ 5)',
    hovertemplate=(
        'Año: %{x}<br>Mediana: $ %{y:.2f} M<extra></extra>'
    ),
))

layout_claro(fig_g10,
             'Experiencia vs sueldo NETO, condicionado por seniority',
             alto=500)
fig_g10.update_xaxes(title='Años de experiencia')
fig_g10.update_yaxes(title='Sueldo NETO (millones de ARS)')


# --- G11  Scatter exp vs sueldo con color = grupo de género ---
fig_g11 = go.Figure()
col_gender = {
    'Hombre Cis':   '#5B8DEF',
    'Mujer Cis':    '#C96C6C',
    'Diversidades': '#9673C0',
}
for g in GRUPOS_GENERO:
    sub = df_gender[df_gender['genero_grupo'] == g]
    fig_g11.add_trace(go.Scatter(
        x=sub['profile_years_experience'],
        y=sub['salary_monthly_NETO'] / 1e6,
        mode='markers',
        marker=dict(size=6, color=col_gender[g], opacity=0.55,
                    line=dict(width=0)),
        name=f'{g} (n={len(sub)})',
        hovertemplate=('Exp: %{x} años<br>NETO: %{y:.2f} M<extra></extra>'),
    ))
layout_claro(fig_g11,
             'Experiencia vs sueldo NETO, condicionado por grupo de género',
             alto=500)
fig_g11.update_xaxes(title='Años de experiencia')
fig_g11.update_yaxes(title='Sueldo NETO (millones de ARS)')

titulo('Figuras del ejercicio 2 generadas')
for nombre in ['G5 - Histogramas de numéricas',
               'G6 - Matriz de correlación',
               'G7 - Categóricas',
               'G8 - BRUTO vs NETO',
               'G9 - Sueldo por nivel de estudio',
               'G10 - Experiencia × sueldo × seniority',
               'G11 - Experiencia × sueldo × género']:
    print(f'  {nombre}')


# --- Conclusiones del ejercicio 2 ---
corr_p_sal_exp = corr_pearson.loc['salary_monthly_NETO',
                                  'profile_years_experience']
corr_p_sal_age = corr_pearson.loc['salary_monthly_NETO', 'profile_age']

dist_p_cond = {
    nivel: abs(p_cond_subpob[nivel] - P_A_est)
    for nivel in SUBPOB_SELECCIONADAS
}

conclusiones_ej2 = [
    f'En esta muestra, y bajo los filtros aplicados, se observa una '
    f'correlación de Pearson de {corr_p_sal_exp:.3f} entre el sueldo '
    f'NETO y los años de experiencia, y de {corr_p_sal_age:.3f} entre '
    f'sueldo NETO y edad. Ambas asociaciones son positivas; la '
    f'experiencia aparece como el predictor más directo del sueldo en '
    f'los datos observados.',

    f'La asociación muestral entre sueldo BRUTO y sueldo NETO es muy '
    f'fuerte (Pearson = {p_bn:.3f}, Spearman = {s_bn:.3f}), con un '
    f'ratio NETO/BRUTO mediano de {ratio_mediana:.3f} y un descuento '
    f'relativo mediano del {desc_pct_mediano:.1f} %. En términos '
    f'descriptivos y a efectos del análisis realizado, la columna '
    f'BRUTO resulta altamente redundante con NETO: puede considerarse '
    f'su remoción del formulario sin pérdida sustancial para este tipo '
    f'de análisis.',

    f'El análisis comparativo de las dos subpoblaciones más numerosas '
    f'({SUBPOB_SELECCIONADAS[0]}, {SUBPOB_SELECCIONADAS[1]}) muestra '
    f'que la distancia |P(A|B) − P(A)| no es cercana a cero en ambos '
    f'grupos (P(A) = {P_A_est:.3f}, distancias '
    f'{dist_p_cond[SUBPOB_SELECCIONADAS[0]]:.3f} y '
    f'{dist_p_cond[SUBPOB_SELECCIONADAS[1]]:.3f}). En términos '
    f'descriptivos, esto sugiere que nivel de estudio y sueldo NO son '
    f'independientes en esta muestra. Solo el '
    f'{100*len(df_estudios)/len(df):.0f} % de los respondentes '
    f'declararon su nivel de estudio, lo que acota el alcance.',

    f'Dentro de cada nivel de seniority la relación experiencia ↔ '
    f'sueldo se mantiene creciente en los datos observados (G10). '
    f'Entre los tres grupos analíticos de género considerados se '
    f'registra, en esta muestra, una brecha relativa de '
    f'{100*(1-ratio_mujer):.1f} % para Mujer Cis respecto de Hombre '
    f'Cis y de {100*(1-ratio_diversidades):.1f} % para el grupo '
    f'Diversidades respecto del mismo grupo de referencia (G11). Una '
    f'afirmación sólida sobre brechas poblacionales requeriría un '
    f'análisis multivariado y herramientas inferenciales que exceden '
    f'el alcance de esta parte.',

    # Cierre: pregunta general del ejercicio 2 respondida a modo de
    # síntesis de lo visto en los sub-ejercicios.
    f'Respondiendo la pregunta general del ejercicio 2 ("¿qué '
    f'herramientas prácticas y teóricas son útiles para explorar la '
    f'base, descubrir patrones y asociaciones?"), el desarrollo de '
    f'los cuatro sub-ejercicios muestra un conjunto mínimo y '
    f'defendible compuesto por: histogramas y diagramas de caja '
    f'para describir distribuciones marginales, coeficientes de '
    f'correlación (Pearson y Spearman) y matrices de correlación '
    f'para medir asociaciones entre numéricas, columnas derivadas '
    f'(como DESCUENTOS = BRUTO − NETO) para caracterizar '
    f'redundancia entre variables, tablas de contingencia para '
    f'pares categóricos, comparación de probabilidades marginales '
    f'y condicionales P(A) vs P(A|B) para el análisis de '
    f'independencia y scatterplots con hue categórico para la '
    f'densidad conjunta condicional. Todas estas herramientas son '
    f'estrictamente descriptivas y suficientes para responder las '
    f'preguntas planteadas en esta parte del entregable.',
]

titulo('Conclusiones del ejercicio 2')
for i, c in enumerate(conclusiones_ej2, 1):
    print(f'{i}. {c}')


# ============================================================
# Generación del HTML
# ============================================================

def fig_div(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       config={'displaylogo': False, 'responsive': True})


def tabla_filtros_html() -> str:
    filas = ''
    for f in filtros_aplicados:
        kurt_str = (f'{f["kurtosis"]:.2f}'
                    if f.get('kurtosis') is not None else '—')
        filas += (
            f'<tr>'
            f'<td>{f["filtro"]}</td>'
            f'<td class="muted">{f["motivo"]}</td>'
            f'<td class="num">{f["n_antes"]}</td>'
            f'<td class="num">{f["n_despues"]}</td>'
            f'<td class="num">−{f["recorte"]} ({f["pct"]:.1f} %)</td>'
            f'<td class="num">{kurt_str}</td>'
            f'</tr>'
        )
    return (
        '<table class="filtros">'
        '<thead><tr>'
        '<th>Filtro</th><th>Motivo</th>'
        '<th>N antes</th><th>N después</th><th>Recorte</th>'
        '<th>Kurtosis NETO</th>'
        '</tr></thead>'
        f'<tbody>{filas}</tbody></table>'
    )


def fmt_moneda(v: float) -> str:
    """Formato monetario ARS con signo $."""
    return f'$ {v:,.0f}'.replace(',', '.')


def df_moneda_html() -> str:
    d = resumen_moneda.copy()
    fmt = {
        'mediana': fmt_moneda,
        'q1':      fmt_moneda,
        'q3':      fmt_moneda,
        'n':       lambda v: f'{int(v)}',
    }
    return d.to_html(classes='datos', border=0, formatters=fmt)


def df_global_html() -> str:
    d = resumen_global.copy()
    d.insert(0, '#', range(1, len(d) + 1))
    d = d[['#', 'n', 'mediana', 'q1', 'q3', 'iqr', 'cv_robusto', 'estable']]
    d = d.rename(columns={
        'mediana': 'mediana', 'q1': 'Q1', 'q3': 'Q3',
        'iqr': 'IQR', 'cv_robusto': 'CV robusto',
    })
    d['estable'] = d['estable'].map({True: 'sí', False: 'no'})
    # n es entero por naturaleza: se castea para evitar el ".0" de pandas
    d['n'] = d['n'].astype(int)
    fmt_m = lambda v: f'$ {v/1e6:.2f} M'
    fmt = {
        'n':          lambda v: f'{int(v)}',
        'mediana':    fmt_m,
        'Q1':         fmt_m,
        'Q3':         fmt_m,
        'IQR':        fmt_m,
        'CV robusto': lambda v: f'{v:.0f} %',
    }
    return d.to_html(classes='datos', border=0, formatters=fmt)


html = f"""<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<title>AyVD Parte 1 — Ejercicio 1</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<!-- KaTeX para renderizar fórmulas matemáticas como en markdown -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{
    delimiters: [
      {{left: '$$', right: '$$', display: true}},
      {{left: '$',  right: '$',  display: false}}
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
  }}
  th {{
    background:var(--soft); color:var(--muted); font-weight:600;
    text-transform:uppercase; font-size:.72rem; letter-spacing:.05em;
  }}
  td.num, .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.muted, .muted {{ color:var(--muted); font-size:.86rem; }}
  table.filtros td:first-child {{ font-weight:600; white-space:nowrap; }}
  table.filtros td:last-child, table.filtros th:last-child {{
    white-space:nowrap; min-width:120px; text-align:right;
  }}
  table.filtros td:nth-child(3),
  table.filtros td:nth-child(4),
  table.filtros th:nth-child(3),
  table.filtros th:nth-child(4) {{ text-align:right; white-space:nowrap; }}
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
</style>
</head>
<body>

<header>
  <h1>Análisis y Visualización de Datos — Parte 1</h1>
  <div class="sub">Diplomatura en Ciencia de Datos 2026 · FAMAF, UNC</div>
  <div class="sub">Alumno: Rubén Rasi · Docente: Fredy Alexander Restrepo Blandon</div>
</header>

<main>

<h2>Ejercicio 1 — ¿Cuáles son los lenguajes asociados a los mejores salarios?</h2>

<div class="card">
  <h3>1.0  Enfoque adoptado</h3>
  <p>Para responder la pregunta hay tres caminos metodológicos
  razonables: comparar las distribuciones de sueldo por lenguaje con
  visualizaciones, comparar medidas de estadística descriptiva por
  lenguaje, o comparar probabilidades condicionales. En este trabajo
  se combinan los dos primeros enfoques: la visualización responde
  la pregunta principal de forma intuitiva y las medidas descriptivas
  la respaldan cuantitativamente. Se deja constancia explícita de la
  combinación para evitar ambigüedad sobre qué enfoque alimenta cada
  conclusión.</p>
  <div class="nota">
    Todas las observaciones que siguen deben leerse como propiedades
    <b>de la muestra analizada</b>, bajo los filtros aplicados. No se
    realizan inferencias a la población general ni tests estadísticos;
    esas herramientas se abordan en otra etapa del trabajo.
  </div>
</div>

<div class="resumen">
  <div class="metric"><div class="label">N inicial</div><div class="value">{N_INICIAL}</div></div>
  <div class="metric"><div class="label">N final (filtrado)</div><div class="value">{N_FINAL}</div></div>
  <div class="metric"><div class="label">Lenguajes únicos</div><div class="value">{len(freq)}</div></div>
  <div class="metric"><div class="label">En el ranking</div><div class="value">{len(lenguajes_mostrables)}</div></div>
</div>

<div class="card">
  <h3>1.1  Selección de columnas relevantes</h3>
  <p>Del conjunto de datos original se retienen <b>{len(COLUMNAS_RELEVANTES)} columnas</b>, estrictamente las necesarias para responder la pregunta del ejercicio:</p>
  <ul>
    <li><code>tools_programming_languages</code> — variable explicativa principal</li>
    <li><code>salary_monthly_NETO</code> — variable respuesta</li>
    <li><code>salary_in_usd</code> — tipo de dolarización del sueldo</li>
    <li><code>work_dedication</code> — filtro de homogeneidad (jornada)</li>
    <li><code>work_contract_type</code> — filtro de homogeneidad (tipo de contrato)</li>
  </ul>
  <div class="nota">
    Trabajar con un subconjunto acotado facilita la auditoría del código y
    la lectura del análisis. Las variables descartadas pueden re-incorporarse
    en los ejercicios siguientes si aportan información relevante.
  </div>
</div>

<div class="card">
  <h3>1.2  Análisis de la variable sueldo y su dolarización</h3>
  <p>La columna <code>salary_in_usd</code> del dataset toma tres valores
  literales cuando el respondente declara alguna forma de dolarización
  del sueldo, y queda en <code>NaN</code> cuando no declara ninguna.
  El dataset confirma esta lectura con una columna booleana derivada,
  <code>sueldo_dolarizado</code>, que es <code>False</code>
  exactamente en los 3.356 registros con <code>NaN</code> y
  <code>True</code> en los 1.583 restantes. Por lo tanto, el grupo
  <code>NaN</code> se interpreta como <b>"cobra 100 % en pesos
  argentinos, sin dolarización alguna"</b>, y se etiqueta en este
  análisis como <code>Cobro en pesos (NaN)</code>.</p>
  <p>Los cuatro valores posibles del sueldo según su vínculo con el
  dólar son entonces:</p>
  <ul>
    <li><code>Cobro en pesos (NaN)</code> — 3.356 registros</li>
    <li><code>Mi sueldo está dolarizado (pero cobro en moneda local)</code> — 353 registros</li>
    <li><code>Cobro parte del salario en dólares</code> — 493 registros</li>
    <li><code>Cobro todo el salario en dólares</code> — 737 registros</li>
  </ul>
  <p>Las medianas del sueldo NETO, antes del filtrado, para cada valor
  son:</p>
  {df_moneda_html()}
  <p>Los cuatro grupos reportan valores del mismo orden de magnitud
  (millones de ARS), no centenares de USD. Esto muestra que la columna
  <code>salary_monthly_NETO</code> contiene el <b>total pesificado</b>
  del sueldo para todos los respondentes, con independencia del valor
  declarado en <code>salary_in_usd</code>. Se puede usar como variable
  respuesta unificada.</p>
  <p>Para los cortes posteriores se definen <b>tres grupos analíticos
  derivados</b> a partir de los cuatro valores literales. Las etiquetas
  <b>ARS</b>, <b>USD parcial</b> y <b>USD total</b>
  <u>no son valores del dataset</u>: son etiquetas propias de este
  análisis.</p>
  <table class="filtros">
    <thead><tr>
      <th>Valor literal de salary_in_usd</th>
      <th>Grupo analítico derivado</th>
    </tr></thead>
    <tbody>
      <tr><td><code>Cobro en pesos (NaN)</code></td><td><b>ARS</b></td></tr>
      <tr><td><code>Mi sueldo está dolarizado (pero cobro en moneda local)</code></td><td><b>ARS</b></td></tr>
      <tr><td><code>Cobro parte del salario en dólares</code></td><td><b>USD parcial</b></td></tr>
      <tr><td><code>Cobro todo el salario en dólares</code></td><td><b>USD total</b></td></tr>
    </tbody>
  </table>
  <div class="nota">
    El valor literal <code>Mi sueldo está dolarizado (pero cobro en
    moneda local)</code> representa un cobro efectivo en pesos — la
    persona recibe el dinero en pesos, aunque el contrato esté atado al
    dólar —, igual que el grupo <code>Cobro en pesos (NaN)</code>. Por
    ser ambos de la misma naturaleza (cobro efectivo en pesos), se
    unifican bajo la etiqueta analítica <b>ARS</b> para el resto del
    análisis.
  </div>
</div>

<div class="card">
  <h3>1.3  Limpieza y filtrado progresivo</h3>
  <p>Los filtros se aplican en orden, declarando motivo y N resultante en cada paso. Las cinco etapas llevan la muestra de <b>{N_INICIAL}</b> a <b>{N_FINAL}</b> filas ({100*(N_INICIAL-N_FINAL)/N_INICIAL:.1f} % de recorte total).</p>
  <p>La tabla incluye además la <b>kurtosis del sueldo NETO</b>
  calculada después de cada filtro. La kurtosis (definición de
  Fisher, normal = 0) mide el peso relativo de las colas de la
  distribución: valores positivos altos indican colas pesadas con
  observaciones extremas. La kurtosis <b>antes de cualquier filtro</b>
  es <b>{kurtosis_inicial:.2f}</b>. Sirve como chequeo para
  verificar que los filtros que no operan sobre el sueldo (F1, F2,
  F3) preservan aproximadamente la forma de la distribución,
  mientras que los que sí filtran por sueldo (F4, F5) deberían
  reducir la kurtosis al eliminar observaciones extremas de las
  colas.</p>
  {tabla_filtros_html()}
</div>

<div class="card">
  <h3>1.4  Desanidado de la lista de lenguajes</h3>
  <p>La columna <code>tools_programming_languages</code> contiene una lista separada por comas de los lenguajes que declara cada respondente. Se aplica una operación de desanidado para pasar a un formato de una fila por lenguaje: una persona que usa N lenguajes contribuye a N grupos distintos.</p>
  <ul>
    <li>Filas después del desanidado: <b>{len(df_long)}</b></li>
    <li>Promedio de lenguajes por respondente: <b>{PROMEDIO_LENGS:.2f}</b></li>
    <li>Lenguajes únicos detectados: <b>{len(freq)}</b></li>
  </ul>
</div>

<div class="card">
  <h3>1.5  Umbral de frecuencia mínima</h3>
  <p>Para la visualización y el ranking se muestran únicamente los lenguajes con al menos <b>{N_MIN_LENGUAJE} respondentes</b>, una regla práctica convencional para que Q1 y Q3 contengan ~7-8 observaciones cada uno y resulten estables. Quedan <b>{len(lenguajes_mostrables)}</b> lenguajes dentro del ranking y <b>{n_excluidos}</b> fuera.</p>
  <div class="nota">
    Este umbral <b>no es un filtro sobre los datos</b>. Ninguna observación
    se descarta del conjunto; es una exclusión de visualización. Los
    lenguajes excluidos permanecen en <code>df_long</code> y pueden
    utilizarse en otros análisis. El criterio descriptivo complementario
    que caracteriza la dispersión interna de cada lenguaje es el
    coeficiente de variación robusto definido en la sección 1.6.
  </div>
</div>

<div class="card">
  <h3>1.6  Coeficiente de variación robusto por lenguaje</h3>
  <p>Para cada lenguaje del ranking se calcula, además de la mediana y
  los cuartiles, el <b>coeficiente de variación robusto</b>, definido como:</p>

  <div class="formula">
    $$\\text{{CV robusto}}_i = \\dfrac{{\\text{{IQR}}_i}}{{\\text{{mediana}}_i}} \\times 100\\,\\%$$
  </div>

  <p>Este indicador mide la dispersión relativa del 50&nbsp;% central
  respecto al valor central: a mayor CV, más heterogéneo es el grupo
  de respondentes dentro del lenguaje.</p>

  <p>Se marca un lenguaje como atípico cuando su CV supera la regla
  clásica de Tukey (1,5&nbsp;·&nbsp;IQR) aplicada sobre la distribución
  de CV del propio ranking:</p>

  <div class="formula">
    $$\\text{{lenguaje marcado}} \\iff \\text{{CV robusto}}_i > Q_3(\\text{{CV}}) + 1{{,}}5 \\cdot \\text{{IQR}}(\\text{{CV}})$$
  </div>

  <p>Tanto el CV como la regla 1,5·IQR provienen directamente del
  material de clase 02.</p>

  <ul>
    <li>Umbral Tukey sobre el CV del conjunto: <b>{UMBRAL_CV:.0f} %</b></li>
    <li>Lenguajes marcados como atípicos: <b>{len(marcados)}</b> {'(ningún lenguaje supera el umbral — el conjunto del ranking es homogéneo en dispersión relativa)' if len(marcados) == 0 else ''}</li>
  </ul>
  {df_global_html()}
</div>

<h2>Resultados visuales</h2>

<div class="chart">{fig_div(fig_rank)}<div class="chart-id">G1</div></div>
<div class="chart">{fig_div(fig_box)}<div class="chart-id">G2</div></div>
<div class="chart">{fig_div(fig_grupo)}<div class="chart-id">G3</div></div>
<div class="chart">{fig_div(fig_nm)}<div class="chart-id">G4</div></div>

<div class="card">
  <h3>1.6.e  Sueldo NETO según cantidad de lenguajes declarados</h3>
  <p>Como análisis complementario —también a nivel persona, sobre el
  mismo <code>df</code> filtrado del ejercicio 1— se computa la cantidad
  de lenguajes declarados por cada respondente y se resume el sueldo
  NETO por cada valor de ese conteo. La pregunta detrás de este cuadro
  es: <em>¿saber más lenguajes aparenta estar asociado con un sueldo
  más alto en esta muestra?</em></p>
  <ul>
    <li>Correlación muestral de Pearson
      <code>(n_lenguajes, NETO)</code>: <b>{corr_n_lang_pearson:.3f}</b></li>
    <li>Correlación muestral de Spearman
      <code>(n_lenguajes, NETO)</code>: <b>{corr_n_lang_spearman:.3f}</b></li>
  </ul>
  <p>En esta muestra, la cantidad de lenguajes declarados aparenta tener
  una asociación débil con el sueldo NETO: saber más lenguajes no se
  traduce linealmente en un sueldo mayor. El boxplot siguiente (G4b)
  muestra la distribución completa para cada valor del conteo que tiene
  al menos 15 observaciones.</p>
</div>

<div class="chart">{fig_div(fig_nlang)}<div class="chart-id">G4b</div></div>

<div class="card">
  <h3>1.8  Conclusiones del ejercicio 1</h3>
  <ol>
    {''.join(f'<li>{c}</li>' for c in conclusiones)}
  </ol>
</div>

<h2>Ejercicio 2 — Variables, relaciones y condicionalidad</h2>

<div class="card">
  <h3>2.0  Selección de variables</h3>
  <p>El ejercicio 2 se realiza sobre el mismo conjunto de datos filtrado
  del ejercicio 1 (<b>N = {N_FINAL}</b>) a nivel persona. No se desanida
  la lista de lenguajes: las variables estudiadas son demográficas y
  laborales.</p>
  <ul>
    <li><b>Numéricas:</b>
      <code>salary_monthly_NETO</code> (variable respuesta),
      <code>profile_years_experience</code> (años de experiencia),
      <code>profile_age</code> (edad).</li>
    <li><b>Categóricas:</b>
      <code>work_seniority</code> (nivel de seniority),
      <code>profile_gender</code> (identidad de género).</li>
  </ul>
</div>

<div class="card">
  <h3>2.0.1  Filtro local de edad biológica (sólo ej 2)</h3>
  <p>La columna <code>profile_age</code> contiene algunos valores
  implausibles (por ejemplo, <b>999 años</b>) que no fueron removidos
  en los filtros F1–F5 del ejercicio 1 porque allí la edad no
  participaba del análisis. Para el ejercicio 2 —donde sí se usa como
  variable numérica— se aplica un <b>filtro LOCAL</b> al tramo
  laboralmente plausible <b>[{EDAD_MIN_EJ2}, {EDAD_MAX_EJ2}]</b> años.</p>
  <p><b>Alcance:</b> este filtro NO se propaga al ejercicio 1. El
  ranking de lenguajes (sección 1) ya fue calculado sobre <code>df</code>
  completo; aquí se construye un DataFrame separado <code>df_ej2</code>
  que se usa exclusivamente en los análisis de esta sección.</p>
  <ul>
    <li>N antes del filtro: <b>{n_antes_ej2}</b></li>
    <li>N después del filtro: <b>{n_despues_ej2}</b>
      (<b>{n_descartados_ej2}</b> filas descartadas)</li>
    {('<li>Ejemplos de edades descartadas: <b>' + ', '.join(str(int(x)) for x in edades_descartadas_ej2[:6]) + '</b></li>') if edades_descartadas_ej2 else ''}
  </ul>
</div>

<h3 style="margin-top:32px">2.a  Densidad conjunta (3 numéricas + 2 categóricas)</h3>

<div class="card">
  <p>Se describen primero las variables por separado y luego su
  correlación conjunta. Los histogramas (G5) muestran las distribuciones
  marginales; la matriz (G6) cuantifica las asociaciones lineales
  monótonas entre las tres variables numéricas.</p>
  {describe_num.round(2).to_html(classes='datos', border=0)}
</div>

<div class="chart">{fig_div(fig_g5)}<div class="chart-id">G5</div></div>
<div class="chart">{fig_div(fig_g6)}<div class="chart-id">G6</div></div>

<div class="card">
  <p>En el plano categórico se observa la distribución del nivel de
  seniority y del grupo de género. Para género se utilizan los tres
  grupos analíticos definidos más adelante en el ejercicio 2.d
  (<b>Hombre Cis</b>, <b>Mujer Cis</b> y <b>Diversidades</b>, donde
  esta última agrupa las identidades con baja cobertura muestral
  individual). Esto garantiza que todas las identidades del
  formulario estén representadas en el análisis sin producir barras
  minúsculas ilegibles en el gráfico.</p>
</div>

<div class="chart">{fig_div(fig_g7)}<div class="chart-id">G7</div></div>

<h3 style="margin-top:32px">2.b  Asociación: sueldo BRUTO vs sueldo NETO</h3>

<div class="card">
  <p>Se estudia la asociación entre el sueldo BRUTO declarado y el
  sueldo NETO. Más allá de medir la correlación entre ambas series,
  se construye una <b>columna derivada</b>
  <code>DESCUENTOS = BRUTO − NETO</code> cuya distribución permite
  caracterizar cuánto margen queda entre las dos variables una vez
  descontada la parte lineal.</p>
  <p>Las <b>observaciones válidas</b> para este análisis son aquellas
  del conjunto filtrado (sección 1.3, con los cinco filtros F1 a F5
  ya aplicados) que además cumplen dos condiciones adicionales:
  ambos valores de sueldo están presentes (no <code>NaN</code>) y
  ambos son estrictamente positivos. El resultado final es un
  subconjunto de {len(bn)} respondentes sobre los que se calculan los
  estadísticos que siguen.</p>
  <div class="resumen">
    <div class="metric"><div class="label">Observaciones válidas</div><div class="value">{len(bn)}</div></div>
    <div class="metric"><div class="label">Correlación Pearson</div><div class="value">{p_bn:.3f}</div></div>
    <div class="metric"><div class="label">Correlación Spearman</div><div class="value">{s_bn:.3f}</div></div>
    <div class="metric"><div class="label">Ratio NETO/BRUTO mediano</div><div class="value">{ratio_mediana:.3f}</div></div>
  </div>
  <p>La recta ajustada por mínimos cuadrados tiene pendiente muestral
  <b>{coef_reg[0]:.3f}</b> (ARS netos observados por cada ARS bruto) y
  ordenada al origen <b>$ {coef_reg[1]:,.0f}</b>. En esta muestra el
  descuento relativo mediano es del <b>{desc_pct_mediano:.2f} %</b>,
  con un rango intercuartil entre <b>{desc_pct_q1:.2f} %</b> y
  <b>{desc_pct_q3:.2f} %</b>.</p>
</div>

<div class="chart">{fig_div(fig_g8)}<div class="chart-id">G8</div></div>

<div class="card">
  <h3>¿Conviene quitar la columna BRUTO del formulario?</h3>
  <p>Una de las preguntas que motiva este sub-ejercicio es si la
  encuesta sysarmy podría simplificarse eliminando la columna de
  sueldo bruto, que actualmente duplica información que parece
  derivable del sueldo neto. Los datos de esta muestra dan una
  respuesta razonablemente clara:</p>
  <ul>
    <li>Las correlaciones muestrales Pearson ({p_bn:.3f}) y Spearman
    ({s_bn:.3f}) son muy cercanas a 1.</li>
    <li>El ratio NETO/BRUTO muestra una estructura estable, con el
    50 % central del descuento relativo ubicado entre el
    {desc_pct_q1:.2f} % y el {desc_pct_q3:.2f} %.</li>
    <li>Conocido el NETO, el valor esperado del BRUTO se puede
    recuperar aplicando esta estructura con un margen descriptivo
    acotado.</li>
  </ul>
  <p><b>En términos descriptivos y a efectos de este tipo de
  análisis</b>, la columna BRUTO aporta información altamente
  redundante respecto de NETO y podría omitirse del formulario sin
  pérdida sustancial para las preguntas que se exploran acá. La
  observación se limita a la muestra considerada; un diseño final de
  encuesta debería además considerar otros usos de la columna BRUTO
  no evaluados en este trabajo.</p>
</div>

<h3 style="margin-top:32px">2.c  Densidad condicional: sueldo según nivel de estudio</h3>

<div class="card">
  <p>Se analiza la distribución del sueldo NETO condicionada al nivel
  educativo declarado. El nivel de estudio fue declarado solo por el
  <b>{100*len(df_estudios)/len(df):.1f} %</b> de los respondentes del
  conjunto filtrado ({len(df_estudios)} de {len(df)}), lo que acota el
  alcance descriptivo de este análisis.</p>
  <p>Como vista general se muestra primero el describe por nivel de
  estudio:</p>
  {describe_estudios_html}
</div>

<div class="card">
  <h3>Comparación de dos subpoblaciones numerosas</h3>
  <p>Para evitar que la comparación quede dominada por los niveles
  con pocos respondentes (donde las medianas son inestables), el
  análisis condicional se enfoca en las dos subpoblaciones con mayor
  cantidad de observaciones declaradas:</p>
  <ul>
    <li><code>{SUBPOB_SELECCIONADAS[0]}</code> — n = {medidas_subpob[SUBPOB_SELECCIONADAS[0]]['n']}</li>
    <li><code>{SUBPOB_SELECCIONADAS[1]}</code> — n = {medidas_subpob[SUBPOB_SELECCIONADAS[1]]['n']}</li>
  </ul>
  <p>Medidas de centralización y dispersión por subpoblación:</p>
  {tabla_medidas_subpob_html}
</div>

<div class="chart">{fig_div(fig_g9)}<div class="chart-id">G9</div></div>

<div class="card">
  <h3>¿Son independientes el nivel de estudio y el sueldo NETO?</h3>
  <p>El marco teórico se toma de la clase 01 (probabilidad condicional).
  Dos eventos A y B son independientes si y sólo si</p>
  <div class="formula">$$P(A \\mid B) = P(A)$$</div>
  <p>Definimos:</p>
  <ul>
    <li><b>A</b> = evento <i>"sueldo NETO mayor que la mediana global"</i> (umbral calculado sobre el conjunto con estudios declarados).</li>
    <li><b>B</b> = evento <i>"nivel de estudio = X"</i> (para cada subpoblación seleccionada).</li>
  </ul>
  <p>Si las variables fueran independientes en esta muestra, las
  probabilidades condicionales serían similares a la marginal. Los
  valores observados son:</p>
  <table class="filtros">
    <thead><tr><th>Probabilidad</th><th>Valor</th><th>|distancia a P(A)|</th></tr></thead>
    <tbody>
      <tr><td>P(A) &nbsp; <i>marginal</i></td><td class="num">{P_A_est:.4f}</td><td class="num">—</td></tr>
      <tr><td>P(A | {SUBPOB_SELECCIONADAS[0]})</td><td class="num">{p_cond_subpob[SUBPOB_SELECCIONADAS[0]]:.4f}</td><td class="num">{abs(p_cond_subpob[SUBPOB_SELECCIONADAS[0]] - P_A_est):.4f}</td></tr>
      <tr><td>P(A | {SUBPOB_SELECCIONADAS[1]})</td><td class="num">{p_cond_subpob[SUBPOB_SELECCIONADAS[1]]:.4f}</td><td class="num">{abs(p_cond_subpob[SUBPOB_SELECCIONADAS[1]] - P_A_est):.4f}</td></tr>
    </tbody>
  </table>
  <div class="nota">
    <b>Lectura descriptiva:</b> las dos probabilidades condicionales
    no son iguales a P(A). La subpoblación {SUBPOB_SELECCIONADAS[1]}
    muestra una distancia marcada respecto de la marginal, mientras
    que {SUBPOB_SELECCIONADAS[0]} se aparta poco. En términos
    <b>puramente descriptivos</b>, esto sugiere que nivel de estudio y
    sueldo NETO <u>no son independientes</u> en esta muestra. No se
    realiza ningún test inferencial; una afirmación más fuerte
    requeriría herramientas de la parte 2 del entregable.
  </div>
</div>

<h3 style="margin-top:32px">2.d  Densidad conjunta condicional: experiencia vs sueldo por categoría</h3>

<div class="card">
  <p>Se estudia cómo se comporta la relación entre <b>años de
  experiencia</b> y <b>sueldo NETO</b> al condicionar por dos factores
  categóricos distintos: el nivel de seniority declarado (G10) y el
  grupo de género (G11). El primero está directamente vinculado a la
  progresión profesional del respondente; el segundo permite examinar
  si existen brechas sistemáticas entre grupos de identidad de género
  dentro de cada tramo de experiencia. Aunque el análisis más básico
  podría hacerse con una sola variable categórica, la segunda se
  incluye como análisis complementario porque aporta una dimensión
  distinta y relevante para el tipo de preguntas que este trabajo
  explora.</p>
  <div class="resumen">
    <div class="metric"><div class="label">Mediana Junior</div><div class="value">$ {seniority_stats.loc['Junior','mediana']/1e6:.2f} M</div></div>
    <div class="metric"><div class="label">Mediana Semi-Senior</div><div class="value">$ {seniority_stats.loc['Semi-Senior','mediana']/1e6:.2f} M</div></div>
    <div class="metric"><div class="label">Mediana Senior</div><div class="value">$ {seniority_stats.loc['Senior','mediana']/1e6:.2f} M</div></div>
  </div>
</div>

<div class="chart">{fig_div(fig_g10)}<div class="chart-id">G10</div></div>

<div class="card">
  <p>El análisis por género se realiza sobre <b>tres grupos analíticos</b>:
  <code>Hombre Cis</code> y <code>Mujer Cis</code>, que son los valores
  literales más numerosos del formulario, y una agrupación llamada
  <b>Diversidades</b> que reúne las categorías <code>No binarie</code>,
  <code>Trans</code>, <code>Queer</code>, <code>Agénero</code> y
  <code>Prefiero no decir</code>. Cada una de estas últimas tiene baja
  cobertura muestral individual (menos de 55 observaciones), pero
  agrupadas bajo una sola etiqueta alcanzan un tamaño suficiente para
  estadísticos descriptivos básicos, y la agrupación permite que estas
  identidades estén representadas en el análisis en lugar de quedar
  excluidas.</p>
  <div class="resumen">
    <div class="metric"><div class="label">Mediana Hombre Cis</div><div class="value">$ {med_hombre/1e6:.2f} M</div></div>
    <div class="metric"><div class="label">Mediana Mujer Cis</div><div class="value">$ {med_mujer/1e6:.2f} M</div></div>
    <div class="metric"><div class="label">Mediana Diversidades</div><div class="value">$ {med_diversidades/1e6:.2f} M</div></div>
  </div>
  <div class="resumen">
    <div class="metric"><div class="label">Brecha Mujer Cis vs Hombre Cis</div><div class="value">{100*(1-ratio_mujer):.1f} %</div></div>
    <div class="metric"><div class="label">Brecha Diversidades vs Hombre Cis</div><div class="value">{100*(1-ratio_diversidades):.1f} %</div></div>
  </div>
  <p>Las brechas relativas se calculan tomando la mediana de
  <code>Hombre Cis</code> como referencia. Un valor positivo indica
  que la mediana del grupo comparado está por debajo de la del
  grupo de referencia.</p>
</div>

<div class="chart">{fig_div(fig_g11)}<div class="chart-id">G11</div></div>

<div class="card">
  <h3>2.e  Conclusiones del ejercicio 2</h3>
  <ol>
    {''.join(f'<li>{c}</li>' for c in conclusiones_ej2)}
  </ol>
</div>

</main>

<footer>
  Generado con Python y Plotly ·
  Para cotejar los datos y estadísticos que sustentan este informe,
  ejecutar <code>python datos_parte1.py</code> en el mismo directorio.
</footer>

</body>
</html>
"""

OUTPUT_HTML.write_text(html, encoding='utf-8')

titulo('Generación del HTML')
print(f'archivo:  {OUTPUT_HTML}')
print(f'tamaño:   {OUTPUT_HTML.stat().st_size/1024:.1f} KB')
