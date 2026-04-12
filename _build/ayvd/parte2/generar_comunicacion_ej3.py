#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el PDF del ejercicio 3 del entregable parte 2:
comunicacion_ej3.pdf — formato "reporte técnico / publicación científica"
en una página A4.

Estructura de la página:
    ┌─────────────────────────────────────────────────────────┐
    │ Título                                                  │
    │ Resumen (2-3 líneas con la cifra central)               │
    │                                                          │
    │ Figura principal (forest plot con la diferencia y el IC)│
    │                                                          │
    │ Tabla técnica compacta                                  │
    │                                                          │
    │ Limitaciones (bullets)                                  │
    │ Oración con énfasis                                     │
    └─────────────────────────────────────────────────────────┘

La elección del medio está justificada en el informe: es el único
formato que permite comunicar con honestidad lo que los datos
soportan (diferencia de medias bivariada con IC, test, potencia y
limitaciones explícitas) sin caer en la tendencia a exacerbar o
simplificar que tienen los medios de difusión masiva o las redes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec


BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / 'comunicacion_ej3.pdf'


def cargar_resultados():
    """Ejecuta datos_parte2.py una vez e importa el diccionario RESULTADOS."""
    ruta = BASE_DIR / 'datos_parte2.py'
    spec = importlib.util.spec_from_file_location('datos_parte2_run', ruta)
    mod = importlib.util.module_from_spec(spec)
    import io
    import contextlib
    # Silenciamos la salida por consola del apéndice al importarlo.
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod.RESULTADOS


def fmt_ars(v):
    return f'$ {v:,.0f}'.replace(',', '.')


def fmt_ars_m(v):
    return f'$ {v/1e6:.3f} M'


COLOR_A = '#5B8DEF'
COLOR_B = '#C96C6C'
COLOR_REF = '#5E6472'
COLOR_TEXTO = '#2E3440'


def construir_pdf(r):
    # A4 portrait en pulgadas
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    gs = GridSpec(
        nrows=100, ncols=1, figure=fig,
        left=0.08, right=0.94, top=0.97, bottom=0.04,
        hspace=0.0,
    )

    # --------------- Encabezado: título y resumen ---------------
    ax_header = fig.add_subplot(gs[0:16, 0])
    ax_header.axis('off')
    ax_header.text(
        0, 0.95,
        'Diferencia del sueldo NETO mensual entre varones y mujeres cis',
        fontsize=15, fontweight='bold',
        color=COLOR_TEXTO, family='serif',
    )
    ax_header.text(
        0, 0.78,
        'Encuesta Sysarmy 2026 · Reporte técnico · Rubén Rasi',
        fontsize=9, style='italic', color=COLOR_REF, family='serif',
    )
    ax_header.axhline(0.70, color='#C5CEDF', linewidth=0.6)

    delta_hat = r['delta_hat']
    ic_w_low, ic_w_high = r['ic_welch']
    p_val = r['p_bilateral']
    d = r['cohens_d']
    nA, nB = r['nA'], r['nB']

    resumen_texto = (
        f'Sobre una muestra filtrada de la encuesta Sysarmy 2026 (n_A = {nA} varones cis,'
        f' n_B = {nB} mujeres cis) se estima una diferencia en el sueldo NETO mensual medio de\n'
        f'Δ̂ = {fmt_ars(delta_hat)} a favor de los varones cis, con un intervalo de confianza '
        f'del 95 % de [{fmt_ars(ic_w_low)} ,  {fmt_ars(ic_w_high)}]. Un test t de Welch (ν = {r["nu_welch"]:.0f})\n'
        f'arroja un p-valor bilateral de {p_val:.2e} y un tamaño del efecto Cohen\'s d = {d:.3f}. '
        f'Bajo los supuestos y el filtrado declarados, los datos son incompatibles con la\n'
        f'hipótesis de igualdad de medias al nivel α = 0,05.'
    )
    ax_header.text(
        0, 0.52, resumen_texto,
        fontsize=9.5, color=COLOR_TEXTO, family='serif',
        va='top',
    )

    # --------------- Figura principal: forest plot ---------------
    ax_fig = fig.add_subplot(gs[18:42, 0])
    metodos = ['Welch paramétrico\n(t, varianzas desiguales)',
               'Bootstrap percentil\n(10 000 resamples)']
    centros = [delta_hat / 1e6, (r['ic_boot'][0] + r['ic_boot'][1]) / 2 / 1e6]
    ics_low = [ic_w_low / 1e6, r['ic_boot'][0] / 1e6]
    ics_high = [ic_w_high / 1e6, r['ic_boot'][1] / 1e6]
    colores = [COLOR_A, '#8FB39E']
    y_pos = [1.0, 0.4]
    ax_fig.axvline(0, color=COLOR_REF, linestyle=':', linewidth=1.3,
                   label='H₀: Δ = 0')
    for y, c, lo, hi, col in zip(y_pos, centros, ics_low, ics_high, colores):
        ax_fig.errorbar(
            c, y, xerr=[[c - lo], [hi - c]],
            fmt='D', markersize=9, color=col, ecolor=col,
            elinewidth=2.4, capsize=6, capthick=1.8,
        )
        ax_fig.text(
            hi + (hi - lo) * 0.15, y,
            f'[{lo:.3f} ,  {hi:.3f}] M',
            va='center', fontsize=9, color=COLOR_TEXTO, family='serif',
        )
    ax_fig.set_yticks(y_pos)
    ax_fig.set_yticklabels(metodos, fontsize=9, family='serif')
    ax_fig.set_xlabel('Δ̂ = μ_A − μ_B  (millones de ARS)',
                      fontsize=10, family='serif')
    ax_fig.set_title(
        'Figura 1. Estimación puntual e intervalo de confianza del 95 % '
        'para la diferencia de medias',
        fontsize=10, pad=10, loc='left', family='serif',
        fontweight='bold',
    )
    ax_fig.set_ylim(0.0, 1.45)
    ax_fig.legend(loc='upper right', fontsize=8, frameon=True,
                  facecolor='white', edgecolor='#E6E8EF')
    for s in ('top', 'right'):
        ax_fig.spines[s].set_visible(False)
    ax_fig.grid(axis='x', color='#E6E8EF', linewidth=0.6)

    # --------------- Tabla técnica ---------------
    ax_tabla = fig.add_subplot(gs[45:68, 0])
    ax_tabla.axis('off')
    ax_tabla.text(
        0, 1.0,
        'Tabla 1. Resultados técnicos del contraste de medias',
        fontsize=10, fontweight='bold', family='serif', color=COLOR_TEXTO,
        transform=ax_tabla.transAxes,
    )

    filas_tabla = [
        ('Tamaño muestral group A (Varón cis) · group B (Mujer cis)',
         f'n_A = {nA}   ·   n_B = {nB}'),
        ('Media muestral por grupo',
         f'{fmt_ars(r["mediaA"])}   ·   {fmt_ars(r["mediaB"])}'),
        ('Desvío estándar muestral por grupo',
         f'{fmt_ars(r["sA"])}   ·   {fmt_ars(r["sB"])}'),
        ('Estimador puntual  Δ̂ = x̄_A − x̄_B',
         fmt_ars(r['delta_hat'])),
        ('IC 95 % (Welch, ν de Satterthwaite)',
         f'[{fmt_ars(ic_w_low)} ,  {fmt_ars(ic_w_high)}]'),
        ('IC 95 % (Bootstrap percentil, 10 000 resamples)',
         f'[{fmt_ars(r["ic_boot"][0])} ,  {fmt_ars(r["ic_boot"][1])}]'),
        ('Test de Welch: estadístico t  ·  ν',
         f'{r["t_stat"]:.3f}   ·   {r["nu_welch"]:.1f}'),
        ('P-valor bilateral (Welch)',
         f'{p_val:.2e}'),
        ('P-valor Mann-Whitney U (robustez no paramétrica)',
         f'{r["p_mwu"]:.2e}'),
        ("Effect size (Cohen's d con SD pooled)",
         f'{d:.3f}'),
        ('Potencia observada (1 − β) al α = 0,05',
         f'{r["power_obs"]:.4f}'),
        ('Decisión del test bilateral al α = 0,05',
         'se rechaza H₀: μ_A = μ_B'),
    ]

    y_top = 0.92
    y_step = 0.072
    for i, (etiqueta, valor) in enumerate(filas_tabla):
        y = y_top - i * y_step
        ax_tabla.text(
            0.0, y, etiqueta,
            fontsize=8.3, family='serif', color=COLOR_TEXTO,
            transform=ax_tabla.transAxes,
        )
        ax_tabla.text(
            0.62, y, valor,
            fontsize=8.3, family='serif', color=COLOR_TEXTO,
            transform=ax_tabla.transAxes, fontweight='bold',
        )

    # --------------- Limitaciones ---------------
    ax_lim = fig.add_subplot(gs[71:90, 0])
    ax_lim.axis('off')
    ax_lim.text(
        0, 1.0,
        'Limitaciones del análisis',
        fontsize=10, fontweight='bold', family='serif', color=COLOR_TEXTO,
        transform=ax_lim.transAxes,
    )
    limitaciones = [
        ('1.',
         'Análisis bivariado. Sólo se contrasta el sueldo por género; no se '
         'controla por años de experiencia, seniority, rol, sector ni '
         'provincia. Parte de la diferencia observada puede deberse a la '
         'distribución diferencial de estos factores entre grupos.'),
        ('2.',
         'Sesgo de autoselección. La encuesta Sysarmy es voluntaria: la '
         'muestra no es aleatoria respecto de la población de trabajadores '
         'del rubro. Las inferencias describen el subconjunto que respondió, '
         'no la población completa.'),
        ('3.',
         'Filtros declarados. Se aplicó un piso de $ 300.000 ARS (SMVM 2026) '
         'y un techo simétrico de $ 15.000.000 ARS sobre ambos grupos para '
         'eliminar valores implausibles sin introducir recortes asimétricos '
         'que contaminen la diferencia de medias.'),
        ('4.',
         'Implicancia legal. El resultado presentado describe una asociación '
         'en la muestra; no establece causalidad por género. No debe usarse '
         'de manera aislada como prueba en un proceso de discriminación '
         'salarial: hace falta un análisis multivariado y un marco '
         'metodológico formal con control de error tipo I.'),
    ]
    y_top_lim = 0.87
    y_step_lim = 0.19
    for i, (n_, txt) in enumerate(limitaciones):
        y = y_top_lim - i * y_step_lim
        ax_lim.text(
            0.0, y, n_,
            fontsize=8.2, family='serif', color=COLOR_REF,
            fontweight='bold',
            transform=ax_lim.transAxes,
        )
        ax_lim.text(
            0.04, y, txt,
            fontsize=8.2, family='serif', color=COLOR_TEXTO,
            transform=ax_lim.transAxes, wrap=True,
        )

    # --------------- Pie: oración con énfasis ---------------
    ax_foot = fig.add_subplot(gs[92:100, 0])
    ax_foot.axis('off')
    ax_foot.axhline(0.9, color='#C5CEDF', linewidth=0.6)
    enfasis = (
        'En la muestra analizada, el sueldo NETO mensual medio de los varones cis '
        'supera en $ 647.000 al de las mujeres cis (IC 95 % $ 517.000 – $ 777.000). '
        'La magnitud del efecto (Cohen\'s d = 0,32) es compatible con una brecha '
        'moderada y robusta al método de estimación empleado.'
    )
    ax_foot.text(
        0.5, 0.45, enfasis,
        fontsize=9.5, style='italic', color=COLOR_TEXTO, family='serif',
        ha='center', va='center', wrap=True,
        transform=ax_foot.transAxes,
    )

    fig.savefig(PDF_PATH, format='pdf', bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    print(f'✅ PDF generado: {PDF_PATH}')
    print(f'   tamaño:     {PDF_PATH.stat().st_size / 1024:.1f} KB')


def main() -> None:
    resultados = cargar_resultados()
    construir_pdf(resultados)


if __name__ == '__main__':
    main()
