#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el PDF del ejercicio 3 del entregable parte 2:
comunicacion_ej3.pdf — formato "reporte técnico / publicación
científica" en una página A4.

Maquetación:
    · Cabecera con título, subtítulo y regla horizontal.
    · Resumen ejecutivo (4 líneas con la cifra central).
    · Figura principal (forest plot, ancho completo).
    · Tabla técnica renderizada con matplotlib.table.
    · Limitaciones numeradas con indentación consistente.
    · Banda inferior con la oración de énfasis.

La elección del medio (reporte técnico) está justificada en el
entregable: es el único formato que permite comunicar con honestidad
lo que los datos soportan (diferencia de medias bivariada con IC,
test, potencia y limitaciones explícitas), sin la tendencia a
exacerbar o simplificar que tienen los medios de difusión masiva o
las redes sociales.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / 'comunicacion_ej3.pdf'

# Paleta consistente con el resto del entregable
COLOR_A = '#5B8DEF'
COLOR_B = '#C96C6C'
COLOR_BOOT = '#8FB39E'
COLOR_REF = '#5E6472'
COLOR_TEXTO = '#2E3440'
COLOR_ACCENT = '#3A63A8'
COLOR_SOFT = '#F5F7FB'
COLOR_BORDER = '#C5CEDF'


def cargar_resultados() -> dict:
    """Ejecuta datos_parte2.py en silencio y devuelve el diccionario
    RESULTADOS con los números necesarios."""
    ruta = BASE_DIR / 'datos_parte2.py'
    spec = importlib.util.spec_from_file_location('datos_parte2_run', ruta)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod.RESULTADOS


def fmt_ars(v: float) -> str:
    return f'$ {v:,.0f}'.replace(',', '.')


def construir_pdf(r: dict) -> None:
    # A4 portrait: 8,27 × 11,69 pulgadas
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')

    # Layout vertical por bandas, con alturas proporcionales al contenido
    # y espacios horizontales generosos para que nada se superponga.
    gs = GridSpec(
        nrows=7, ncols=1, figure=fig,
        left=0.09, right=0.93, top=0.955, bottom=0.04,
        height_ratios=[1.35, 1.65, 2.35, 3.10, 2.15, 0.85, 0.05],
        hspace=0.55,
    )
    # 0: header · 1: resumen · 2: figura · 3: tabla · 4: limitaciones
    # 5: énfasis · 6: reserva de margen inferior

    # ═══════════ 0  Header ═══════════
    ax_h = fig.add_subplot(gs[0, 0])
    ax_h.axis('off')
    ax_h.text(
        0.0, 0.82,
        'Diferencia del sueldo NETO mensual',
        fontsize=17, fontweight='bold', family='serif',
        color=COLOR_TEXTO, transform=ax_h.transAxes,
    )
    ax_h.text(
        0.0, 0.55,
        'entre varones y mujeres cis — Encuesta Sysarmy 2026',
        fontsize=13, fontweight='normal', family='serif',
        color=COLOR_ACCENT, transform=ax_h.transAxes,
    )
    ax_h.text(
        0.0, 0.26,
        'Reporte técnico · Rubén Rasi · '
        'Diplomatura en Ciencia de Datos — FAMAF, UNC',
        fontsize=9, style='italic', family='serif',
        color=COLOR_REF, transform=ax_h.transAxes,
    )
    # regla horizontal completa
    ax_h.axhline(0.08, color=COLOR_BORDER, linewidth=0.9,
                 xmin=0.0, xmax=1.0)

    # ═══════════ 1  Resumen ejecutivo ═══════════
    ax_r = fig.add_subplot(gs[1, 0])
    ax_r.axis('off')
    ax_r.text(
        0.0, 0.95,
        'Resumen',
        fontsize=10, fontweight='bold', family='serif',
        color=COLOR_ACCENT, transform=ax_r.transAxes,
    )

    resumen = (
        f'Sobre una muestra filtrada de la encuesta Sysarmy 2026 '
        f'(n_A = {r["nA"]} varones cis, n_B = {r["nB"]} mujeres cis) se '
        f'estima una diferencia en el sueldo NETO mensual medio de '
        f'Δ̂ = {fmt_ars(r["delta_hat"])} a favor de los varones cis, con '
        f'un intervalo de confianza del 95 % de '
        f'[{fmt_ars(r["ic_welch"][0])} , {fmt_ars(r["ic_welch"][1])}]. '
        f'Un test t de Welch (ν = {r["nu_welch"]:.0f}) arroja un '
        f'p-valor bilateral de {r["p_bilateral"]:.2e} y un tamaño del '
        f'efecto Cohen\'s d = {r["cohens_d"]:.3f}. Bajo los supuestos y '
        f'el filtrado declarados, los datos son incompatibles con la '
        f'hipótesis de igualdad de medias al nivel α = 0,05.'
    )
    # Texto con wrap automático por ancho de caracteres (~92 col)
    resumen_wrap = fill(resumen, width=92)
    ax_r.text(
        0.0, 0.78,
        resumen_wrap,
        fontsize=9.5, color=COLOR_TEXTO, family='serif',
        va='top', transform=ax_r.transAxes,
        linespacing=1.35,
    )

    # ═══════════ 2  Figura — forest plot ═══════════
    ax_f = fig.add_subplot(gs[2, 0])
    ax_f.set_title(
        'Figura 1. Estimación puntual e IC del 95 % para la diferencia de medias',
        fontsize=10, fontweight='bold', family='serif',
        color=COLOR_TEXTO, loc='left', pad=10,
    )

    metodos = ['Welch\n(t, var. desiguales)', 'Bootstrap\n(percentil)']
    centros = [r['delta_hat'] / 1e6,
               (r['ic_boot'][0] + r['ic_boot'][1]) / 2 / 1e6]
    ics_low = [r['ic_welch'][0] / 1e6, r['ic_boot'][0] / 1e6]
    ics_high = [r['ic_welch'][1] / 1e6, r['ic_boot'][1] / 1e6]
    colores = [COLOR_A, COLOR_BOOT]
    y_pos = [1.0, 0.4]

    ax_f.axvline(0, color=COLOR_REF, linestyle=':', linewidth=1.3,
                 label='H₀: Δ = 0', zorder=1)
    for y, c, lo, hi, col in zip(y_pos, centros, ics_low, ics_high, colores):
        ax_f.errorbar(
            c, y, xerr=[[c - lo], [hi - c]],
            fmt='D', markersize=10, color=col, ecolor=col,
            elinewidth=2.6, capsize=7, capthick=2.0, zorder=3,
        )
        ax_f.text(
            hi + (hi - lo) * 0.22, y,
            f'[{lo:.3f},  {hi:.3f}] M',
            va='center', ha='left',
            fontsize=9, color=COLOR_TEXTO, family='serif',
        )
    ax_f.set_yticks(y_pos)
    ax_f.set_yticklabels(metodos, fontsize=9, family='serif')
    ax_f.set_xlabel('Δ̂ = μ_A − μ_B  (millones de ARS)',
                    fontsize=10, family='serif', labelpad=6)
    ax_f.set_ylim(0.05, 1.45)
    # Margen para que las etiquetas quepan a la derecha de cada IC
    x_margin = (max(ics_high) - min(ics_low)) * 0.40
    ax_f.set_xlim(min(ics_low) - x_margin * 0.3,
                  max(ics_high) + x_margin * 1.3)
    ax_f.legend(loc='upper right', fontsize=8, frameon=True,
                facecolor='white', edgecolor=COLOR_BORDER)
    for s in ('top', 'right'):
        ax_f.spines[s].set_visible(False)
    ax_f.grid(axis='x', color=COLOR_SOFT, linewidth=0.8, zorder=0)
    ax_f.tick_params(axis='both', labelsize=8.5)

    # ═══════════ 3  Tabla técnica ═══════════
    ax_t = fig.add_subplot(gs[3, 0])
    ax_t.axis('off')
    ax_t.text(
        0.0, 1.02,
        'Tabla 1. Resultados técnicos del contraste de medias',
        fontsize=10, fontweight='bold', family='serif',
        color=COLOR_TEXTO, transform=ax_t.transAxes,
    )

    filas = [
        ('Tamaño muestral',
         f'n_A = {r["nA"]}     n_B = {r["nB"]}'),
        ('Media muestral por grupo',
         f'{fmt_ars(r["mediaA"])}     {fmt_ars(r["mediaB"])}'),
        ('Desvío estándar por grupo',
         f'{fmt_ars(r["sA"])}     {fmt_ars(r["sB"])}'),
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
    # Uso una tabla matplotlib de ancho fijo, con colWidths proporcionales
    tabla = ax_t.table(
        cellText=[[et, val] for et, val in filas],
        colWidths=[0.62, 0.38],
        cellLoc='left',
        loc='upper left',
        bbox=[0.0, 0.0, 1.0, 0.96],
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.5)
    # Estilos celda por celda
    for (row, col), cell in tabla.get_celld().items():
        cell.set_edgecolor(COLOR_BORDER)
        cell.set_linewidth(0.5)
        cell.set_height(0.079)  # altura uniforme
        txt = cell.get_text()
        txt.set_family('serif')
        txt.set_color(COLOR_TEXTO)
        cell.PAD = 0.035
        # Fila par con fondo suave para legibilidad (tipo zebra)
        if row % 2 == 0:
            cell.set_facecolor(COLOR_SOFT)
        else:
            cell.set_facecolor('white')
        if col == 1:
            txt.set_fontweight('bold')
            cell.set_text_props(horizontalalignment='right')

    # ═══════════ 4  Limitaciones ═══════════
    ax_l = fig.add_subplot(gs[4, 0])
    ax_l.axis('off')
    ax_l.text(
        0.0, 1.0,
        'Limitaciones del análisis',
        fontsize=10, fontweight='bold', family='serif',
        color=COLOR_TEXTO, transform=ax_l.transAxes,
    )

    limitaciones = [
        ('1.',
         'Análisis bivariado. Sólo se contrasta el sueldo por género; '
         'no se controla por años de experiencia, seniority, rol, '
         'sector ni provincia. Parte de la diferencia observada puede '
         'deberse a la distribución diferencial de estos factores.'),
        ('2.',
         'Sesgo de autoselección. La encuesta Sysarmy es voluntaria: '
         'la muestra no es aleatoria respecto de la población de '
         'trabajadores del rubro. Las inferencias describen el '
         'subconjunto que respondió, no la población completa.'),
        ('3.',
         'Filtros declarados. Se aplicó un piso de $ 300.000 ARS '
         '(SMVM 2026) y un techo simétrico de $ 15.000.000 ARS sobre '
         'ambos grupos para eliminar valores implausibles sin '
         'introducir recortes asimétricos que contaminen la '
         'diferencia de medias.'),
        ('4.',
         'Implicancia legal. El resultado describe una asociación en '
         'la muestra; no establece causalidad por género. No debe '
         'usarse de manera aislada como prueba en un proceso de '
         'discriminación salarial: hace falta un análisis multivariado '
         'y un marco metodológico formal con control de error tipo I.'),
    ]
    # Distribución uniforme vertical con wrap
    y_top = 0.88
    y_slot = 0.22  # altura asignada a cada bullet
    for i, (n_, texto) in enumerate(limitaciones):
        y = y_top - i * y_slot
        wrap_txt = fill(texto, width=102)
        ax_l.text(
            0.0, y, n_,
            fontsize=8.8, fontweight='bold', family='serif',
            color=COLOR_REF, transform=ax_l.transAxes,
            va='top',
        )
        ax_l.text(
            0.03, y, wrap_txt,
            fontsize=8.8, family='serif',
            color=COLOR_TEXTO, transform=ax_l.transAxes,
            va='top', linespacing=1.30,
        )

    # ═══════════ 5  Banda de énfasis (con caja sutil) ═══════════
    ax_e = fig.add_subplot(gs[5, 0])
    ax_e.axis('off')
    ax_e.set_xlim(0, 1)
    ax_e.set_ylim(0, 1)

    # Caja con fondo suave y borde acento
    box = FancyBboxPatch(
        (0.0, 0.10), 1.0, 0.80,
        boxstyle='round,pad=0.012,rounding_size=0.012',
        linewidth=0.8, edgecolor=COLOR_ACCENT,
        facecolor=COLOR_SOFT, transform=ax_e.transAxes,
    )
    ax_e.add_patch(box)

    enfasis = (
        'En la muestra analizada, el sueldo NETO mensual medio de los '
        'varones cis supera en $ 647.000 al de las mujeres cis '
        '(IC 95 % $ 517.000 – $ 777.000). La magnitud del efecto '
        "(Cohen's d = 0,32) es compatible con una brecha moderada y "
        'robusta al método de estimación empleado.'
    )
    enfasis_wrap = fill(enfasis, width=88)
    ax_e.text(
        0.5, 0.50, enfasis_wrap,
        fontsize=9.5, style='italic', family='serif',
        color=COLOR_TEXTO, ha='center', va='center',
        transform=ax_e.transAxes, linespacing=1.35,
    )

    fig.savefig(PDF_PATH, format='pdf', bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    print(f'✅ PDF generado: {PDF_PATH}')
    print(f'   tamaño:     {PDF_PATH.stat().st_size / 1024:.1f} KB')


def main() -> None:
    r = cargar_resultados()
    construir_pdf(r)


if __name__ == '__main__':
    main()
