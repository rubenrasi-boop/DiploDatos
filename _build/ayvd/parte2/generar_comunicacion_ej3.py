#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el PDF del ejercicio 3 del entregable parte 2:
comunicacion_ej3.pdf — reporte técnico de una página A4.

Diseño
------
Se abandonó el enfoque basado en GridSpec (que no puede garantizar la
ausencia de superposiciones entre secciones de contenido variable) y
se reemplazó por un layout manual en coordenadas de figura 0..1. Un
único cursor `y` recorre la página de arriba hacia abajo; cada
sección calcula su altura a partir del contenido real (número de
líneas envueltas × altura de línea) y avanza el cursor. De esa forma
ninguna sección puede invadir a la siguiente.

Secciones
---------
    1. Encabezado — título, subtítulo, autoría, regla horizontal.
    2. Resumen ejecutivo — 4–5 líneas envueltas.
    3. Figura 1 — forest plot con los dos IC (Welch y Bootstrap).
    4. Tabla 1 — resultados técnicos del contraste de medias.
    5. Limitaciones — 4 bullets numerados con wrap automático.
    6. Oración de énfasis — dentro de una caja redondeada.

Todas las mediciones de altura se hacen en pulgadas y se convierten a
fracciones de figura con `iy(inches)`. Las distancias dentro de cada
sección (padding, interlineado) están calculadas a partir de
`fontsize × linespacing / 72`, que es el alto real de una línea en
matplotlib.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

# CRÍTICO: desactivar el parseo de $...$ como mathtext. Los símbolos
# de moneda (por ejemplo "$ 300.000 ARS") se insertan como texto plano
# en varios lugares del reporte y si matplotlib los interpreta como
# delimitadores de math mode, los espacios desaparecen y el texto
# queda corrupto ("300.000ARS").
plt.rcParams['text.parse_math'] = False

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / 'comunicacion_ej3.pdf'

# ── Tamaño de página A4 vertical ──────────────────────────────────
PAGE_W = 8.27
PAGE_H = 11.69

# ── Paleta ───────────────────────────────────────────────────────
COLOR_A = '#5B8DEF'
COLOR_BOOT = '#8FB39E'
COLOR_REF = '#5E6472'
COLOR_TEXTO = '#2E3440'
COLOR_ACCENT = '#3A63A8'
COLOR_SOFT = '#F5F7FB'
COLOR_BORDER = '#C5CEDF'


# ── Conversores inch ↔ figure coords ─────────────────────────────
def ix(inches: float) -> float:
    """Convierte pulgadas a fracción de ancho de página."""
    return inches / PAGE_W


def iy(inches: float) -> float:
    """Convierte pulgadas a fracción de alto de página."""
    return inches / PAGE_H


def lh(fontsize_pt: float, linespacing: float = 1.40) -> float:
    """Alto de una línea en pulgadas dado un fontsize y linespacing."""
    return fontsize_pt * linespacing / 72.0


def cargar_resultados() -> dict:
    """Ejecuta datos_parte2.py en silencio y devuelve RESULTADOS."""
    ruta = BASE_DIR / 'datos_parte2.py'
    spec = importlib.util.spec_from_file_location('datos_parte2_run', ruta)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod.RESULTADOS


def fmt_ars(v: float) -> str:
    return f'$ {v:,.0f}'.replace(',', '.')


def construir_pdf(r: dict) -> None:
    fig = plt.figure(figsize=(PAGE_W, PAGE_H), facecolor='white')

    # Márgenes uniformes en fracción de figura
    MARGIN_L = ix(0.6)
    MARGIN_R = 1 - ix(0.6)
    CONTENT_W = MARGIN_R - MARGIN_L    # ~7,07"
    MARGIN_TOP_IN = 0.55
    MARGIN_BOT_IN = 0.50

    # Cursor vertical: va bajando a medida que se dibuja
    y = 1 - iy(MARGIN_TOP_IN)

    # ═════════════════════════════════════════════════════════════
    # 1.  ENCABEZADO
    # ═════════════════════════════════════════════════════════════
    # Título principal
    fig.text(MARGIN_L, y,
             'Diferencia del sueldo NETO mensual',
             fontsize=17, fontweight='bold', family='serif',
             color=COLOR_TEXTO, va='top')
    y -= iy(lh(17) + 0.05)

    # Subtítulo
    fig.text(MARGIN_L, y,
             'entre varones y mujeres cis — Encuesta Sysarmy 2026',
             fontsize=13, family='serif',
             color=COLOR_ACCENT, va='top')
    y -= iy(lh(13) + 0.04)

    # Autoría
    fig.text(MARGIN_L, y,
             'Reporte técnico · Rubén Rasi · '
             'Diplomatura en Ciencia de Datos — FAMAF, UNC',
             fontsize=9, style='italic', family='serif',
             color=COLOR_REF, va='top')
    y -= iy(lh(9) + 0.10)

    # Regla horizontal completa bajo el encabezado
    line = Line2D(
        [MARGIN_L, MARGIN_R], [y, y],
        color=COLOR_BORDER, linewidth=0.9,
        transform=fig.transFigure, figure=fig,
    )
    fig.lines.append(line)
    y -= iy(0.20)  # espacio después de la regla

    # ═════════════════════════════════════════════════════════════
    # 2.  RESUMEN
    # ═════════════════════════════════════════════════════════════
    fig.text(MARGIN_L, y, 'Resumen',
             fontsize=10.5, fontweight='bold', family='serif',
             color=COLOR_ACCENT, va='top')
    y -= iy(lh(10.5) + 0.07)

    resumen_txt = (
        f'Sobre una muestra filtrada de la encuesta Sysarmy 2026 '
        f'(n_A = {r["nA"]} varones cis, n_B = {r["nB"]} mujeres cis) se '
        f'estima una diferencia en el sueldo NETO mensual medio de '
        f'Δ̂ = {fmt_ars(r["delta_hat"])} a favor de los varones cis, con '
        f'un intervalo de confianza del 95 % de '
        f'[{fmt_ars(r["ic_welch"][0])} ,  {fmt_ars(r["ic_welch"][1])}]. '
        f'Un test t de Welch (ν = {r["nu_welch"]:.0f}) arroja un '
        f'p-valor bilateral de {r["p_bilateral"]:.2e} y un tamaño del '
        f'efecto Cohen\'s d = {r["cohens_d"]:.3f}. Bajo los supuestos y '
        f'el filtrado declarados, los datos son incompatibles con la '
        f'hipótesis de igualdad de medias al nivel α = 0,05.'
    )
    resumen_wrap = fill(resumen_txt, width=108)
    n_lines_res = resumen_wrap.count('\n') + 1
    fig.text(MARGIN_L, y, resumen_wrap,
             fontsize=9.5, family='serif', color=COLOR_TEXTO,
             va='top', linespacing=1.40)
    y -= iy(n_lines_res * lh(9.5) + 0.18)

    # ═════════════════════════════════════════════════════════════
    # 3.  FIGURA 1 — Forest plot
    # ═════════════════════════════════════════════════════════════
    fig.text(MARGIN_L, y,
             'Figura 1. Estimación puntual e intervalo de confianza '
             'del 95 % para la diferencia de medias',
             fontsize=10, fontweight='bold', family='serif',
             color=COLOR_TEXTO, va='top')
    y -= iy(lh(10) + 0.12)

    # Altura del cuadro del axes (no incluye xlabel ni ticks)
    FIG_H_IN = 1.40
    # Margen adicional POR DEBAJO del axes para tick labels + xlabel
    FIG_XLABEL_MARGIN_IN = 0.52
    # Margen adicional POR LA IZQUIERDA del axes para las etiquetas
    # multi-línea del eje Y ("Welch\n(t, varianzas desiguales)")
    FIG_YLABEL_INDENT_IN = 1.10

    axes_bottom = y - iy(FIG_H_IN)
    ax_f = fig.add_axes([
        MARGIN_L + ix(FIG_YLABEL_INDENT_IN),
        axes_bottom,
        CONTENT_W - ix(FIG_YLABEL_INDENT_IN),
        iy(FIG_H_IN),
    ])

    metodos = ['Welch\n(t, varianzas desiguales)', 'Bootstrap\n(percentil)']
    centros = [
        r['delta_hat'] / 1e6,
        (r['ic_boot'][0] + r['ic_boot'][1]) / 2 / 1e6,
    ]
    ics_low = [r['ic_welch'][0] / 1e6, r['ic_boot'][0] / 1e6]
    ics_high = [r['ic_welch'][1] / 1e6, r['ic_boot'][1] / 1e6]
    colores_mt = [COLOR_A, COLOR_BOOT]
    y_pos_mt = [1.0, 0.40]

    ax_f.axvline(0, color=COLOR_REF, linestyle=':', linewidth=1.3,
                 label='H₀: Δ = 0', zorder=1)
    for yp, c, lo, hi, col in zip(
        y_pos_mt, centros, ics_low, ics_high, colores_mt,
    ):
        ax_f.errorbar(
            c, yp, xerr=[[c - lo], [hi - c]],
            fmt='D', markersize=10, color=col, ecolor=col,
            elinewidth=2.6, capsize=7, capthick=2.0, zorder=3,
        )
        ax_f.text(
            hi + (hi - lo) * 0.22, yp,
            f'[{lo:.3f} ,  {hi:.3f}] M',
            va='center', ha='left',
            fontsize=9, color=COLOR_TEXTO, family='serif',
        )
    ax_f.set_yticks(y_pos_mt)
    ax_f.set_yticklabels(metodos, fontsize=9, family='serif')
    ax_f.set_xlabel(
        'Δ̂ = μ_A − μ_B  (millones de ARS)',
        fontsize=9.5, family='serif', labelpad=6,
    )
    ax_f.set_ylim(0.0, 1.45)
    # Margen en x para que las etiquetas [lo, hi] quepan a la derecha
    x_max_data = max(ics_high)
    x_min_data = min(0.0, min(ics_low))
    span = x_max_data - x_min_data
    ax_f.set_xlim(
        x_min_data - span * 0.05,
        x_max_data + span * 0.55,
    )
    ax_f.legend(
        loc='upper right', fontsize=8, frameon=True,
        facecolor='white', edgecolor=COLOR_BORDER,
    )
    for s in ('top', 'right'):
        ax_f.spines[s].set_visible(False)
    ax_f.grid(axis='x', color=COLOR_SOFT, linewidth=0.8, zorder=0)
    ax_f.tick_params(axis='both', labelsize=8.5)

    # Avanzo el cursor: el axes consume FIG_H_IN y el xlabel consume
    # FIG_XLABEL_MARGIN_IN adicional hacia abajo.
    y -= iy(FIG_H_IN + FIG_XLABEL_MARGIN_IN)

    # ═════════════════════════════════════════════════════════════
    # 4.  TABLA 1 — Resultados técnicos
    # ═════════════════════════════════════════════════════════════
    fig.text(MARGIN_L, y,
             'Tabla 1. Resultados técnicos del contraste de medias',
             fontsize=10, fontweight='bold', family='serif',
             color=COLOR_TEXTO, va='top')
    y -= iy(lh(10) + 0.10)

    filas = [
        ('Tamaño muestral',
         f'n_A = {r["nA"]}     n_B = {r["nB"]}'),
        ('Media muestral por grupo',
         f'{fmt_ars(r["mediaA"])}      {fmt_ars(r["mediaB"])}'),
        ('Desvío estándar por grupo',
         f'{fmt_ars(r["sA"])}      {fmt_ars(r["sB"])}'),
        ('Estimador puntual  Δ̂ = x̄_A − x̄_B',
         fmt_ars(r['delta_hat'])),
        ('IC 95 % (Welch, ν de Satterthwaite)',
         f'[{fmt_ars(r["ic_welch"][0])} ,  {fmt_ars(r["ic_welch"][1])}]'),
        ('IC 95 % (Bootstrap, 10 000 resamples)',
         f'[{fmt_ars(r["ic_boot"][0])} ,  {fmt_ars(r["ic_boot"][1])}]'),
        ('Welch — estadístico t · ν',
         f'{r["t_stat"]:.3f}     ·     {r["nu_welch"]:.1f}'),
        ('P-valor bilateral (Welch)',
         f'{r["p_bilateral"]:.2e}'),
        ('P-valor Mann-Whitney U (robustez)',
         f'{r["p_mwu"]:.2e}'),
        ("Effect size (Cohen's d)",
         f'{r["cohens_d"]:.3f}'),
        ('Potencia observada (1 − β)',
         f'{r["power_obs"]:.4f}'),
        ('Decisión bilateral  α = 0,05',
         'se rechaza H₀: μ_A = μ_B'),
    ]
    n_rows = len(filas)
    ROW_H_IN = 0.170
    TABLE_H_IN = n_rows * ROW_H_IN

    ax_t = fig.add_axes(
        [MARGIN_L, y - iy(TABLE_H_IN), CONTENT_W, iy(TABLE_H_IN)]
    )
    ax_t.axis('off')

    tbl = ax_t.table(
        cellText=[[et, val] for et, val in filas],
        colWidths=[0.60, 0.40],
        cellLoc='left',
        loc='upper left',
        bbox=[0.0, 0.0, 1.0, 1.0],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(COLOR_BORDER)
        cell.set_linewidth(0.5)
        t = cell.get_text()
        t.set_family('serif')
        t.set_color(COLOR_TEXTO)
        cell.PAD = 0.05
        # Cebra para legibilidad
        cell.set_facecolor(COLOR_SOFT if row % 2 == 0 else 'white')
        if col == 1:
            t.set_fontweight('bold')
            cell.set_text_props(horizontalalignment='right')

    y -= iy(TABLE_H_IN + 0.18)

    # ═════════════════════════════════════════════════════════════
    # 5.  LIMITACIONES
    # ═════════════════════════════════════════════════════════════
    fig.text(MARGIN_L, y, 'Limitaciones del análisis',
             fontsize=10, fontweight='bold', family='serif',
             color=COLOR_TEXTO, va='top')
    y -= iy(lh(10) + 0.08)

    limitaciones = [
        'Análisis bivariado. Sólo se contrasta el sueldo por género; no se '
        'controla por años de experiencia, seniority, rol, sector ni '
        'provincia. Parte de la diferencia observada puede deberse a la '
        'distribución diferencial de estos factores.',

        'Sesgo de autoselección. La encuesta Sysarmy es voluntaria: la '
        'muestra no es aleatoria respecto de la población de trabajadores '
        'del rubro. Las inferencias describen el subconjunto que respondió, '
        'no la población completa.',

        'Filtros declarados. Se aplicó un piso de $ 300.000 ARS (SMVM 2026) '
        'y un techo simétrico de $ 15.000.000 ARS sobre ambos grupos para '
        'eliminar valores implausibles sin introducir recortes asimétricos '
        'que contaminen la diferencia de medias.',

        'Implicancia legal. El resultado describe una asociación en la '
        'muestra; no establece causalidad por género. No debe usarse de '
        'manera aislada como prueba en un proceso de discriminación '
        'salarial: hace falta un análisis multivariado y un marco '
        'metodológico formal con control de error tipo I.',
    ]
    LIM_FONT = 9
    LIM_WIDTH = 108       # caracteres por línea (wrap textwrap)
    LIM_LH_IN = lh(LIM_FONT)   # alto de línea en pulgadas
    LIM_GAP_IN = 0.07     # espacio entre bullets
    INDENT = ix(0.26)     # indentación del texto respecto del número

    for i, texto in enumerate(limitaciones, 1):
        wrapped = fill(texto, width=LIM_WIDTH)
        n_l = wrapped.count('\n') + 1
        # Número del bullet
        fig.text(MARGIN_L, y, f'{i}.',
                 fontsize=LIM_FONT, fontweight='bold', family='serif',
                 color=COLOR_REF, va='top')
        # Texto envuelto, indentado
        fig.text(MARGIN_L + INDENT, y, wrapped,
                 fontsize=LIM_FONT, family='serif',
                 color=COLOR_TEXTO, va='top', linespacing=1.40)
        y -= iy(n_l * LIM_LH_IN + LIM_GAP_IN)

    y -= iy(0.04)  # pequeño respiro antes de la caja de énfasis

    # ═════════════════════════════════════════════════════════════
    # 6.  BANDA DE ÉNFASIS (con caja redondeada)
    # ═════════════════════════════════════════════════════════════
    enfasis_txt = (
        'En la muestra analizada, el sueldo NETO mensual medio de los '
        'varones cis supera en $ 647.000 al de las mujeres cis '
        '(IC 95 % $ 517.000 – $ 777.000). La magnitud del efecto '
        "(Cohen's d = 0,32) es compatible con una brecha moderada y "
        'robusta al método de estimación empleado.'
    )
    enfasis_wrap = fill(enfasis_txt, width=100)
    n_l_enf = enfasis_wrap.count('\n') + 1

    ENF_FONT = 9.5
    ENF_LH_IN = lh(ENF_FONT)
    PAD_TOP_IN = 0.18
    PAD_BOT_IN = 0.18
    TEXT_H_IN = n_l_enf * ENF_LH_IN
    BOX_H_IN = TEXT_H_IN + PAD_TOP_IN + PAD_BOT_IN

    box_top = y
    box_bot = box_top - iy(BOX_H_IN)

    box = FancyBboxPatch(
        (MARGIN_L, box_bot), CONTENT_W, box_top - box_bot,
        boxstyle='round,pad=0.0,rounding_size=0.012',
        facecolor=COLOR_SOFT, edgecolor=COLOR_ACCENT, linewidth=0.9,
        transform=fig.transFigure,
    )
    fig.patches.append(box)

    # Texto centrado verticalmente dentro de la caja
    text_y_center = (box_top + box_bot) / 2
    fig.text(
        (MARGIN_L + MARGIN_R) / 2, text_y_center, enfasis_wrap,
        fontsize=ENF_FONT, style='italic', family='serif',
        color=COLOR_TEXTO, ha='center', va='center',
        linespacing=1.40,
    )

    # Guardar SIN bbox_inches='tight' para mantener el tamaño A4 exacto
    fig.savefig(PDF_PATH, format='pdf', facecolor='white')
    plt.close(fig)

    print(f'✅ PDF generado: {PDF_PATH}')
    print(f'   tamaño:     {PDF_PATH.stat().st_size / 1024:.1f} KB')


def main() -> None:
    r = cargar_resultados()
    construir_pdf(r)


if __name__ == '__main__':
    main()
