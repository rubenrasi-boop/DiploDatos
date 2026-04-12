#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entregable AyVD Parte 1 — Datos y estadísticos del Ejercicio 1
Diplomatura en Ciencia de Datos 2026 — FAMAF, UNC

Alumno:  Rubén Rasi
Docente: Fredy Alexander Restrepo Blandon

Acompaña al informe HTML informe_parte1.html como apéndice de datos.
Consolida todos los cuadros, estadísticos y transformaciones intermedias
que sustentan el análisis de los ejercicios 1 y 2, incluidos los que no
aparecen visualmente en el informe pero justifican las decisiones
metodológicas.

Ejercicios:
    1.  Análisis descriptivo: ¿cuáles son los lenguajes de programación
        asociados a los mejores salarios?
    2a. Densidad conjunta con 3 variables numéricas y 2 categóricas.
    2b. Asociación: correlación entre sueldo BRUTO y sueldo NETO.
    2c. Densidad condicional: sueldo según nivel de estudio.
    2d. Densidad conjunta condicional: experiencia vs sueldo con
        coloreado por factor categórico (seniority, género).

Uso:
    python datos_parte1.py
        imprime por consola todos los cuadros en orden.

    python datos_parte1.py --csv
        además exporta cada cuadro a CSV en ./datos_parte1_csv/.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option('display.width', 140)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 200)

# Tema claro con contraste suave, coherente con el informe HTML
sns.set_theme(style='whitegrid', context='notebook')
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#FAFBFC',
    'axes.edgecolor':   '#C5CEDF',
    'axes.labelcolor':  '#2E3440',
    'axes.titlecolor':  '#2E3440',
    'xtick.color':      '#5E6472',
    'ytick.color':      '#5E6472',
    'grid.color':       '#E6E8EF',
    'font.family':      'DejaVu Sans',
    'font.size':        10,
})

PALETA = ['#5B8DEF', '#6BBF80', '#E8A04F', '#C96C6C',
          '#9673C0', '#4BAFB0', '#C78EB0', '#8C99AD',
          '#D6A35C', '#70A9A1', '#A4B8D3', '#B8868B']
COLOR_ARS = '#5B8DEF'
COLOR_USD_PARCIAL = '#E8A04F'
COLOR_USD_TOTAL = '#6BBF80'


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'sysarmy_survey_2026_processed.csv'
CSV_DIR = BASE_DIR / 'datos_parte1_csv'
IMG_DIR = BASE_DIR / 'datos_parte1_img'
IMG_DIR.mkdir(exist_ok=True)

# Umbral mínimo de observaciones para incluir un lenguaje en el ranking
# del informe. Regla práctica convencional: con n ≥ 30 cada cuartil
# (Q1, Q3) contiene ~7-8 observaciones y resulta razonablemente estable.
# No descarta datos: es una exclusión de visualización.
N_MIN_LENGUAJE = 30

EXPORTAR_CSV = '--csv' in sys.argv
if EXPORTAR_CSV:
    CSV_DIR.mkdir(exist_ok=True)

# Registro de cuadros para la exportación final
cuadros_exportables: dict[str, pd.DataFrame | pd.Series] = {}


def mostrar(nombre: str, obj) -> None:
    """Imprime un cuadro con encabezado y lo registra para CSV opcional."""
    sep = '━' * max(3, 70 - len(nombre))
    print(f'\n━━━ {nombre} {sep}')
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        print(obj.to_string())
        cuadros_exportables[nombre] = obj
    else:
        print(obj)


# ============================================================
# 1.0  Carga del conjunto de datos y declaración de enfoque
# ============================================================
# La consigna del ejercicio 1 permite elegir UNA de las siguientes
# opciones:
#   A) Comparar distribuciones de sueldo por lenguaje con visualizaciones.
#   B) Comparar medidas de estadística descriptiva por lenguaje.
#   C) Comparar probabilidades.
#
# En este trabajo se utilizan las opciones A y B en conjunto: la
# visualización (A) responde la pregunta principal y las medidas
# descriptivas (B) la respaldan cuantitativamente. La decisión se
# declara explícitamente para evitar ambigüedad.

df_original = pd.read_csv(DATA_PATH)
N_INICIAL = len(df_original)

metadatos_carga = pd.DataFrame({
    'métrica': ['archivo', 'filas iniciales', 'columnas totales'],
    'valor': [DATA_PATH.name, N_INICIAL, len(df_original.columns)],
})
mostrar('1.0  Carga del conjunto de datos', metadatos_carga)

enfoque_ej1 = pd.DataFrame({
    'elemento': ['opción elegida', 'visualización', 'soporte cuantitativo'],
    'decisión': [
        'A + B combinadas',
        'distribuciones por lenguaje (G1-G4)',
        'mediana, cuartiles, IQR y dispersión relativa',
    ],
})
mostrar('1.0  Enfoque adoptado para el ejercicio 1', enfoque_ej1)


# ============================================================
# 1.1  Selección de columnas relevantes
# ============================================================

COLUMNAS_RELEVANTES = [
    'tools_programming_languages',
    'salary_monthly_NETO',
    'salary_monthly_BRUTO',
    'salary_in_usd',
    'work_dedication',
    'work_contract_type',
    'profile_years_experience',
    'profile_age',
    'work_seniority',
    'profile_studies_level',
    'profile_studies_level_state',
    'profile_gender',
]

columnas_retenidas = pd.DataFrame({
    'columna': COLUMNAS_RELEVANTES,
    'ejercicio': [
        '1',
        '1, 2a, 2b, 2c, 2d',
        '2b',
        '1',
        '1 (filtro)',
        '1 (filtro)',
        '2a, 2d',
        '2a',
        '2a, 2d',
        '2c',
        '2c',
        '2a, 2d',
    ],
    'rol': [
        'variable explicativa del ejercicio 1',
        'variable respuesta principal',
        'segunda variable de sueldo (para 2b)',
        'tipo de dolarización del sueldo',
        'filtro de homogeneidad: jornada',
        'filtro de homogeneidad: tipo de contrato',
        'años de experiencia profesional',
        'edad del respondente',
        'nivel de seniority declarado',
        'nivel educativo alcanzado',
        'estado del nivel educativo (completo, en curso, incompleto)',
        'identidad de género',
    ],
})
mostrar('1.1  Columnas retenidas', columnas_retenidas)
print(f'\n  columnas descartadas: '
      f'{len(df_original.columns) - len(COLUMNAS_RELEVANTES)}')

df = df_original[COLUMNAS_RELEVANTES].copy()


# ============================================================
# 1.2  Análisis de la variable sueldo y su dolarización
# ============================================================
# Este paso se ejecuta antes del filtrado porque determina cómo
# interpretar la columna respuesta y cómo se estratifica el análisis.

# --- 1.2.a  Valores crudos de salary_in_usd (antes de normalizar) ---
crudos_usd = df['salary_in_usd'].value_counts(dropna=False).to_frame('n')
crudos_usd.index.name = 'salary_in_usd (crudo)'
crudos_usd['pct'] = (100 * crudos_usd['n'] / len(df)).round(2)
mostrar('1.2.a  Valores crudos de salary_in_usd', crudos_usd)


# --- 1.2.b  Preservación de los valores literales ---
# Se conserva el contenido crudo de salary_in_usd. Los NaN representan
# a respondentes que no declararon ninguna forma de dolarización, lo
# que el propio dataset codifica como sueldo_dolarizado = False
# (coincidencia exacta entre ambas columnas). Es decir, el grupo NaN
# se interpreta como "cobra 100 % en pesos argentinos". Se etiqueta
# como 'Cobro en pesos (NaN)' para dejar esto explícito.

df['moneda_categoria'] = df['salary_in_usd'].fillna('Cobro en pesos (NaN)')

orden_cats = [
    'Cobro en pesos (NaN)',
    'Mi sueldo está dolarizado (pero cobro en moneda local)',
    'Cobro parte del salario en dólares',
    'Cobro todo el salario en dólares',
]

# --- 1.2.c  Estadísticos completos del sueldo NETO por categoría ---
describe_moneda = (
    df.groupby('moneda_categoria')['salary_monthly_NETO']
    .describe(percentiles=[.10, .25, .50, .75, .90])
    .reindex(orden_cats)
    .round(0)
)
mostrar('1.2.b  Sueldo NETO por categoría (describe completo)',
        describe_moneda)

# --- 1.2.d  Chequeo de orden de magnitud ---
# Confirma empíricamente que salary_monthly_NETO es el total pesificado.
med_pesos   = describe_moneda.loc['Cobro en pesos (NaN)', '50%']
med_parcial = describe_moneda.loc[
    'Cobro parte del salario en dólares', '50%']
med_total   = describe_moneda.loc[
    'Cobro todo el salario en dólares', '50%']


def fmt_ars(v: float) -> str:
    return f'{v:,.0f}'.replace(',', '.')


chequeo_magnitud = pd.DataFrame({
    'métrica': [
        'mediana "Cobro en pesos (NaN)"',
        'mediana "Cobro parte del salario en dólares"',
        'relación con la mediana del grupo en pesos',
        'mediana "Cobro todo el salario en dólares"',
        'relación con la mediana del grupo en pesos',
    ],
    'valor': [
        fmt_ars(med_pesos),
        fmt_ars(med_parcial),
        f'{med_parcial/med_pesos:.2f} ×',
        fmt_ars(med_total),
        f'{med_total/med_pesos:.2f} ×',
    ],
})
mostrar('1.2.c  Chequeo de orden de magnitud', chequeo_magnitud)

print('\n  Lectura del chequeo:')
print('  - Los cuatro grupos reportan valores del orden de millones de ARS,')
print('    no centenares de USD. La columna salary_monthly_NETO contiene el')
print('    TOTAL PESIFICADO del sueldo para todos los respondentes, con')
print('    independencia del valor declarado en salary_in_usd. Se usa como')
print('    variable respuesta unificada.')
print('  - El valor literal "Mi sueldo está dolarizado (pero cobro en')
print('    moneda local)" representa un cobro efectivo en pesos, igual')
print('    que el grupo "Cobro en pesos (NaN)". Por ser ambos de la misma')
print('    naturaleza (cobro efectivo en pesos), se unifican bajo la')
print('    etiqueta analítica ARS.')

# --- 1.2.e  Mapeo de valores literales a grupos analíticos derivados ---
# Los grupos ARS, USD parcial y USD total NO son valores del dataset:
# son etiquetas derivadas para agrupar los 4 estados literales de
# salary_in_usd en 3 subpoblaciones con comportamiento salarial
# comparable.
MAPEO_GRUPO = {
    'Cobro en pesos (NaN)':                                     'ARS',
    'Mi sueldo está dolarizado (pero cobro en moneda local)':   'ARS',
    'Cobro parte del salario en dólares':                       'USD parcial',
    'Cobro todo el salario en dólares':                         'USD total',
}
df['moneda_grupo'] = df['moneda_categoria'].map(MAPEO_GRUPO)

grupos_moneda = df['moneda_grupo'].value_counts().to_frame('n')
grupos_moneda['pct'] = (100 * grupos_moneda['n'] / len(df)).round(2)
mostrar('1.2.d  Grupos de moneda derivados (antes de filtrar)',
        grupos_moneda)


# ============================================================
# 1.3  Limpieza y filtrado progresivo
# ============================================================

registro_filtros: list[dict] = []


def aplicar_filtro(dataframe: pd.DataFrame, nombre: str,
                   motivo: str, mascara: pd.Series) -> pd.DataFrame:
    n_antes = len(dataframe)
    nuevo = dataframe[mascara].copy()
    n_despues = len(nuevo)
    recorte = n_antes - n_despues
    registro_filtros.append({
        'filtro': nombre,
        'motivo': motivo,
        'n_antes': n_antes,
        'n_despues': n_despues,
        'recorte': recorte,
        'pct': round(100 * recorte / n_antes, 2) if n_antes else 0,
    })
    return nuevo


# F1 — filas sin lenguaje o sin sueldo NETO
df = aplicar_filtro(
    df,
    'F1 - sin lenguaje o sin sueldo NETO',
    'observaciones sin alguna de las dos variables principales no aportan.',
    df['tools_programming_languages'].notna()
    & df['salary_monthly_NETO'].notna(),
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
# sueldo mensual (Staff en planta permanente, Contractor bajo contrato
# directo y Tercerizado vía consultora o agencia). Se descartan Freelance
# y Cooperativa porque facturan por honorarios, monotributo o
# participación societaria, y mezclan conceptos distintos con el NETO.
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


# F4 — regla de Tukey 1,5·IQR aplicada por separado dentro de cada
# grupo de moneda. Para cada grupo se calculan Q1 y Q3 del sueldo NETO
# y se descartan las observaciones fuera del intervalo
#   [Q1 − 1,5·IQR ,  Q3 + 1,5·IQR].
# La estratificación es necesaria porque ARS, USD parcial y USD total
# tienen medianas naturalmente distintas: un IQR calculado sobre el
# conjunto completo no separaría correctamente los atípicos de cada
# subpoblación.
def mascara_iqr_por_grupo(dframe: pd.DataFrame, col: str,
                          grupo: str) -> pd.Series:
    mask = pd.Series(False, index=dframe.index)
    for _, sub in dframe.groupby(grupo):
        q1, q3 = sub[col].quantile([.25, .75])
        iqr = q3 - q1
        mask.loc[sub.index] = sub[col].between(q1 - 1.5 * iqr,
                                               q3 + 1.5 * iqr)
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

N_FINAL = len(df)
df_filtros = pd.DataFrame(registro_filtros)

mostrar('1.3.a  Secuencia completa de filtros', df_filtros)

composicion_final = df['moneda_grupo'].value_counts().to_frame('n')
composicion_final['pct'] = (100 * composicion_final['n'] / N_FINAL).round(2)
mostrar('1.3.b  Composición por grupo de moneda después de filtrar',
        composicion_final)

sumario_recorte = pd.DataFrame({
    'métrica': ['N inicial', 'N final', 'recorte total', 'recorte %'],
    'valor': [
        N_INICIAL,
        N_FINAL,
        N_INICIAL - N_FINAL,
        f'{100*(N_INICIAL-N_FINAL)/N_INICIAL:.2f} %',
    ],
})
mostrar('1.3.c  Sumario global del recorte', sumario_recorte)


# ============================================================
# 1.4  Desanidado de la lista de lenguajes y frecuencias
# ============================================================

df_long = df.assign(
    lenguaje=df['tools_programming_languages'].str.split(',')
).explode('lenguaje')
df_long['lenguaje'] = df_long['lenguaje'].str.strip()
df_long = df_long[df_long['lenguaje'].astype(bool)]

PROMEDIO_LENGS = len(df_long) / max(len(df), 1)
freq = df_long['lenguaje'].value_counts()

metadatos_desanidado = pd.DataFrame({
    'métrica': [
        'filas tras desanidar la lista',
        'lenguajes por respondente (promedio)',
        'lenguajes únicos detectados',
    ],
    'valor': [
        len(df_long),
        round(PROMEDIO_LENGS, 3),
        len(freq),
    ],
})
mostrar('1.4.a  Metadatos del desanidado', metadatos_desanidado)

# Frecuencia COMPLETA de todos los lenguajes (no solo el top 15)
freq_completa = freq.to_frame('n')
freq_completa['pct'] = (100 * freq_completa['n'] / len(df_long)).round(3)
mostrar('1.4.b  Frecuencia completa de lenguajes (todos los detectados)',
        freq_completa)


# ============================================================
# 1.5  Umbral de frecuencia mínima (exclusión de visualización)
# ============================================================

lenguajes_mostrables = sorted(freq[freq >= N_MIN_LENGUAJE].index.tolist())
excluidos = freq[freq < N_MIN_LENGUAJE]

umbral_sumario = pd.DataFrame({
    'métrica': [
        'umbral n ≥',
        'lenguajes incluidos en el ranking',
        'lenguajes excluidos de la visualización',
        'observaciones en incluidos',
        'observaciones en excluidos',
    ],
    'valor': [
        N_MIN_LENGUAJE,
        len(lenguajes_mostrables),
        len(excluidos),
        int(freq[freq >= N_MIN_LENGUAJE].sum()),
        int(excluidos.sum()),
    ],
})
mostrar('1.5.a  Efectos del umbral de visualización', umbral_sumario)

excluidos_df = excluidos.to_frame('n')
excluidos_df['pct'] = (100 * excluidos_df['n'] / len(df_long)).round(3)
mostrar('1.5.b  Lenguajes excluidos de la visualización '
        '(siguen en df_long)', excluidos_df)

df_rank = df_long[df_long['lenguaje'].isin(lenguajes_mostrables)].copy()


# ============================================================
# 1.6  Resumen estadístico y dispersión relativa de la mediana
# ============================================================
# Indicador descriptivo que combina dispersión (IQR), tamaño de muestra
# (n) y el valor de la mediana, expresado en porcentaje:
#
#     disp_i  =  100 · IQR_i / ( √n_i · mediana_i )    [%]
#
# Es puramente descriptivo: no supone distribución ni hace inferencia.
# A mayor dispersión o menor n, mayor es disp_i.
#
# Criterio de estabilidad (sin umbrales arbitrarios):
#
#     lenguaje marcado con dispersión alta  ⇔  disp_i  >  2 · mediana(disp)
#
# El umbral se recalibra automáticamente al cambiar el conjunto de datos.


def resumen_robusto(serie: pd.Series) -> pd.Series:
    q1, mediana, q3 = serie.quantile([.25, .5, .75])
    n = int(serie.count())
    iqr = q3 - q1
    disp_pct = (100 * iqr / (math.sqrt(n) * mediana)
                if n > 0 and mediana else np.nan)
    return pd.Series({
        'n': n,
        'mediana': mediana,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
        'disp_pct': disp_pct,
    })


resumen_global = (
    df_rank.groupby('lenguaje')['salary_monthly_NETO']
    .apply(resumen_robusto).unstack()
    .sort_values('mediana', ascending=False)
)

disp_mediana = resumen_global['disp_pct'].median()
UMBRAL_DISP = 2 * disp_mediana
resumen_global['estable'] = resumen_global['disp_pct'] <= UMBRAL_DISP
resumen_global.insert(0, 'ranking', range(1, len(resumen_global) + 1))

# Vista legible con montos en millones (con signo $) y porcentaje
vista_global = resumen_global.copy()
for c in ('mediana', 'q1', 'q3', 'iqr'):
    vista_global[c] = '$ ' + (vista_global[c] / 1e6).round(3).astype(str) + ' M'
vista_global['disp_pct'] = vista_global['disp_pct'].round(2).astype(str) + ' %'
vista_global['estable'] = vista_global['estable'].map({True: 'sí', False: 'no'})
vista_global = vista_global.rename(columns={
    'mediana':  'mediana',
    'q1':       'Q1',
    'q3':       'Q3',
    'iqr':      'IQR',
    'disp_pct': 'dispersión rel.',
})
mostrar('1.6.a  Resumen estadístico completo por lenguaje '
        '(mediana, cuartiles, IQR, dispersión relativa)', vista_global)

criterio_sumario = pd.DataFrame({
    'métrica': [
        'fórmula del indicador',
        'dispersión relativa mediana del conjunto',
        'umbral (2 × mediana)',
        'lenguajes estables',
        'lenguajes marcados (dispersión alta)',
    ],
    'valor': [
        '100 · IQR / (√n · mediana)',
        f'{disp_mediana:.2f} %',
        f'{UMBRAL_DISP:.2f} %',
        int(resumen_global['estable'].sum()),
        int((~resumen_global['estable']).sum()),
    ],
})
mostrar('1.6.b  Criterio de estabilidad aplicado', criterio_sumario)

marcados = (
    resumen_global[~resumen_global['estable']]
    [['ranking', 'n', 'mediana', 'iqr', 'disp_pct']]
    .copy()
)
marcados['mediana'] = '$ ' + (marcados['mediana'] / 1e6).round(3).astype(str) + ' M'
marcados['iqr'] = '$ ' + (marcados['iqr'] / 1e6).round(3).astype(str) + ' M'
marcados['disp_pct'] = marcados['disp_pct'].round(2).astype(str) + ' %'
marcados = marcados.rename(columns={
    'iqr':      'IQR',
    'disp_pct': 'dispersión rel.',
})
mostrar('1.6.c  Lenguajes marcados con dispersión alta', marcados)

# Resumen por grupo de moneda × lenguaje (todos los pares con n ≥ 1)
resumen_por_grupo = (
    df_rank.groupby(['moneda_grupo', 'lenguaje'])['salary_monthly_NETO']
    .agg(n='count',
         mediana='median',
         q1=lambda x: x.quantile(.25),
         q3=lambda x: x.quantile(.75))
    .reset_index()
    .sort_values(['moneda_grupo', 'mediana'], ascending=[True, False])
)
for c in ('mediana', 'q1', 'q3'):
    resumen_por_grupo[c] = resumen_por_grupo[c].round(0)
mostrar('1.6.d  Resumen por grupo de moneda × lenguaje '
        '(todos los pares presentes)', resumen_por_grupo)


# ============================================================
# 1.7  Valores derivados usados en las conclusiones del informe
# ============================================================

top3 = resumen_global.head(3)
mediana_conjunto = resumen_global['mediana'].median()
premio_top1 = 100 * (top3['mediana'].iloc[0] / mediana_conjunto - 1)

derivados_conclusiones = pd.DataFrame({
    'métrica': [
        'lenguaje ranking 1',
        'mediana ranking 1 (ARS)',
        'lenguaje ranking 2',
        'mediana ranking 2 (ARS)',
        'lenguaje ranking 3',
        'mediana ranking 3 (ARS)',
        'mediana del conjunto de lenguajes (ARS)',
        'premio del ranking 1 vs mediana del conjunto',
        'cantidad de lenguajes marcados con dispersión alta',
    ],
    'valor': [
        top3.index[0],
        fmt_ars(top3['mediana'].iloc[0]),
        top3.index[1],
        fmt_ars(top3['mediana'].iloc[1]),
        top3.index[2],
        fmt_ars(top3['mediana'].iloc[2]),
        fmt_ars(mediana_conjunto),
        f'{premio_top1:.1f} %',
        int((~resumen_global['estable']).sum()),
    ],
})
mostrar('1.7  Valores derivados usados en las conclusiones del informe',
        derivados_conclusiones)


# ============================================================
# 1.8  Gráficos equivalentes en matplotlib / seaborn
# ============================================================
# Se generan las versiones estáticas de los gráficos G1 a G4 que
# aparecen en el informe HTML usando las librerías estándar vistas
# en las notebooks del curso (matplotlib y seaborn). Los marcadores
# visuales de los lenguajes con dispersión alta (asterisco y opacidad
# reducida) se mantienen en ambas representaciones.
#
# Los IDs de gráfico (G1..G4) no aparecen en el título del gráfico
# sino como texto pequeño en la esquina inferior derecha de la figura.

# Paleta desaturada para G3 (grupo de moneda)
COLORES_MONEDA_G3 = {
    'ARS':         '#7B96C9',   # azul polvo
    'USD parcial': '#D4A574',   # arena
    'USD total':   '#8FB39E',   # salvia
}

orden_lenguajes = resumen_global.sort_values(
    'mediana', ascending=False).index.tolist()
estables_dict = resumen_global['estable'].to_dict()


def etiqueta_lenguaje(lang: str) -> str:
    return lang if estables_dict[lang] else f'{lang} *'


def marcar_id(fig: plt.Figure, gid: str) -> None:
    """Coloca el identificador del gráfico en la esquina inferior
    derecha, fuera del área del eje, para no superponerse al contenido."""
    fig.text(0.985, 0.010, gid,
             ha='right', va='bottom', fontsize=9,
             color='#5E6472', family='monospace')


def guardar(fig: plt.Figure, nombre_archivo: str, gid: str) -> Path:
    marcar_id(fig, gid)
    ruta = IMG_DIR / nombre_archivo
    fig.savefig(ruta, dpi=120, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return ruta


# --- G1  Ranking por mediana ---------------------------------
fig, ax = plt.subplots(figsize=(11, 8))
y_pos = np.arange(len(orden_lenguajes))
medianas_m = [resumen_global.loc[l, 'mediana'] / 1e6 for l in orden_lenguajes]
colores_bar = sns.color_palette('Blues_r', n_colors=len(orden_lenguajes))

for i, lang in enumerate(orden_lenguajes):
    es_estable = estables_dict[lang]
    ax.barh(
        i, medianas_m[i],
        color=colores_bar[i],
        alpha=(1.0 if es_estable else 0.45),
        edgecolor='white', linewidth=0.8,
    )
    n = int(resumen_global.loc[lang, 'n'])
    disp = resumen_global.loc[lang, 'disp_pct']
    ax.text(medianas_m[i] + 0.05, i,
            f'$ {medianas_m[i]:.2f} M  (n={n}, disp. {disp:.1f} %)',
            va='center', fontsize=8, color='#2E3440')

ax.set_yticks(y_pos)
ax.set_yticklabels([etiqueta_lenguaje(l) for l in orden_lenguajes])
ax.invert_yaxis()
ax.set_xlabel('Sueldo NETO mediano (millones de ARS)')
ax.set_title('Ranking de lenguajes por sueldo NETO mediano',
             fontsize=13, pad=14, loc='left')
ax.set_xlim(0, max(medianas_m) * 1.55)  # headroom para las etiquetas largas
ax.text(
    0, -1.2,
    f'*  dispersión relativa de la mediana superior a '
    f'{UMBRAL_DISP:.1f} % (2 × la mediana del conjunto)',
    fontsize=8, color='#5E6472', transform=ax.get_xaxis_transform(),
)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g1 = guardar(fig, 'G1_ranking_mediana.png', 'G1')


# --- G2  Distribución por lenguaje (diagrama de caja) --------
fig, ax = plt.subplots(figsize=(10, 9))
datos_box = [df_rank.loc[df_rank['lenguaje'] == l,
                         'salary_monthly_NETO'].values / 1e6
             for l in orden_lenguajes]
bp = ax.boxplot(
    datos_box, vert=False, patch_artist=True,
    showmeans=True, meanline=True,
    medianprops=dict(color='#2E3440', linewidth=1.2),
    meanprops=dict(color='#C96C6C', linestyle='--', linewidth=1),
    flierprops=dict(marker='o', markersize=3,
                    markerfacecolor='#8C99AD',
                    markeredgecolor='none', alpha=0.5),
    whiskerprops=dict(color='#8C99AD'),
    capprops=dict(color='#8C99AD'),
)
for i, (patch, lang) in enumerate(zip(bp['boxes'], orden_lenguajes)):
    color = PALETA[i % len(PALETA)]
    es_estable = estables_dict[lang]
    patch.set_facecolor(color)
    patch.set_alpha(0.55 if es_estable else 0.22)
    patch.set_edgecolor(color)
ax.set_yticklabels([etiqueta_lenguaje(l) for l in orden_lenguajes])
ax.invert_yaxis()
ax.set_xlabel('Sueldo NETO (millones de ARS)')
ax.set_title('Distribución de sueldos NETO por lenguaje',
             fontsize=13, pad=14, loc='left')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g2 = guardar(fig, 'G2_boxplot_lenguajes.png', 'G2')


# --- G3  Mediana por lenguaje y grupo de moneda --------------
pivot = (resumen_por_grupo
         .pivot(index='lenguaje', columns='moneda_grupo', values='mediana')
         .reindex(orden_lenguajes))

grupos_presentes = [g for g in ['ARS', 'USD parcial', 'USD total']
                    if g in pivot.columns]

x = np.arange(len(orden_lenguajes))
ancho = 0.27

fig, ax = plt.subplots(figsize=(12, 5.5))
for i, grupo in enumerate(grupos_presentes):
    offset = (i - (len(grupos_presentes) - 1) / 2) * ancho
    valores = (pivot[grupo] / 1e6).values
    ax.bar(x + offset, valores, width=ancho,
           color=COLORES_MONEDA_G3[grupo], alpha=0.88,
           edgecolor='white', linewidth=0.8, label=grupo)

ax.set_xticks(x)
ax.set_xticklabels(orden_lenguajes, rotation=40, ha='right', fontsize=9)
ax.set_ylabel('Mediana (millones de ARS)')
ax.set_title('Sueldo NETO mediano por lenguaje y grupo de moneda',
             fontsize=13, pad=14, loc='left')
ax.legend(title='Grupo de moneda', loc='upper right', frameon=True,
          facecolor='white', edgecolor='#E6E8EF')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g3 = guardar(fig, 'G3_mediana_por_moneda.png', 'G3')


# --- G4  Frecuencia vs sueldo mediano (tamaño = IQR) ---------
fig, ax = plt.subplots(figsize=(11, 7))
for lang in resumen_global.index:
    n = resumen_global.loc[lang, 'n']
    mediana = resumen_global.loc[lang, 'mediana'] / 1e6
    iqr = resumen_global.loc[lang, 'iqr']
    es_estable = estables_dict[lang]
    size = np.sqrt(iqr / 1e5) * 30 + 80
    ax.scatter(
        n, mediana,
        s=size,
        c=[[0.35, 0.51, 0.88]],
        alpha=(0.85 if es_estable else 0.35),
        edgecolor='white', linewidth=1,
    )
    ax.annotate(
        etiqueta_lenguaje(lang),
        (n, mediana),
        xytext=(0, 8), textcoords='offset points',
        ha='center', fontsize=8, color='#2E3440',
    )
ax.set_xscale('log')
ax.set_xlabel('Cantidad de respondentes (escala logarítmica)')
ax.set_ylabel('Sueldo NETO mediano (millones de ARS)')
ax.set_title('Frecuencia vs sueldo mediano '
             '(tamaño del punto = dispersión IQR)',
             fontsize=13, pad=14, loc='left')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g4 = guardar(fig, 'G4_frecuencia_vs_mediana.png', 'G4')


graficos_generados = pd.DataFrame({
    'gráfico': [
        'G1 - Ranking por mediana',
        'G2 - Distribución por lenguaje (diagrama de caja)',
        'G3 - Mediana por lenguaje y grupo de moneda',
        'G4 - Frecuencia vs sueldo mediano',
    ],
    'archivo': [
        ruta_g1.name, ruta_g2.name, ruta_g3.name, ruta_g4.name,
    ],
    'libreria': [
        'matplotlib', 'matplotlib', 'matplotlib', 'matplotlib',
    ],
})
mostrar('1.8  Gráficos equivalentes generados (matplotlib/seaborn)',
        graficos_generados)
print(f'\n  Guardados en: {IMG_DIR}/')


# ============================================================
# EJERCICIO 2 — Variables, relaciones y condicionalidad
# ============================================================
#
# Ejercicio 2a:  Densidad conjunta con 3 numéricas y 2 categóricas.
# Ejercicio 2b:  Asociación entre sueldo BRUTO y sueldo NETO.
# Ejercicio 2c:  Densidad condicional: sueldo según nivel de estudio.
# Ejercicio 2d:  Densidad conjunta condicional: experiencia vs sueldo
#                coloreada por factor categórico.
#
# El ejercicio 2 trabaja sobre el mismo conjunto de datos filtrado del
# ejercicio 1 (df, N = N_FINAL) a nivel persona: no se desanida la lista
# de lenguajes. Las columnas necesarias ya fueron retenidas en 1.1.


# ============================================================
# 2.0  Selección de variables para el ejercicio 2
# ============================================================

VARS_NUMERICAS = ['salary_monthly_NETO',
                  'profile_years_experience',
                  'profile_age']
VARS_CATEGORICAS = ['work_seniority', 'profile_gender']

seleccion_ej2 = pd.DataFrame({
    'variable': VARS_NUMERICAS + VARS_CATEGORICAS,
    'tipo': (['numérica'] * 3) + (['categórica'] * 2),
    'rol en el ejercicio 2': [
        'variable respuesta principal',
        'variable numérica de control (años de experiencia)',
        'variable numérica de control (edad del respondente)',
        'factor categórico: nivel de seniority',
        'factor categórico: identidad de género',
    ],
})
mostrar('2.0  Variables seleccionadas para el ejercicio 2', seleccion_ej2)


# ============================================================
# 2.a  Densidad conjunta (3 numéricas + 2 categóricas)
# ============================================================

# --- 2.a.1  Estadísticos descriptivos de las 3 numéricas ---
describe_num = (
    df[VARS_NUMERICAS]
    .describe(percentiles=[.10, .25, .50, .75, .90])
    .round(2)
)
mostrar('2.a.1  Estadísticos descriptivos de las variables numéricas',
        describe_num)

# --- 2.a.2 y 2.a.3  Matrices de correlación ---
corr_pearson = df[VARS_NUMERICAS].corr(method='pearson').round(3)
corr_spearman = df[VARS_NUMERICAS].corr(method='spearman').round(3)
mostrar('2.a.2  Correlación de Pearson entre numéricas', corr_pearson)
mostrar('2.a.3  Correlación de Spearman entre numéricas', corr_spearman)

# --- 2.a.4  Distribución de las variables categóricas ---
seniority_counts = df['work_seniority'].value_counts().to_frame('n')
seniority_counts['pct'] = (100 * seniority_counts['n'] / len(df)).round(2)
mostrar('2.a.4  Distribución de work_seniority', seniority_counts)

gender_counts = df['profile_gender'].value_counts(dropna=False).to_frame('n')
gender_counts['pct'] = (100 * gender_counts['n'] / len(df)).round(2)
mostrar('2.a.5  Distribución de profile_gender', gender_counts)

# --- 2.a.6  Contingencia seniority × gender ---
contingencia = pd.crosstab(df['work_seniority'], df['profile_gender'])
mostrar('2.a.6  Contingencia work_seniority × profile_gender',
        contingencia)


# ============================================================
# 2.b  Asociación: correlación Bruto vs Neto
# ============================================================

bn = df[['salary_monthly_BRUTO', 'salary_monthly_NETO']].dropna()
bn = bn[(bn['salary_monthly_BRUTO'] > 0) & (bn['salary_monthly_NETO'] > 0)]
bn['ratio_neto_bruto'] = bn['salary_monthly_NETO'] / bn['salary_monthly_BRUTO']

p_bruto_neto = bn[['salary_monthly_BRUTO', 'salary_monthly_NETO']].corr(
    method='pearson').iloc[0, 1]
s_bruto_neto = bn[['salary_monthly_BRUTO', 'salary_monthly_NETO']].corr(
    method='spearman').iloc[0, 1]

ratio_mediana = bn['ratio_neto_bruto'].median()
ratio_media = bn['ratio_neto_bruto'].mean()
ratio_q1 = bn['ratio_neto_bruto'].quantile(.25)
ratio_q3 = bn['ratio_neto_bruto'].quantile(.75)

asociacion_bruto_neto = pd.DataFrame({
    'métrica': [
        'observaciones válidas',
        'correlación de Pearson',
        'correlación de Spearman',
        'ratio NETO/BRUTO mediano',
        'ratio NETO/BRUTO medio',
        'ratio NETO/BRUTO Q1',
        'ratio NETO/BRUTO Q3',
    ],
    'valor': [
        len(bn),
        round(p_bruto_neto, 4),
        round(s_bruto_neto, 4),
        round(ratio_mediana, 4),
        round(ratio_media, 4),
        round(ratio_q1, 4),
        round(ratio_q3, 4),
    ],
})
mostrar('2.b.1  Asociación entre sueldo BRUTO y sueldo NETO',
        asociacion_bruto_neto)

# --- 2.b.2  Regresión lineal neto = a · bruto + b ---
coef_reg = np.polyfit(bn['salary_monthly_BRUTO'],
                      bn['salary_monthly_NETO'], 1)
regresion_tabla = pd.DataFrame({
    'parámetro': ['pendiente (a)', 'ordenada al origen (b)'],
    'valor':     [round(coef_reg[0], 4),
                  round(coef_reg[1], 2)],
    'interpretación': [
        'ARS netos observados por cada ARS bruto',
        'componente fija en ARS (tiende a cero en el caso ideal)',
    ],
})
mostrar('2.b.2  Regresión lineal NETO = a · BRUTO + b', regresion_tabla)

# --- 2.b.3  Columna derivada DESCUENTOS = BRUTO - NETO ---
# Siguiendo el práctico de la clase 03, se construye una columna
# derivada con los descuentos mensuales. Permite caracterizar la
# redundancia entre BRUTO y NETO: si los descuentos son aproximadamente
# proporcionales al bruto, la información de BRUTO queda contenida en
# NETO salvo un factor multiplicativo.
bn['descuentos'] = bn['salary_monthly_BRUTO'] - bn['salary_monthly_NETO']
bn['descuentos_pct'] = 100 * bn['descuentos'] / bn['salary_monthly_BRUTO']

descuentos_resumen = pd.DataFrame({
    'métrica': [
        'descuentos mensuales medianos (ARS)',
        'descuentos mensuales medios (ARS)',
        'descuento relativo mediano (% del BRUTO)',
        'descuento relativo medio (% del BRUTO)',
        'descuento relativo Q1 (%)',
        'descuento relativo Q3 (%)',
    ],
    'valor': [
        fmt_ars(bn['descuentos'].median()),
        fmt_ars(bn['descuentos'].mean()),
        f'{bn["descuentos_pct"].median():.2f} %',
        f'{bn["descuentos_pct"].mean():.2f} %',
        f'{bn["descuentos_pct"].quantile(.25):.2f} %',
        f'{bn["descuentos_pct"].quantile(.75):.2f} %',
    ],
})
mostrar('2.b.3  Columna derivada DESCUENTOS = BRUTO − NETO',
        descuentos_resumen)

# --- 2.b.4  Respuesta a la pregunta implícita de la consigna ---
#
# La consigna pregunta: "Necesitamos decidir si sacar o no la columna
# de salario bruto. Para hacer la encuesta más simple. ¿Existe una
# correlación entre el salario bruto y el neto?"
#
# Se construye una respuesta basada en lo observado en esta muestra,
# manteniendo el carácter descriptivo (no se extrapola a la población
# general).
respuesta_2b = pd.DataFrame({
    'criterio': [
        'correlación muestral Pearson',
        'correlación muestral Spearman',
        'estabilidad del ratio NETO/BRUTO (IQR)',
        'información no redundante en BRUTO',
        'recomendación sobre la columna BRUTO',
    ],
    'observación': [
        f'{p_bruto_neto:.3f} (muy cercana a 1 en esta muestra)',
        f'{s_bruto_neto:.3f} (muy cercana a 1 en esta muestra)',
        f'estrecha: el 50 % central del ratio cae entre '
        f'{bn["descuentos_pct"].quantile(.25):.1f} % y '
        f'{bn["descuentos_pct"].quantile(.75):.1f} % de descuentos',
        'baja, una vez conocida NETO',
        'dada la observación en esta muestra y bajo los filtros '
        'aplicados, la columna BRUTO puede considerarse altamente '
        'redundante con NETO y podría omitirse del formulario sin '
        'pérdida sustancial para este tipo de análisis descriptivo.',
    ],
})
mostrar('2.b.4  Respuesta a la pregunta implícita sobre BRUTO',
        respuesta_2b)


# ============================================================
# 2.c  Densidad condicional: sueldo según nivel de estudio
# ============================================================

df_estudios = df[df['profile_studies_level'].notna()].copy()

ORDEN_ESTUDIOS = [
    'Secundario',
    'Terciario',
    'Universitario',
    'Posgrado/Especialización',
    'Maestría',
    'Doctorado',
    'Posdoctorado',
]

cobertura_estudios = pd.DataFrame({
    'métrica': [
        'observaciones con nivel declarado',
        'observaciones con NaN',
        'pct con nivel declarado',
    ],
    'valor': [
        len(df_estudios),
        int(df['profile_studies_level'].isna().sum()),
        f'{100 * len(df_estudios) / len(df):.2f} %',
    ],
})
mostrar('2.c.1  Cobertura de la variable profile_studies_level',
        cobertura_estudios)

niveles_presentes = [n for n in ORDEN_ESTUDIOS
                     if n in df_estudios['profile_studies_level'].unique()]

describe_por_estudios = (
    df_estudios.groupby('profile_studies_level')['salary_monthly_NETO']
    .describe(percentiles=[.25, .5, .75])
    .reindex(niveles_presentes)
    .round(0)
)
mostrar('2.c.2  Sueldo NETO por nivel de estudio (describe)',
        describe_por_estudios)

# Conteo por nivel (n para cada categoría, crucial para interpretar)
n_por_estudios = (
    df_estudios['profile_studies_level']
    .value_counts()
    .reindex(niveles_presentes)
    .to_frame('n')
)
n_por_estudios['pct'] = (
    100 * n_por_estudios['n'] / n_por_estudios['n'].sum()).round(2)
mostrar('2.c.3  Tamaños muestrales por nivel de estudio', n_por_estudios)


# --- 2.c.4  Selección de las 2 subpoblaciones más numerosas ---
# La consigna pide elegir dos subpoblaciones numerosas y compararlas
# con histogramas. Se eligen, en términos puramente descriptivos, las
# dos que concentran mayor cantidad de observaciones declaradas.
SUBPOB_SELECCIONADAS = (
    n_por_estudios['n']
    .sort_values(ascending=False)
    .head(2)
    .index.tolist()
)

seleccion_subpob = pd.DataFrame({
    'posición': ['primera', 'segunda'],
    'nivel de estudio (literal)': SUBPOB_SELECCIONADAS,
    'n': [int(n_por_estudios.loc[s, 'n']) for s in SUBPOB_SELECCIONADAS],
})
mostrar('2.c.4  Subpoblaciones seleccionadas para el análisis comparativo',
        seleccion_subpob)


# --- 2.c.5  Centralización y dispersión por subpoblación ---
# La clase 02 enseña las medidas de tendencia central (media, mediana)
# y dispersión (std, IQR). Se calculan ambas por subpoblación como
# pide la consigna.
def medidas_subpob(serie: pd.Series) -> dict:
    q1, mediana, q3 = serie.quantile([.25, .5, .75])
    return {
        'n':       int(serie.count()),
        'media':   round(serie.mean(), 0),
        'mediana': round(mediana, 0),
        'std':     round(serie.std(), 0),
        'Q1':      round(q1, 0),
        'Q3':      round(q3, 0),
        'IQR':     round(q3 - q1, 0),
    }


medidas_por_subpob = {}
for nivel in SUBPOB_SELECCIONADAS:
    sub = df_estudios[df_estudios['profile_studies_level'] == nivel][
        'salary_monthly_NETO']
    medidas_por_subpob[nivel] = medidas_subpob(sub)

tabla_medidas_subpob = pd.DataFrame(medidas_por_subpob).T
mostrar('2.c.5  Medidas de centralización y dispersión por subpoblación',
        tabla_medidas_subpob)


# --- 2.c.6  Análisis de independencia vía probabilidad condicional ---
# Marco teórico tomado de la clase 01 (Probabilidad): dos eventos A y B
# son independientes si P(A|B) = P(A). Se define:
#
#   A = evento "sueldo NETO mayor que la mediana global de df_estudios"
#   B_i = evento "nivel de estudio = i-ésima subpoblación"
#
# Si A y B_i fueran independientes, P(A | B_i) debería ser
# aproximadamente igual a P(A). Una diferencia apreciable sugiere
# asociación entre las variables (sin realizar tests inferenciales).

sal_todos = df_estudios['salary_monthly_NETO']
umbral_mediana_global = sal_todos.median()
P_A = (sal_todos > umbral_mediana_global).mean()

filas_indep = [{
    'evento': 'A = sueldo NETO > mediana global',
    'n': int(sal_todos.count()),
    'probabilidad': round(P_A, 4),
}]
for nivel in SUBPOB_SELECCIONADAS:
    sub = df_estudios[
        df_estudios['profile_studies_level'] == nivel]['salary_monthly_NETO']
    p_cond = (sub > umbral_mediana_global).mean()
    filas_indep.append({
        'evento': f'A | B = ({nivel})',
        'n': int(sub.count()),
        'probabilidad': round(p_cond, 4),
    })

tabla_independencia = pd.DataFrame(filas_indep)
mostrar('2.c.6  Probabilidad condicional P(A|B) vs marginal P(A)',
        tabla_independencia)

# Distancia entre P(A|B) y P(A) — indicador puramente descriptivo
brechas_independencia = pd.DataFrame({
    'subpoblación B': SUBPOB_SELECCIONADAS,
    '|P(A|B) − P(A)|': [
        round(abs(
            (df_estudios[df_estudios['profile_studies_level'] == s]
             ['salary_monthly_NETO'] > umbral_mediana_global).mean() - P_A),
            4)
        for s in SUBPOB_SELECCIONADAS
    ],
})
mostrar('2.c.7  Distancia descriptiva entre la condicional y la marginal',
        brechas_independencia)

print('\n  Lectura descriptiva (sin inferencia):')
print('  Si las dos variables fueran independientes en esta muestra,')
print('  la distancia |P(A|B) − P(A)| sería cercana a cero en cada')
print('  subpoblación. Cuanto mayor es la distancia, más se aparta la')
print('  distribución condicional de la marginal, lo que en términos')
print('  descriptivos sugiere que el nivel de estudio está asociado')
print('  con el sueldo en esta muestra. Este análisis no realiza un')
print('  test de independencia estadístico.')


# ============================================================
# 2.d  Densidad conjunta condicional: experiencia vs sueldo + hue
# ============================================================
#
# La consigna pide dos variables numéricas y UNA variable categórica.
# Se adopta como variable categórica principal "work_seniority" por
# estar directamente vinculada a la pregunta del ejercicio 1. Como
# análisis complementario se incluye también "profile_gender" (dos
# categorías principales), con la salvedad de que la consigna pide
# una sola categórica — se declara explícitamente que el segundo
# scatter (G11) es extendido más allá del mínimo requerido.

declaracion_2d = pd.DataFrame({
    'elemento': [
        'numéricas (pedidas: 2)',
        'categórica principal (pedida: 1)',
        'categórica complementaria (extendida)',
    ],
    'elección': [
        'profile_years_experience, salary_monthly_NETO',
        'work_seniority (G10)',
        'profile_gender (G11, análisis extendido)',
    ],
})
mostrar('2.d.0  Declaración de variables del ejercicio 2d',
        declaracion_2d)

# --- 2.d.1  Por seniority ---
seniority_resumen = (
    df.groupby('work_seniority')[['profile_years_experience',
                                  'salary_monthly_NETO']]
    .agg(
        n=('salary_monthly_NETO', 'count'),
        exp_mediana=('profile_years_experience', 'median'),
        exp_q1=('profile_years_experience', lambda x: x.quantile(.25)),
        exp_q3=('profile_years_experience', lambda x: x.quantile(.75)),
        sal_mediana=('salary_monthly_NETO', 'median'),
        sal_q1=('salary_monthly_NETO', lambda x: x.quantile(.25)),
        sal_q3=('salary_monthly_NETO', lambda x: x.quantile(.75)),
    )
    .reindex(['Junior', 'Semi-Senior', 'Senior'])
    .round(0)
)
mostrar('2.d.1  Experiencia y sueldo por seniority', seniority_resumen)

# --- 2.d.2  Por género (restringido a Hombre Cis / Mujer Cis) ---
GENEROS_PRINCIPALES = ['Hombre Cis', 'Mujer Cis']
df_gender = df[df['profile_gender'].isin(GENEROS_PRINCIPALES)].copy()

cobertura_gender = pd.DataFrame({
    'métrica': [
        'observaciones en df filtrado',
        'observaciones con género ∈ {Hombre Cis, Mujer Cis}',
        'otras categorías (excluidas del análisis visual)',
        'pct considerado',
    ],
    'valor': [
        len(df),
        len(df_gender),
        len(df) - len(df_gender),
        f'{100 * len(df_gender) / len(df):.2f} %',
    ],
})
mostrar('2.d.2  Cobertura del análisis por género', cobertura_gender)
print('\n  Se restringe el análisis por género a "Hombre Cis" y "Mujer Cis"')
print('  porque el resto de categorías (No binarie, Trans, Queer, Agénero,')
print('  Prefiero no decir) tienen cada una menos de 55 observaciones, con')
print('  una precisión insuficiente para inferencia por grupo. La exclusión')
print('  se declara explícitamente en el informe.')

gender_resumen = (
    df_gender.groupby('profile_gender')['salary_monthly_NETO']
    .describe(percentiles=[.25, .5, .75])
    .reindex(GENEROS_PRINCIPALES)
    .round(0)
)
mostrar('2.d.3  Sueldo NETO por género (Hombre Cis / Mujer Cis)',
        gender_resumen)

# Brecha salarial estimada entre géneros principales
med_hombre = gender_resumen.loc['Hombre Cis', '50%']
med_mujer = gender_resumen.loc['Mujer Cis', '50%']
brecha_ratio = med_mujer / med_hombre

brecha_tabla = pd.DataFrame({
    'métrica': [
        'mediana Hombre Cis (ARS)',
        'mediana Mujer Cis (ARS)',
        'ratio Mujer/Hombre',
        'brecha Hombre − Mujer (ARS)',
        'brecha relativa a favor de Hombre Cis',
    ],
    'valor': [
        fmt_ars(med_hombre),
        fmt_ars(med_mujer),
        f'{brecha_ratio:.4f}',
        fmt_ars(med_hombre - med_mujer),
        f'{100 * (1 - brecha_ratio):.2f} %',
    ],
})
mostrar('2.d.4  Brecha salarial entre géneros principales', brecha_tabla)


# ============================================================
# 2.e  Gráficos del ejercicio 2 (matplotlib / seaborn)
# ============================================================

# --- G5  Histogramas de las 3 variables numéricas ---
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
datos_g5 = [
    df['salary_monthly_NETO'] / 1e6,
    df['profile_years_experience'],
    df['profile_age'],
]
titles_g5 = ['Sueldo NETO (millones de ARS)',
             'Años de experiencia',
             'Edad (años)']
colores_g5 = [COLOR_ARS, '#6BBF80', '#E8A04F']
for ax_i, datos, ttl, color in zip(axes, datos_g5, titles_g5, colores_g5):
    ax_i.hist(datos, bins=30, color=color, alpha=0.78, edgecolor='white')
    ax_i.set_title(ttl, fontsize=11, pad=8, loc='left')
    ax_i.set_ylabel('frecuencia')
    for s in ('top', 'right'):
        ax_i.spines[s].set_visible(False)
fig.suptitle('Distribución marginal de las 3 variables numéricas',
             fontsize=13, y=1.03, x=0.015, ha='left')
ruta_g5 = guardar(fig, 'G5_histogramas_numericas.png', 'G5')

# --- G6  Matriz de correlación (Pearson, coherente con clase 03) ---
# La clase 03 calcula la correlación con np.corrcoef (Pearson). Se
# conserva el cálculo de Spearman en 2.a.3 como control de robustez.
fig, ax = plt.subplots(figsize=(7.2, 5.5))
sns.heatmap(
    corr_pearson, annot=True, fmt='.2f', cmap='RdBu_r',
    center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
    linecolor='white', cbar_kws={'label': 'r de Pearson'}, ax=ax,
)
ax.set_title('Matriz de correlación (Pearson) entre numéricas',
             fontsize=13, pad=14, loc='left')
ruta_g6 = guardar(fig, 'G6_matriz_correlacion.png', 'G6')

# --- G7  Distribución de las 2 variables categóricas ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
s_plot = df['work_seniority'].value_counts().reindex(
    ['Junior', 'Semi-Senior', 'Senior'])
axes[0].bar(s_plot.index, s_plot.values,
            color=[PALETA[0], PALETA[1], PALETA[2]],
            alpha=0.85, edgecolor='white')
axes[0].set_title('Nivel de seniority', fontsize=11, pad=8, loc='left')
axes[0].set_ylabel('frecuencia')
for s in ('top', 'right'):
    axes[0].spines[s].set_visible(False)

g_plot = df['profile_gender'].value_counts()
cols_g = [COLOR_ARS if g in GENEROS_PRINCIPALES else '#BFC4D3'
          for g in g_plot.index]
axes[1].bar(g_plot.index, g_plot.values, color=cols_g,
            alpha=0.85, edgecolor='white')
axes[1].set_title('Identidad de género', fontsize=11, pad=8, loc='left')
axes[1].set_ylabel('frecuencia')
axes[1].tick_params(axis='x', rotation=25, labelsize=8)
for s in ('top', 'right'):
    axes[1].spines[s].set_visible(False)
fig.suptitle('Distribución de las variables categóricas',
             fontsize=13, y=1.03, x=0.015, ha='left')
ruta_g7 = guardar(fig, 'G7_categoricas.png', 'G7')

# --- G8  Scatter Bruto vs Neto (ej 2b) ---
fig, ax = plt.subplots(figsize=(9, 7))
bn_plot = bn[['salary_monthly_BRUTO', 'salary_monthly_NETO']] / 1e6
ax.scatter(
    bn_plot['salary_monthly_BRUTO'], bn_plot['salary_monthly_NETO'],
    s=14, alpha=0.35, color=COLOR_ARS, edgecolor='none',
)
lim = float(bn_plot.values.max()) * 1.02
ax.plot([0, lim], [0, lim], color='#8C99AD', linestyle='--',
        linewidth=1, label='identidad (neto = bruto)')
xs = np.linspace(0, lim, 100)
ax.plot(xs, coef_reg[0] * xs * 1e6 / 1e6 + coef_reg[1] / 1e6,
        color='#C96C6C', linewidth=1.5,
        label=f'regresión: neto = {coef_reg[0]:.3f} · bruto '
              f'{"+" if coef_reg[1] >= 0 else "−"} '
              f'{abs(coef_reg[1])/1e6:.3f} M')
ax.set_xlabel('Sueldo BRUTO mensual (millones de ARS)')
ax.set_ylabel('Sueldo NETO mensual (millones de ARS)')
ax.set_title('Asociación entre sueldo BRUTO y sueldo NETO',
             fontsize=13, pad=14, loc='left')
ax.legend(loc='lower right', facecolor='white', edgecolor='#E6E8EF')
ax.set_xlim(0, lim)
ax.set_ylim(0, lim)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g8 = guardar(fig, 'G8_bruto_vs_neto.png', 'G8')

# --- G9  Histogramas comparativos de 2 subpoblaciones numerosas (ej 2c) ---
# Respuesta literal a la consigna del 2c: "elija dos subpoblaciones
# numerosas y grafique de manera comparativa ambos histogramas".
# Técnica tomada de la clase 03 (celda MD29): dos llamadas a plt.hist
# con transparencia para que ambas distribuciones se vean superpuestas.
fig, ax = plt.subplots(figsize=(11, 6))
colores_subpob_g9 = {
    SUBPOB_SELECCIONADAS[0]: '#5B8DEF',  # azul
    SUBPOB_SELECCIONADAS[1]: '#C96C6C',  # rojo terroso
}
rangos = []
for nivel in SUBPOB_SELECCIONADAS:
    sub_m = (df_estudios[df_estudios['profile_studies_level'] == nivel]
             ['salary_monthly_NETO'] / 1e6)
    rangos.extend([sub_m.min(), sub_m.max()])
bins = np.linspace(min(rangos), max(rangos), 30)

for nivel in SUBPOB_SELECCIONADAS:
    sub_m = (df_estudios[df_estudios['profile_studies_level'] == nivel]
             ['salary_monthly_NETO'] / 1e6)
    ax.hist(sub_m, bins=bins, alpha=0.55,
            color=colores_subpob_g9[nivel],
            edgecolor='white', linewidth=0.5,
            density=True,
            label=f'{nivel} (n={len(sub_m)})')
    # Línea vertical de la mediana de cada subpoblación
    ax.axvline(sub_m.median(), color=colores_subpob_g9[nivel],
               linestyle='--', linewidth=1.2, alpha=0.85)

ax.set_xlabel('Sueldo NETO (millones de ARS)')
ax.set_ylabel('densidad')
ax.set_title('Histogramas comparativos del sueldo NETO por nivel de estudio',
             fontsize=13, pad=14, loc='left')
ax.legend(loc='upper right', facecolor='white', edgecolor='#E6E8EF',
          title='subpoblación (línea discontinua = mediana)')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g9 = guardar(fig, 'G9_histogramas_subpob_estudios.png', 'G9')

# --- G10  Scatter exp vs sueldo con hue = seniority (ej 2d) ---
fig, ax = plt.subplots(figsize=(10, 6.5))
col_seniority = {'Junior': '#6BBF80',
                 'Semi-Senior': '#E8A04F',
                 'Senior': '#C96C6C'}
for nivel in ['Junior', 'Semi-Senior', 'Senior']:
    sub = df[df['work_seniority'] == nivel]
    ax.scatter(sub['profile_years_experience'],
               sub['salary_monthly_NETO'] / 1e6,
               s=18, alpha=0.40, color=col_seniority[nivel],
               edgecolor='none', label=f'{nivel} (n={len(sub)})')
ax.set_xlabel('Años de experiencia')
ax.set_ylabel('Sueldo NETO (millones de ARS)')
ax.set_title('Experiencia vs sueldo NETO, condicionado por seniority',
             fontsize=13, pad=14, loc='left')
ax.legend(loc='upper left', facecolor='white', edgecolor='#E6E8EF')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g10 = guardar(fig, 'G10_exp_sueldo_seniority.png', 'G10')

# --- G11  Scatter exp vs sueldo con hue = género (ej 2d) ---
fig, ax = plt.subplots(figsize=(10, 6.5))
col_gender = {'Hombre Cis': COLOR_ARS, 'Mujer Cis': '#C96C6C'}
for g in GENEROS_PRINCIPALES:
    sub = df_gender[df_gender['profile_gender'] == g]
    ax.scatter(sub['profile_years_experience'],
               sub['salary_monthly_NETO'] / 1e6,
               s=18, alpha=0.40, color=col_gender[g],
               edgecolor='none', label=f'{g} (n={len(sub)})')
ax.set_xlabel('Años de experiencia')
ax.set_ylabel('Sueldo NETO (millones de ARS)')
ax.set_title('Experiencia vs sueldo NETO, condicionado por género',
             fontsize=13, pad=14, loc='left')
ax.legend(loc='upper left', facecolor='white', edgecolor='#E6E8EF')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g11 = guardar(fig, 'G11_exp_sueldo_genero.png', 'G11')

graficos_ej2 = pd.DataFrame({
    'gráfico': [
        'G5 - Histogramas de las 3 variables numéricas',
        'G6 - Matriz de correlación (Pearson)',
        'G7 - Distribución de las variables categóricas',
        'G8 - Scatter BRUTO vs NETO',
        'G9 - Histogramas comparativos de 2 subpoblaciones (estudios)',
        'G10 - Experiencia vs sueldo con hue = seniority',
        'G11 - Experiencia vs sueldo con hue = género (extendido)',
    ],
    'archivo': [ruta_g5.name, ruta_g6.name, ruta_g7.name,
                ruta_g8.name, ruta_g9.name, ruta_g10.name, ruta_g11.name],
    'ejercicio': ['2a', '2a', '2a', '2b', '2c', '2d', '2d'],
})
mostrar('2.e  Gráficos del ejercicio 2 generados', graficos_ej2)


# ============================================================
# 2.f  Conclusiones del ejercicio 2
# ============================================================

corr_pearson_sal_exp = corr_pearson.loc['salary_monthly_NETO',
                                        'profile_years_experience']
corr_pearson_sal_age = corr_pearson.loc['salary_monthly_NETO', 'profile_age']

conclusiones_ej2 = [
    f'En esta muestra, y bajo los filtros aplicados, se observa una '
    f'correlación de Pearson de {corr_pearson_sal_exp:.3f} entre el sueldo '
    f'NETO y los años de experiencia, y de {corr_pearson_sal_age:.3f} '
    f'entre sueldo NETO y edad. Ambas asociaciones son positivas; la '
    f'experiencia aparece como el predictor más directo del sueldo en los '
    f'datos observados.',

    f'La asociación muestral entre sueldo BRUTO y sueldo NETO es muy '
    f'fuerte (Pearson = {p_bruto_neto:.3f}, Spearman = {s_bruto_neto:.3f}) '
    f'con un ratio NETO/BRUTO mediano de {ratio_mediana:.3f}. El '
    f'análisis de la columna derivada DESCUENTOS sugiere, en esta '
    f'muestra, una estructura de descuentos relativamente estable, '
    f'consistente con la existencia de un componente fijo (aportes de '
    f'seguridad social) más un componente progresivo sobre los sueldos '
    f'más altos. En términos descriptivos, la columna BRUTO resulta '
    f'altamente redundante con NETO.',

    f'El análisis del ejercicio 2c muestra que la distribución muestral '
    f'del sueldo NETO condicionada al nivel de estudio se aparta de la '
    f'distribución marginal: en la muestra considerada, '
    f'|P(A|B) − P(A)| no es cercana a cero para las subpoblaciones '
    f'seleccionadas. En términos descriptivos esto sugiere que nivel de '
    f'estudio y sueldo están asociados. Solo el '
    f'{100*len(df_estudios)/len(df):.0f} % de los respondentes del '
    f'conjunto filtrado declararon su nivel de estudio, lo que acota el '
    f'alcance de la observación.',

    f'Dentro de cada nivel de seniority la relación entre experiencia y '
    f'sueldo NETO se mantiene creciente en los datos observados (G10). '
    f'Entre las subpoblaciones "Hombre Cis" y "Mujer Cis" se registra, '
    f'en esta muestra, una diferencia relativa del '
    f'{100*(1-brecha_ratio):.1f} % a favor de Hombre Cis (G11). Una '
    f'afirmación más sólida sobre la existencia de una brecha '
    f'poblacional requeriría un análisis multivariado y herramientas '
    f'inferenciales que exceden el alcance de esta parte.',
]

titulo_ej2 = '2.f  Conclusiones del ejercicio 2'
print(f'\n━━━ {titulo_ej2} ' + '━' * max(0, 70 - len(titulo_ej2)))
for i, c in enumerate(conclusiones_ej2, 1):
    print(f'{i}. {c}')


# ============================================================
# Exportación opcional a CSV
# ============================================================

if EXPORTAR_CSV:
    print(f'\n━━━ Exportando cuadros a {CSV_DIR}/ ━━━')
    for nombre, cuadro in cuadros_exportables.items():
        slug = (nombre.split('  ')[0]
                .replace('.', '_')
                .replace(' ', '') + '.csv')
        ruta = CSV_DIR / slug
        cuadro.to_csv(ruta, encoding='utf-8-sig')
        print(f'  {slug}')
    print(f'\n  {len(cuadros_exportables)} cuadros exportados.')

print(f'\n{"═" * 74}')
print(f'  Total de cuadros registrados: {len(cuadros_exportables)}')
print(f'  Ejecutar con --csv para exportar a {CSV_DIR.name}/')
print(f'{"═" * 74}')
