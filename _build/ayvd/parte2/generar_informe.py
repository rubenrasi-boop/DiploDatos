#!/usr/bin/env python3
"""
Entregable AyVD Parte 2 — Generador de informe HTML/PDF
Diplomatura en Ciencia de Datos 2026 — FAMAF, UNC

Alumno: Rubén Rasi
Docente de seguimiento: Fredy Restrepo Blandón

Objetivos:
  1. Describir y analizar la base desde varios ángulos, múltiples variables,
     visualmente y con medidas descriptivas. Observar relaciones.
     Plantear preguntas, hipótesis y diseñar un abordaje.
  2. Aprender a diferenciar datos de modelos.
  3. Realizar inferencia: estimación y testeo.
  4. Comunicar resultados.

Uso:
  python generar_informe.py            → genera HTML
  python generar_informe.py --pdf      → genera HTML + PDF
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACIÓN
# ============================================================

DATASET_URL = (
    'https://raw.githubusercontent.com/DiploDatos/'
    'AnalisisyVisualizacion/master/sysarmy_survey_2026_processed.csv'
)

ENTREGABLES_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', '..',
    'AnalisisyVisualizacion', 'entregables', 'parte2'
)
OUTPUT_HTML = os.path.join(ENTREGABLES_DIR, 'entregable_ayvd_parte2.html')
OUTPUT_PDF = os.path.join(ENTREGABLES_DIR, 'entregable_ayvd_parte2.pdf')

# ============================================================
# CARGA DE DATOS
# ============================================================

# TODO: implementar


# ============================================================
# OBJETIVO 1 — Análisis descriptivo multivariado
# ============================================================

# TODO: implementar


# ============================================================
# OBJETIVO 2 — Datos vs Modelos
# ============================================================

# TODO: implementar


# ============================================================
# OBJETIVO 3 — Inferencia: estimación y testeo
# ============================================================

# TODO: implementar


# ============================================================
# OBJETIVO 4 — Comunicación de resultados
# ============================================================

# TODO: implementar


# ============================================================
# GENERACIÓN DEL INFORME HTML
# ============================================================

# TODO: implementar


# ============================================================
# GENERACIÓN PDF (opcional)
# ============================================================

if '--pdf' in sys.argv:
    # TODO: implementar (weasyprint o similar)
    pass
