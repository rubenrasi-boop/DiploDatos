# 📝 Entregable AyVD — Parte 1

**Materia:** Análisis y Visualización de Datos 2026
**Alumno:** Rubén Rasi
**Docente de seguimiento:** Fredy Alexander Restrepo Blandon

> **🔍 Estado: en revisión.** El informe principal y el apéndice de datos están completos y son funcionales. Actualmente se están iterando ajustes de redacción, justificaciones metodológicas y consistencia de narrativa antes de considerarlo definitivo para presentación.

---

## 📅 Fechas

| Campo | Detalle |
|-------|---------|
| **Apertura** | Viernes 10/04/2026, 00:00 |
| **Entrega** | Lunes 13/04/2026, 23:59 |
| **Consigna** | [Ver en Google Drive](https://drive.google.com/file/d/1devPC-DscjuaA-5FId39jgDAz6B-Vr03/view?usp=sharing) |

---

## 🎯 Objetivos

Describir y analizar la base desde "varios ángulos", con varias variables, visualmente y a través de medidas descriptivas. Observar relaciones. Plantear preguntas, hipótesis y diseñar un abordaje.

---

## 📋 Ejercicios resueltos

### Ejercicio 1 — Análisis descriptivo

**Pregunta:** ¿Cuáles son los lenguajes de programación asociados a los mejores salarios?

- Selección de columnas relevantes.
- Selección de filas con filtrado progresivo (F1 a F4) declarando motivo y N resultante de cada paso.
- Desanidado de la lista de lenguajes.
- Umbral de frecuencia mínima declarado como exclusión de visualización (no filtro de datos).
- **Opción metodológica adoptada:** combinación de las opciones **A (visualizaciones)** y **B (estadística descriptiva)** de la consigna, declarada explícitamente en la sección 1.0 del informe.
- Criterio de dispersión relativa de la mediana derivado de los datos (sin umbrales arbitrarios).

### Ejercicio 2 — Densidades y varias variables

**Pregunta general:** ¿Qué herramientas (prácticas y teóricas) son útiles para explorar la base, descubrir patrones y asociaciones?

Esta pregunta se responde de forma sintética al final del ejercicio, como conclusión de cierre que integra las herramientas utilizadas en cada uno de los sub-ejercicios siguientes.

- **2a) Densidad conjunta:** 3 variables numéricas (`salary_monthly_NETO`, `profile_years_experience`, `profile_age`) y 2 categóricas (`work_seniority`, `profile_gender`). Se incluyen histogramas marginales, matriz de correlación de Pearson (coherente con la clase 03) y distribución de las categóricas.
- **2b) Asociación Bruto ↔ Neto:** correlaciones muestrales de Pearson y Spearman, regresión lineal ajustada, columna derivada `DESCUENTOS = BRUTO − NETO` (técnica del práctico de la clase 03) y respuesta explícita a la pregunta implícita *"¿conviene quitar BRUTO del formulario?"*.
- **2c) Densidad condicional:** selección de las dos subpoblaciones más numerosas con nivel de estudio declarado (`Universitario` y `Terciario`), histogramas comparativos, medidas de centralización y dispersión por subpoblación, y análisis de independencia vía `P(A|B)` versus `P(A)` según el marco de la clase 01.
- **2d) Densidad conjunta condicional:** `profile_years_experience` vs `salary_monthly_NETO` con hue = `work_seniority`. Se incluye un análisis extendido con hue = `profile_gender` restringido a las dos categorías con mayor cobertura muestral, declarado explícitamente como extensión más allá del mínimo solicitado.

Todas las conclusiones se redactan en términos descriptivos *"en esta muestra"*, *"se observa"*, *"sugiere"*, sin emplear herramientas inferenciales de la parte 2 del entregable (intervalos de confianza, tests de hipótesis, p-valores).

---

## 📂 Archivos del entregable

```
parte1/
├── README.md                               ← Este archivo
├── consigna_parte1.ipynb                   ← Consigna oficial del curso
│
├── entregable_ayvd_parte1.html             ← 📄 INFORME PRINCIPAL
│
├── datos_parte1.py                         ← 📄 Apéndice ejecutable de datos
│
├── datos_parte1_img/                       ← Gráficos equivalentes en
│   │                                          matplotlib/seaborn (clase 02/03)
│   ├── G1_ranking_mediana.png
│   ├── G2_boxplot_lenguajes.png
│   ├── G3_mediana_por_moneda.png
│   ├── G4_frecuencia_vs_mediana.png
│   ├── G5_histogramas_numericas.png
│   ├── G6_matriz_correlacion.png
│   ├── G7_categoricas.png
│   ├── G8_bruto_vs_neto.png
│   ├── G9_histogramas_subpob_estudios.png
│   ├── G10_exp_sueldo_seniority.png
│   └── G11_exp_sueldo_genero.png
│
└── data/
    └── sysarmy_survey_2026_processed.csv   ← Dataset de entrada
```

---

## 🚀 Cómo revisar el entregable

### Opción 1 — Lectura directa (recomendada)

Abrir **`entregable_ayvd_parte1.html`** en cualquier navegador moderno. El informe es autocontenido: los gráficos interactivos de Plotly se cargan desde CDN, por lo que se requiere conexión a internet para la primera visualización.

### Opción 2 — Cotejar los datos por consola

El archivo **`datos_parte1.py`** es el apéndice de datos del informe. Imprime por consola los 44 cuadros intermedios (DataFrames, estadísticos, valores derivados) que sustentan cada afirmación del HTML, y regenera los 11 gráficos equivalentes con matplotlib/seaborn (las librerías vistas en clase).

```bash
# Desde esta carpeta (entregables/parte1/)
python datos_parte1.py
```

Para exportar todos los cuadros como CSV adicionalmente:

```bash
python datos_parte1.py --csv
# → crea datos_parte1_csv/ con un CSV por cuadro
```

### Opción 3 — Revisión cruzada HTML ↔ código

Cada estadístico, gráfico o cuadro que aparece en el HTML se puede rastrear hasta su cálculo en `datos_parte1.py`. El archivo está organizado con los mismos identificadores de sección que el informe (1.0, 1.1, ..., 2.a, 2.b, 2.c, 2.d), lo que facilita el cotejo línea por línea.

---

## 🛠️ Stack técnico

| Uso | Librería |
|---|---|
| Manipulación de datos | `pandas`, `numpy` |
| Gráficos del informe HTML | `plotly` |
| Gráficos equivalentes estáticos | `matplotlib`, `seaborn` |

Dependencias: `pandas`, `numpy`, `plotly`, `matplotlib`, `seaborn`.

---

## 🔗 Material de referencia utilizado

| Fuente | Uso |
|---|---|
| **Clase 01 — Probabilidad** | Independencia y probabilidad condicional `P(A\|B)` (aplicado en 2c) |
| **Clase 02 — Datos y Modelos** | Medidas de tendencia central, dispersión, IQR, boxplots, eliminación de atípicos por IQR |
| **Clase 03 — Varias Variables** | Histogramas, `crosstab`, histogramas superpuestos para subpoblaciones, `np.corrcoef` (Pearson), columna derivada `DESCUENTOS` |
| **Consigna oficial** | `consigna_parte1.ipynb` |
