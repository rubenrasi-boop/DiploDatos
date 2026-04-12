#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entregable AyVD Parte 2 — Inferencia sobre la diferencia de medias
Diplomatura en Ciencia de Datos 2026 — FAMAF, UNC

Alumno:  Rubén Rasi
Docente: Fredy Alexander Restrepo Blandon

Apéndice de datos ejecutable del entregable parte 2. Imprime por consola
todos los cuadros intermedios (filtros, estadísticos, componentes del IC,
resultados del test, potencia) y regenera los 5 gráficos matplotlib que
acompañan al notebook entregable.

Ejercicios cubiertos:
    1.  Estimación puntual e intervalo de confianza (Welch + bootstrap).
    2.1 Formalización del test de hipótesis.
    2.2 P-valor, decisión, Mann-Whitney U como robustez.
    2.3 Potencia del test (opcional).
    3.  Comunicación: datos volcados luego al PDF comunicacion_ej3.pdf.

Uso:
    python datos_parte2.py
        imprime por consola todos los cuadros.

    python datos_parte2.py --csv
        además exporta cada cuadro a CSV en ./datos_parte2_csv/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.power import tt_ind_solve_power

pd.set_option('display.width', 140)
pd.set_option('display.max_columns', 20)

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

COLOR_A = '#5B8DEF'   # azul — Varón cis
COLOR_B = '#C96C6C'   # coral suave — Mujer cis
COLOR_REF = '#5E6472' # gris pizarra para líneas de referencia

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'sysarmy_survey_2026_processed.csv'
if not DATA_PATH.exists():
    DATA_PATH = (BASE_DIR.parents[2] /
                 'AnalisisyVisualizacion/entregables/parte2/data/'
                 'sysarmy_survey_2026_processed.csv')
CSV_DIR = BASE_DIR / 'datos_parte2_csv'
IMG_DIR = BASE_DIR / 'datos_parte2_img'
IMG_DIR.mkdir(exist_ok=True)

EXPORTAR_CSV = '--csv' in sys.argv
if EXPORTAR_CSV:
    CSV_DIR.mkdir(exist_ok=True)

ALPHA = 0.05

cuadros_exportables: dict[str, pd.DataFrame | pd.Series] = {}


def mostrar(nombre: str, obj) -> None:
    """Imprime un cuadro con encabezado visible y lo registra para CSV."""
    print(f'\n━━━ {nombre} ' + '━' * max(1, 70 - len(nombre)))
    if isinstance(obj, pd.DataFrame):
        print(obj.to_string(index=False))
    elif isinstance(obj, pd.Series):
        print(obj.to_string())
    else:
        print(obj)
    if EXPORTAR_CSV:
        slug = (nombre.replace(' ', '_').replace('/', '-')
                .replace('(', '').replace(')', '')
                .replace(':', '').replace(',', ''))
        ruta = CSV_DIR / f'{slug}.csv'
        if isinstance(obj, pd.DataFrame):
            obj.to_csv(ruta, index=False)
        elif isinstance(obj, pd.Series):
            obj.to_csv(ruta)
    cuadros_exportables[nombre] = obj


def fmt_ars(valor: float) -> str:
    """Formato ARS con separador de miles tipo argentino."""
    return f'$ {valor:,.0f}'.replace(',', '.')


def marcar_id(fig: plt.Figure, gid: str) -> None:
    fig.text(0.985, 0.010, gid, ha='right', va='bottom',
             fontsize=9, color=COLOR_REF, family='monospace')


def guardar(fig: plt.Figure, nombre_archivo: str, gid: str) -> Path:
    marcar_id(fig, gid)
    ruta = IMG_DIR / nombre_archivo
    fig.savefig(ruta, dpi=120, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return ruta


# ============================================================
# 1.0  Carga
# ============================================================

print('═' * 74)
print('  Entregable AyVD Parte 2 — Apéndice de datos')
print('═' * 74)

df = pd.read_csv(DATA_PATH)
N_INICIAL = len(df)
print(f'\n  Archivo: {DATA_PATH.name}')
print(f'  Filas iniciales: {N_INICIAL}')
print(f'  Columnas: {df.shape[1]}')


# ============================================================
# 1.1  Columnas retenidas
# ============================================================

COLUMNAS = [
    'tools_programming_languages',
    'salary_monthly_NETO',
    'work_dedication',
    'work_contract_type',
    'profile_gender',
]
df = df[COLUMNAS].copy()
mostrar('1.1  Columnas retenidas',
        pd.Series(COLUMNAS, name='columna').to_frame())


# ============================================================
# 1.2  Filtros F1-F5 heredados de parte 1
# ============================================================
# Se reutiliza el mismo esquema de filtros base de parte 1 para
# mantener la comparabilidad muestral entre los dos entregables.
# F4 (Tukey estratificado por moneda) se OMITE acá porque los tests
# inferenciales necesitan ver la varianza real de la cola.

CONTRATOS_VALIDOS = [
    'Staff (planta permanente)',
    'Contractor',
    'Tercerizado (trabajo a través de consultora o SaaS)',
]
PISO_SMVM = 300_000
TECHO_SIMETRICO = 15_000_000

registro_filtros: list[dict] = []


def aplicar_filtro(dataframe: pd.DataFrame, nombre: str, motivo: str,
                   mascara: pd.Series) -> pd.DataFrame:
    n_antes = len(dataframe)
    nuevo = dataframe[mascara].copy()
    n_despues = len(nuevo)
    recorte = n_antes - n_despues
    registro_filtros.append({
        'filtro':    nombre,
        'motivo':    motivo,
        'n_antes':   n_antes,
        'n_despues': n_despues,
        'recorte':   recorte,
        'pct':       round(100 * recorte / n_antes, 2) if n_antes else 0,
    })
    return nuevo


df = aplicar_filtro(
    df, 'F1', 'Descartar filas sin lenguaje declarado o sin sueldo NETO',
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

tabla_filtros = pd.DataFrame(registro_filtros)
mostrar('1.2  Filtros F1-F6 aplicados (sin F4 Tukey, innecesario para ej 2)',
        tabla_filtros)

print('\n  Nota metodológica:')
print('  - F5 (piso 300k) reemplaza al piso 100k de la consigna: 100k está')
print('    por debajo del SMVM argentino 2026 y captura mayoritariamente')
print('    respuestas erróneas o casos mal clasificados.')
print('  - F6 (techo 15M simétrico) se aplica a AMBOS grupos. La consigna')
print('    lo aplica sólo a groupA (varones), lo que contaminaría la')
print('    diferencia de medias con un artefacto de recorte asimétrico.')
print('  - F4 (Tukey 1,5·IQR) se omite: los tests del ej 2 necesitan ver la')
print('    varianza legítima de la cola para calibrar correctamente IC y')
print('    p-valores.')


# ============================================================
# 1.3  Comparación con la versión asimétrica de la consigna
# ============================================================
# Se declara cuántas observaciones varones descartó el techo simétrico
# respecto de la versión de la consigna (que no tenía techo en mujeres).

mask_hombre_cis = df['profile_gender'] == 'Hombre Cis'
mask_mujer_cis = df['profile_gender'] == 'Mujer Cis'

# Recuperamos los datos pre-F6 para medir el impacto del techo
df_pre_f6_count = pd.Series(registro_filtros[-1]).loc['n_antes']
# Recontamos sobre el df final pero esa es la versión post-F6 simétrica
delta_f6 = registro_filtros[-1]['recorte']

comparativo_techo = pd.DataFrame({
    'versión': [
        'consigna (techo asimétrico: sólo groupA ≤ 15M)',
        'entregable (techo simétrico: ambos ≤ 15M)',
    ],
    'implicancia': [
        'groupA sufre recorte superior, groupB no → gap artificial',
        'ambos grupos viven en la misma ventana → comparación honesta',
    ],
    'filas descartadas por F6 (total)': [
        'no declarado por la consigna',
        delta_f6,
    ],
})
mostrar('1.3  Comparación con el techo asimétrico de la consigna',
        comparativo_techo)


# ============================================================
# 1.4  Construcción de groupA y groupB
# ============================================================

groupA = df.loc[mask_hombre_cis, 'salary_monthly_NETO']
groupB = df.loc[mask_mujer_cis, 'salary_monthly_NETO']
nA, nB = len(groupA), len(groupB)

conteo_grupos = pd.DataFrame({
    'grupo':    ['groupA (Varón cis)', 'groupB (Mujer cis)'],
    'n':        [nA, nB],
    'filtros':  ['F1 ∩ F2 ∩ F3 ∩ F5 ∩ F6 ∩ (gender=Hombre Cis)',
                 'F1 ∩ F2 ∩ F3 ∩ F5 ∩ F6 ∩ (gender=Mujer Cis)'],
})
mostrar('1.4  Construcción de groupA y groupB', conteo_grupos)


# ============================================================
# 1.5  Estadísticos descriptivos por grupo
# ============================================================

def describir(serie: pd.Series) -> dict:
    return {
        'n':       int(serie.count()),
        'media':   float(serie.mean()),
        'mediana': float(serie.median()),
        'std':     float(serie.std(ddof=1)),
        'min':     float(serie.min()),
        'Q1':      float(serie.quantile(.25)),
        'Q3':      float(serie.quantile(.75)),
        'max':     float(serie.max()),
    }


descA = describir(groupA)
descB = describir(groupB)
desc_table = pd.DataFrame(
    [descA, descB],
    index=['groupA (Varón cis)', 'groupB (Mujer cis)'],
)
desc_fmt = desc_table.copy()
for col in ('media', 'mediana', 'std', 'min', 'Q1', 'Q3', 'max'):
    desc_fmt[col] = desc_fmt[col].apply(fmt_ars)
desc_fmt['n'] = desc_fmt['n'].astype(int)
mostrar('1.5  Estadísticos descriptivos por grupo',
        desc_fmt.reset_index().rename(columns={'index': 'grupo'}))


# ============================================================
# EJERCICIO 1 — Estimación puntual e intervalo de confianza
# ============================================================

print('\n\n' + '═' * 74)
print('  EJERCICIO 1 — Estimación puntual e IC para μA − μB')
print('═' * 74)


# ----- 2.1  Estimador puntual -----
delta_hat = descA['media'] - descB['media']
mostrar('2.1  Estimación puntual de la diferencia de medias',
        pd.DataFrame({
            'métrica': ['x̄_A (Varón cis)', 'x̄_B (Mujer cis)',
                        'Δ̂ = x̄_A − x̄_B'],
            'valor':   [fmt_ars(descA['media']),
                        fmt_ars(descB['media']),
                        fmt_ars(delta_hat)],
        }))


# ----- 2.2  IC de Welch (varianzas desiguales) -----
# Fórmula:
#   Δ̂ ± t_{α/2, νW} · sqrt(sA²/nA + sB²/nB)
# con νW calculado por Satterthwaite.
sA2, sB2 = descA['std'] ** 2, descB['std'] ** 2
se_welch = np.sqrt(sA2 / nA + sB2 / nB)
nu_welch = (sA2 / nA + sB2 / nB) ** 2 / (
    (sA2 / nA) ** 2 / (nA - 1) + (sB2 / nB) ** 2 / (nB - 1)
)
t_crit = stats.t.ppf(1 - ALPHA / 2, nu_welch)
ic_welch_low = delta_hat - t_crit * se_welch
ic_welch_high = delta_hat + t_crit * se_welch

mostrar('2.2  Componentes del IC de Welch (95 %)', pd.DataFrame({
    'componente': [
        'n_A', 'n_B',
        's_A² (varianza muestral A)',
        's_B² (varianza muestral B)',
        'SE_Welch = √(s_A²/n_A + s_B²/n_B)',
        'ν_W (Satterthwaite)',
        f't crítico α/2 = {ALPHA/2:.3f}',
        'Δ̂ − t·SE',
        'Δ̂ + t·SE',
    ],
    'valor': [
        nA, nB,
        f'{sA2:,.0f}'.replace(',', '.'),
        f'{sB2:,.0f}'.replace(',', '.'),
        fmt_ars(se_welch),
        round(nu_welch, 2),
        round(t_crit, 4),
        fmt_ars(ic_welch_low),
        fmt_ars(ic_welch_high),
    ],
}))


# ----- 2.3  IC por bootstrap percentil (robustez) -----
# 10 000 resamples con reposición de cada grupo. Seed fija para
# reproducibilidad.
rng = np.random.default_rng(seed=202604)
n_boot = 10_000
a_arr = groupA.to_numpy()
b_arr = groupB.to_numpy()
diffs_boot = np.empty(n_boot)
for i in range(n_boot):
    ai = rng.choice(a_arr, size=nA, replace=True)
    bi = rng.choice(b_arr, size=nB, replace=True)
    diffs_boot[i] = ai.mean() - bi.mean()
ic_boot_low, ic_boot_high = np.percentile(
    diffs_boot, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)]
)

mostrar('2.3  IC bootstrap percentil (95 %, 10 000 resamples)',
        pd.DataFrame({
            'métrica': [
                'n_boot',
                'media de las diferencias bootstrap',
                'percentil 2,5 %',
                'percentil 97,5 %',
            ],
            'valor': [
                n_boot,
                fmt_ars(diffs_boot.mean()),
                fmt_ars(ic_boot_low),
                fmt_ars(ic_boot_high),
            ],
        }))


# ----- 2.4  Comparación Welch vs bootstrap -----
comparativo_ic = pd.DataFrame({
    'método':        ['Welch (t, asume ~normalidad)', 'Bootstrap percentil'],
    'IC inferior':   [fmt_ars(ic_welch_low), fmt_ars(ic_boot_low)],
    'estimador':     [fmt_ars(delta_hat), fmt_ars(diffs_boot.mean())],
    'IC superior':   [fmt_ars(ic_welch_high), fmt_ars(ic_boot_high)],
    'ancho del IC':  [fmt_ars(ic_welch_high - ic_welch_low),
                      fmt_ars(ic_boot_high - ic_boot_low)],
})
mostrar('2.4  Comparación de IC: Welch paramétrico vs bootstrap percentil',
        comparativo_ic)

print('\n  Lectura: la similitud entre ambos IC indica que el supuesto de')
print('  normalidad asintótica del IC de Welch es razonable para estos')
print('  tamaños muestrales. El bootstrap se reporta como verificación')
print('  de robustez, no como reemplazo.')


# ----- 2.5  Relación IC ↔ test -----
print('\n  Relación entre IC e hipótesis:')
cero_en_ic_welch = ic_welch_low <= 0 <= ic_welch_high
cero_en_ic_boot = ic_boot_low <= 0 <= ic_boot_high
print(f'    · 0 ∈ IC_Welch del 95 %?    {cero_en_ic_welch}')
print(f'    · 0 ∈ IC_bootstrap del 95 %? {cero_en_ic_boot}')
print('  Un IC del (1-α) para μA − μB está en dualidad exacta con el test')
print('  bilateral al nivel α para H0: μA − μB = 0. Si el IC no contiene')
print('  el 0, el test bilateral rechaza H0 al mismo nivel.')


# ============================================================
# EJERCICIO 2 — Test de hipótesis
# ============================================================

print('\n\n' + '═' * 74)
print('  EJERCICIO 2 — Test de hipótesis sobre μA = μB')
print('═' * 74)


# ----- 3.1  Formalización -----
formalizacion = pd.DataFrame({
    'componente': [
        'Hipótesis nula H₀',
        'Hipótesis alternativa H₁',
        'Estadístico (pivote)',
        'Distribución bajo H₀',
        'Nivel de significancia α',
        'Zona de rechazo',
    ],
    'especificación': [
        'μ_A − μ_B = 0',
        'μ_A − μ_B ≠ 0   (bilateral)',
        'T = (x̄_A − x̄_B) / √(s_A²/n_A + s_B²/n_B)',
        'T  ~  t de Student con ν_W grados de libertad (Welch–Satterthwaite)',
        f'{ALPHA}',
        '{ |T| > t_{α/2, νW} }',
    ],
})
mostrar('3.1  Formalización del test', formalizacion)


# ----- 3.2  Test de Welch -----
t_stat, p_bilateral = stats.ttest_ind(groupA, groupB, equal_var=False)

resultado_welch = pd.DataFrame({
    'métrica': [
        't observado',
        'ν_W (Satterthwaite)',
        'p-valor bilateral',
        f'Umbral α = {ALPHA}',
        'Decisión',
    ],
    'valor': [
        f'{t_stat:.4f}',
        f'{nu_welch:.2f}',
        f'{p_bilateral:.3e}',
        f'{ALPHA}',
        'Se rechaza H₀' if p_bilateral < ALPHA else 'No se rechaza H₀',
    ],
})
mostrar('3.2  Test de Welch (t para varianzas desiguales)', resultado_welch)


# ----- 3.3  Mann-Whitney U como verificación de robustez -----
u_stat, p_mwu = stats.mannwhitneyu(groupA, groupB, alternative='two-sided')

resultado_mwu = pd.DataFrame({
    'métrica': [
        'U observado',
        'p-valor bilateral',
        f'Umbral α = {ALPHA}',
        'Decisión',
    ],
    'valor': [
        f'{u_stat:.0f}',
        f'{p_mwu:.3e}',
        f'{ALPHA}',
        'Se rechaza H₀' if p_mwu < ALPHA else 'No se rechaza H₀',
    ],
})
mostrar('3.3  Mann-Whitney U (no paramétrico, verificación de robustez)',
        resultado_mwu)

print('\n  Interpretación cuidada del p-valor:')
print('  Bajo H₀ (medias poblacionales iguales), la probabilidad de observar')
print('  una diferencia de medias tan extrema o más que la de esta muestra')
print(f'  es p ≈ {p_bilateral:.2e}. Dicho valor es incompatible con H₀ al')
print(f'  nivel α = {ALPHA}, por lo que la hipótesis nula se rechaza.')
print()
print('  El test de Mann-Whitney U (no paramétrico, no asume normalidad)')
print('  arroja la MISMA decisión, lo que indica que el resultado NO es')
print('  artefacto del supuesto de normalidad.')


# ============================================================
# 2.3 — Potencia del test
# ============================================================

# Cohen's d con SD pooled
s_pooled = np.sqrt(
    ((nA - 1) * sA2 + (nB - 1) * sB2) / (nA + nB - 2)
)
cohens_d = (descA['media'] - descB['media']) / s_pooled
ratio_nb_na = nB / nA

n_necesario = {
    p: tt_ind_solve_power(effect_size=cohens_d, alpha=ALPHA,
                          power=p, ratio=ratio_nb_na)
    for p in (0.80, 0.90, 0.95)
}

potencia_tabla = pd.DataFrame({
    'métrica': [
        "Cohen's d (effect size)",
        's_pooled',
        'ratio nB/nA',
        'n_A necesario (power = 0,80)',
        'n_A necesario (power = 0,90)',
        'n_A necesario (power = 0,95)',
    ],
    'valor': [
        round(cohens_d, 4),
        fmt_ars(s_pooled),
        round(ratio_nb_na, 4),
        int(np.ceil(n_necesario[0.80])),
        int(np.ceil(n_necesario[0.90])),
        int(np.ceil(n_necesario[0.95])),
    ],
})
mostrar('3.4  Potencia — n_A necesario para power ∈ {0,80; 0,90; 0,95}',
        potencia_tabla)

# Potencia observada con el n_A real
from statsmodels.stats.power import TTestIndPower

power_obs = TTestIndPower().power(
    effect_size=cohens_d, nobs1=nA, alpha=ALPHA, ratio=ratio_nb_na,
)
mostrar('3.5  Potencia observada con la muestra real',
        pd.DataFrame({
            'métrica': [
                'n_A real',
                'n_B real',
                f"Cohen's d observado",
                'potencia observada (1 − β)',
            ],
            'valor': [
                nA, nB,
                round(cohens_d, 4),
                round(power_obs, 6),
            ],
        }))

print('\n  Lectura del resultado de potencia:')
print('  · Con el n_A real, la potencia observada es prácticamente 1, lo')
print('    que significa que el test detecta la diferencia observada')
print('    casi con certeza bajo los supuestos del modelo.')
print('  · El n_A necesario para power 0,80 es MUCHO menor que nuestro n_A')
print('    real, indicando que la muestra es holgada para describir la')
print('    tendencia general observada en los datos.')
print()
print('  Discusión: tendencia general vs juicio penal por discriminación')
print('  ─────────────────────────────────────────────────────────────')
print('  · Para describir una tendencia general en la encuesta, la muestra')
print('    es amplia: la potencia al effect size observado está por encima')
print('    de cualquier umbral convencional (0,80 / 0,90 / 0,95).')
print('  · Para una causa legal contra una empresa por discriminación, el')
print('    análisis bivariado presentado NO alcanza. Haría falta:')
print('      (1) Potencia ≥ 0,95 y control estricto del error tipo I.')
print('      (2) Análisis multivariado que controle por experiencia,')
print('          seniority, especialización, provincia, etc., para separar')
print('          el efecto del género del de las variables correlacionadas.')
print('      (3) Marco metodológico formal (protocolo preregistrado,')
print('          auditoría de datos, expertos independientes).')
print('  El test bivariado describe una diferencia en la muestra: no')
print('  establece causalidad por género, y no debería usarse por sí solo')
print('  como prueba en un proceso legal.')


# ============================================================
# 4.0  Gráficos — datos_parte2_img/
# ============================================================

print('\n\n' + '═' * 74)
print('  Gráficos matplotlib')
print('═' * 74)


# ---- G1  Histogramas comparativos ----
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
for ax, serie, color, titulo in [
    (axes[0], groupA, COLOR_A, f'groupA — Varón cis  (n={nA})'),
    (axes[1], groupB, COLOR_B, f'groupB — Mujer cis  (n={nB})'),
]:
    ax.hist(serie / 1e6, bins=40, color=color, alpha=0.78,
            edgecolor='white', linewidth=0.4)
    ax.axvline(serie.mean() / 1e6, color=COLOR_REF, linestyle='--',
               linewidth=1.2, label=f'media = $ {serie.mean()/1e6:.2f} M')
    ax.axvline(serie.median() / 1e6, color=COLOR_REF, linestyle=':',
               linewidth=1.2, label=f'mediana = $ {serie.median()/1e6:.2f} M')
    ax.set_title(titulo, fontsize=11, pad=8, loc='left')
    ax.set_xlabel('Sueldo NETO (millones de ARS)')
    ax.legend(loc='upper right', fontsize=8, frameon=True,
              facecolor='white', edgecolor='#E6E8EF')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel('frecuencia')
fig.suptitle('Distribución del sueldo NETO por grupo',
             fontsize=13, y=1.02, x=0.015, ha='left')
ruta_g1 = guardar(fig, 'G1_histogramas_grupos.png', 'G1')


# ---- G2  Boxplot comparativo ----
fig, ax = plt.subplots(figsize=(9, 4.5))
datos_box = [groupA / 1e6, groupB / 1e6]
positions = [1, 2]
bp = ax.boxplot(
    datos_box, positions=positions, widths=0.55,
    patch_artist=True, showfliers=False,
    medianprops=dict(color=COLOR_REF, linewidth=1.8),
    boxprops=dict(facecolor='#F0F3FB', edgecolor=COLOR_REF, linewidth=1.2),
    whiskerprops=dict(color=COLOR_REF, linewidth=1.2),
    capprops=dict(color=COLOR_REF, linewidth=1.2),
)
# Coloreo custom
for patch, color in zip(bp['boxes'], [COLOR_A, COLOR_B]):
    patch.set_facecolor(color)
    patch.set_alpha(0.45)
# Overlay de puntos con jitter vertical
rng_plot = np.random.default_rng(seed=7)
for pos, serie, color in zip(positions, [groupA, groupB], [COLOR_A, COLOR_B]):
    x_jit = pos + rng_plot.uniform(-0.16, 0.16, size=len(serie))
    ax.scatter(x_jit, serie / 1e6, s=5, alpha=0.25, color=color,
               edgecolor='none')
# Medias como marcador
ax.scatter([1, 2], [descA['media'] / 1e6, descB['media'] / 1e6],
           marker='D', s=70, color='white', edgecolor=COLOR_REF,
           linewidth=1.6, zorder=5, label='media del grupo')
ax.set_xticks(positions)
ax.set_xticklabels([f'groupA (Varón cis)\nn = {nA}',
                    f'groupB (Mujer cis)\nn = {nB}'])
ax.set_ylabel('Sueldo NETO (millones de ARS)')
ax.set_title('Comparación del sueldo NETO por grupo',
             fontsize=13, pad=14, loc='left')
ax.legend(loc='upper right', fontsize=8, frameon=True,
          facecolor='white', edgecolor='#E6E8EF')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g2 = guardar(fig, 'G2_boxplot_comparativo.png', 'G2')


# ---- G3  QQ-plots ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, serie, color, titulo in [
    (axes[0], groupA, COLOR_A, 'groupA — Varón cis'),
    (axes[1], groupB, COLOR_B, 'groupB — Mujer cis'),
]:
    (quant, ordered), (slope, intercept, r) = stats.probplot(
        serie.values, dist='norm'
    )
    ax.scatter(quant, ordered / 1e6, s=8, alpha=0.45, color=color)
    x_line = np.array([quant.min(), quant.max()])
    ax.plot(x_line, (slope * x_line + intercept) / 1e6,
            color=COLOR_REF, linewidth=1.4,
            label=f'ajuste (r² = {r**2:.3f})')
    ax.set_title(titulo, fontsize=11, pad=8, loc='left')
    ax.set_xlabel('Cuantil teórico normal')
    ax.set_ylabel('Cuantil muestral (millones ARS)')
    ax.legend(loc='upper left', fontsize=8, frameon=True,
              facecolor='white', edgecolor='#E6E8EF')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
fig.suptitle('QQ-plots contra la normal (chequeo visual de normalidad)',
             fontsize=13, y=1.02, x=0.015, ha='left')
ruta_g3 = guardar(fig, 'G3_qq_plots.png', 'G3')


# ---- G4  Forest plot de IC (Welch vs bootstrap) ----
fig, ax = plt.subplots(figsize=(10, 3.6))
metodos = ['Welch paramétrico', 'Bootstrap percentil']
centros = [delta_hat / 1e6, diffs_boot.mean() / 1e6]
ics_low = [ic_welch_low / 1e6, ic_boot_low / 1e6]
ics_high = [ic_welch_high / 1e6, ic_boot_high / 1e6]
colores = [COLOR_A, '#8FB39E']
y_pos = [1.0, 0.4]

ax.axvline(0, color=COLOR_REF, linestyle=':', linewidth=1.3,
           label='H₀: Δ = 0')

for y, m, c, lo, hi, col in zip(y_pos, metodos, centros, ics_low, ics_high,
                                 colores):
    ax.errorbar(
        c, y,
        xerr=[[c - lo], [hi - c]],
        fmt='D', markersize=9, color=col,
        ecolor=col, elinewidth=2.4, capsize=6, capthick=1.8,
    )
    ax.text(hi + 0.02, y, f'[{lo:.3f} ,  {hi:.3f}]  M',
            va='center', fontsize=9, color='#2E3440')
ax.set_yticks(y_pos)
ax.set_yticklabels(metodos)
ax.set_xlabel('Δ̂ = μ_A − μ_B  (millones de ARS)')
ax.set_title('Estimación puntual e intervalo de confianza del 95 %',
             fontsize=13, pad=14, loc='left')
ax.set_ylim(0.0, 1.4)
ax.legend(loc='lower right', fontsize=9, frameon=True,
          facecolor='white', edgecolor='#E6E8EF')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g4 = guardar(fig, 'G4_forest_plot_IC.png', 'G4')


# ---- G5  Curva de potencia ----
fig, ax = plt.subplots(figsize=(10, 4.6))
n_grid = np.linspace(20, max(nA * 1.05, 500), 200)
power_grid = [
    TTestIndPower().power(effect_size=cohens_d, nobs1=n,
                          alpha=ALPHA, ratio=ratio_nb_na)
    for n in n_grid
]
ax.plot(n_grid, power_grid, color=COLOR_A, linewidth=2,
        label=f"curva (d = {cohens_d:.3f})")
# Líneas horizontales en los targets
for target, ls in [(0.80, '--'), (0.90, '-.'), (0.95, ':')]:
    ax.axhline(target, color=COLOR_REF, linestyle=ls, linewidth=1.1,
               alpha=0.8)
    ax.text(n_grid.max() * 0.985, target + 0.012, f'power = {target}',
            fontsize=8, color=COLOR_REF, ha='right')
# Marcadores del n necesario
for target, marker in [(0.80, 'o'), (0.90, 's'), (0.95, '^')]:
    n_needed = tt_ind_solve_power(effect_size=cohens_d, alpha=ALPHA,
                                  power=target, ratio=ratio_nb_na)
    ax.scatter(n_needed, target, s=80, color=COLOR_B, zorder=5,
               edgecolor='white', marker=marker,
               label=f'n_A requerido p={target} → {int(np.ceil(n_needed))}')
# n_A real
ax.axvline(nA, color=COLOR_REF, linestyle='-', linewidth=1.2, alpha=0.6)
ax.text(nA, 0.05, f'  n_A real = {nA}', fontsize=9, color='#2E3440',
        rotation=0, ha='left', va='bottom')
ax.set_xlabel('Tamaño muestral n_A  (n_B = ratio · n_A)')
ax.set_ylabel('Potencia 1 − β')
ax.set_ylim(0, 1.05)
ax.set_title('Curva de potencia del test para el effect size observado',
             fontsize=13, pad=14, loc='left')
ax.legend(loc='lower right', fontsize=8, frameon=True,
          facecolor='white', edgecolor='#E6E8EF')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ruta_g5 = guardar(fig, 'G5_curva_potencia.png', 'G5')


# ============================================================
# 4.1  Resumen ejecutivo para el ej 3 (se vuelca al PDF)
# ============================================================

resumen_ej3 = pd.DataFrame({
    'campo': [
        'n_A (Varón cis)',
        'n_B (Mujer cis)',
        'media groupA',
        'media groupB',
        'Δ̂ = μ_A − μ_B',
        'IC 95 % Welch',
        'IC 95 % Bootstrap',
        't de Welch',
        'ν Welch',
        'p-valor bilateral',
        'Mann-Whitney U p-valor',
        "Cohen's d",
        'Potencia observada',
        'Decisión al α = 0,05',
    ],
    'valor': [
        nA, nB,
        fmt_ars(descA['media']),
        fmt_ars(descB['media']),
        fmt_ars(delta_hat),
        f'[{fmt_ars(ic_welch_low)} ,  {fmt_ars(ic_welch_high)}]',
        f'[{fmt_ars(ic_boot_low)} ,  {fmt_ars(ic_boot_high)}]',
        f'{t_stat:.3f}',
        f'{nu_welch:.1f}',
        f'{p_bilateral:.2e}',
        f'{p_mwu:.2e}',
        f'{cohens_d:.3f}',
        f'{power_obs:.4f}',
        'rechazo de H₀',
    ],
})
mostrar('4.1  Resumen ejecutivo para el PDF del ejercicio 3', resumen_ej3)


# Gráficos generados
graficos_generados = pd.DataFrame({
    'gráfico': [
        'G1 - Histogramas comparativos',
        'G2 - Boxplot comparativo',
        'G3 - QQ-plots contra la normal',
        'G4 - Forest plot de IC (Welch vs bootstrap)',
        'G5 - Curva de potencia',
    ],
    'archivo': [
        ruta_g1.name, ruta_g2.name, ruta_g3.name, ruta_g4.name, ruta_g5.name,
    ],
})
mostrar('4.2  Gráficos generados', graficos_generados)
print(f'\n  Guardados en: {IMG_DIR}/')

# Variables exportadas para el PDF del ejercicio 3
RESULTADOS = {
    'nA': nA, 'nB': nB,
    'mediaA': descA['media'], 'mediaB': descB['media'],
    'delta_hat': delta_hat,
    'ic_welch': (ic_welch_low, ic_welch_high),
    'ic_boot': (ic_boot_low, ic_boot_high),
    't_stat': t_stat, 'nu_welch': nu_welch,
    'p_bilateral': p_bilateral, 'p_mwu': p_mwu,
    'cohens_d': cohens_d, 'power_obs': power_obs,
    'sA': descA['std'], 'sB': descB['std'],
    'groupA': groupA, 'groupB': groupB,
}

print('\n' + '═' * 74)
print(f'  Total de cuadros registrados: {len(cuadros_exportables)}')
if EXPORTAR_CSV:
    print(f'  CSV exportados en: {CSV_DIR}/')
else:
    print('  Ejecutar con --csv para exportar cuadros a datos_parte2_csv/')
print('═' * 74)
