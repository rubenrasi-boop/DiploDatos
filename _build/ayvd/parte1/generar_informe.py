#!/usr/bin/env python3
"""
Entregable AyVD Parte 1 — Generador de informe HTML/PDF
Diplomatura en Ciencia de Datos 2026 — FAMAF, UNC

Alumno: Rubén Rasi
Docente de seguimiento: Fredy Alexander Restrepo Blandon

Objetivos:
  - Describir y analizar la base desde varios ángulos
  - Múltiples variables, visualmente y con medidas descriptivas
  - Observar relaciones
  - Plantear preguntas, hipótesis y diseñar un abordaje

Ejercicios:
  1. Análisis descriptivo: ¿Cuáles son los lenguajes de programación asociados
     a los mejores salarios?
  2a. Densidad conjunta (3 numéricas + 2 categóricas)
  2b. Asociación: correlación Bruto vs Neto
  2c. Densidad condicional: salario según nivel de estudio
  2d. Densidad conjunta condicional: scatterplot con hue

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
    'AnalisisyVisualizacion', 'entregables', 'parte1'
)
OUTPUT_HTML = os.path.join(ENTREGABLES_DIR, 'entregable_ayvd_parte1.html')
OUTPUT_PDF = os.path.join(ENTREGABLES_DIR, 'entregable_ayvd_parte1.pdf')

# ============================================================
# CARGA DE DATOS
# ============================================================

# TODO: implementar


# ============================================================
# EJERCICIO 1 — Análisis descriptivo: Lenguajes y salarios
# ============================================================

# 1.1 Selección de columnas relevantes
# TODO: implementar

# 1.2 Selección y limpieza de filas
# TODO: implementar

# 1.3 Conteo de frecuencias de lenguajes
# TODO: implementar

# 1.4 Filtrado de lenguajes relevantes
# TODO: implementar

# 1.5 Métricas y análisis
# TODO: implementar

# 1.6 Conclusiones
# TODO: implementar


# ============================================================
# EJERCICIO 2a — Densidad conjunta
# ============================================================

# TODO: implementar


# ============================================================
# EJERCICIO 2b — Asociación: Bruto vs Neto
# ============================================================

# TODO: implementar


# ============================================================
# EJERCICIO 2c — Densidad condicional: salario según estudio
# ============================================================

# TODO: implementar


# ============================================================
# EJERCICIO 2d — Densidad conjunta condicional (hue)
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
