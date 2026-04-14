# 📝 Entregable AyVD — Parte 1

**Materia:** Análisis y Visualización de Datos 2026
**Alumno:** Rubén Rasi · **Grupo 21**
**Docente de seguimiento:** Fredy Alexander Restrepo Blandon

> **🟢 Estado: Entregado.** Trabajo grupal finalizado y enviado al aula virtual. Esta carpeta contiene tanto los archivos oficiales del **Grupo 21** como los anexos personales de trabajo previo (informe HTML, notebook con respuestas integradas, apéndice ejecutable y 12 gráficos en matplotlib/seaborn).

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
- **Filtrado progresivo en cinco etapas (F1 a F5)** declarando motivo y N resultante en cada paso:
  - **F1** — descarte de filas sin lenguaje declarado o sin sueldo NETO.
  - **F2** — retención exclusiva de jornadas Full-Time.
  - **F3** — retención de contratos con ingreso en forma de sueldo mensual (Staff, Contractor, Tercerizado); descarte de Freelance y Cooperativa.
  - **F4** — descarte de valores atípicos con la regla de Tukey 1,5·IQR aplicada de forma estratificada por grupo de moneda (ARS, USD parcial, USD total).
  - **F5** — piso de sueldo implausible: se descartan los sueldos mensuales NETO inferiores a 300.000 ARS (orden del SMVM argentino). Este piso captura valores que el F4 no elimina porque el límite inferior Q1 − 1,5·IQR del grupo ARS puede caer en valores negativos.
- Desanidado de la lista de lenguajes para pasar del formato "una fila por persona" al formato "una fila por (persona, lenguaje)".
- Umbral de frecuencia mínima (`n ≥ 30`) declarado como **exclusión de visualización** (no filtro de datos), con justificación basada en la estabilidad de los cuartiles.
- **Opción metodológica adoptada:** combinación de las opciones **A (visualizaciones)** y **B (estadística descriptiva)**, declarada explícitamente en la sección 1.0 del informe.
- **Criterio del coeficiente de variación robusto** (`CV = IQR / mediana`) con umbral derivado de la regla de Tukey 1,5·IQR aplicada sobre la distribución de CV del propio conjunto de lenguajes del ranking. Ambos elementos —CV y regla 1,5·IQR— son citables directamente de la filmina de clase 02.
- **Valores literales del dataset preservados:** los valores crudos de `salary_in_usd` no se parafrasean; se usan las cadenas literales del formulario y el `NaN` se interpreta como "cobro en pesos" apoyándose en la columna booleana `sueldo_dolarizado` del propio dataset.
- **Gráfico G2** rediseñado como visualización compuesta con tres capas que coexisten: violín (densidad KDE), boxplot con relleno transparente y borde en gris pizarra, y todos los puntos individuales con jitter vertical en tonalidad oscura contrastante.
- **Kurtosis del sueldo NETO por filtro**: el log de filtrado progresivo (F1–F5) incluye la kurtosis de Fisher del sueldo NETO luego de cada filtro, para mostrar cuantitativamente que ningún filtro distorsiona significativamente la forma de la distribución (más allá del recorte de colas pesadas que el propio filtro se propone realizar).
- **Análisis complementario (1.6.e + G4b)**: sueldo NETO vs cantidad de lenguajes declarados por respondente (nivel persona, sobre el mismo `df` filtrado). Se reporta la correlación muestral Pearson/Spearman y se grafica la distribución por cada valor del conteo con al menos 15 observaciones. En esta muestra, la asociación aparenta ser débil: saber más lenguajes no se traduce linealmente en un sueldo mayor.

### Ejercicio 2 — Densidades y varias variables

**Pregunta general:** ¿Qué herramientas (prácticas y teóricas) son útiles para explorar la base, descubrir patrones y asociaciones?

Esta pregunta se responde de forma sintética al final del ejercicio, como conclusión de cierre que integra las herramientas utilizadas en cada uno de los sub-ejercicios siguientes.

- **2.0.1) Filtro local de edad biológica:** antes de iniciar los análisis del ejercicio 2, se aplica un filtro **local** a `profile_age` restringiendo al tramo laboralmente plausible `[15, 80]` años. Este filtro NO se propaga al ejercicio 1 (el ranking de lenguajes ya fue calculado sobre el `df` completo) y se declara explícitamente en una sección propia con el N antes/después y ejemplos de los valores descartados (p. ej. `999`).
- **2a) Densidad conjunta:** 3 variables numéricas (`salary_monthly_NETO`, `profile_years_experience`, `profile_age`) y 2 categóricas (`work_seniority`, `profile_gender`) computadas sobre `df_ej2` (filtro de edad local). Se incluyen histogramas marginales con el rango de edad acotado al tramo laboralmente plausible `[15, 80]` años, matriz de correlación de Pearson (coherente con la clase 03) con el eje Y invertido para que la diagonal de 1 quede ascendente, y distribución de las categóricas mostrando los tres grupos analíticos de género.
- **2b) Asociación Bruto ↔ Neto:** correlaciones muestrales de Pearson y Spearman, regresión lineal ajustada, columna derivada `DESCUENTOS = BRUTO − NETO` (técnica del práctico de la clase 03) y respuesta explícita a la pregunta sobre la posible remoción de la columna BRUTO del formulario. Se declaran las observaciones válidas (filtros F1-F5 más no-NaN y valores estrictamente positivos en ambas columnas).
- **2c) Densidad condicional:** selección de las dos subpoblaciones más numerosas con nivel de estudio declarado (`Universitario` y `Terciario`), histogramas comparativos, medidas de centralización y dispersión por subpoblación, y análisis de independencia vía `P(A|B)` versus `P(A)` según el marco descriptivo de la clase 01.
- **2d) Densidad conjunta condicional:** `profile_years_experience` vs `salary_monthly_NETO` con hue = `work_seniority` (G10) y hue = grupo de género (G11). El análisis por género se hace sobre **tres grupos analíticos**: `Hombre Cis`, `Mujer Cis` y `Diversidades` (agrupación respetuosa de las identidades minoritarias del formulario —No binarie, Trans, Queer, Agénero, Prefiero no decir— que individualmente tienen baja cobertura muestral). La agrupación "Diversidades" sigue la terminología empleada en la filmina de clase 03. G10 incorpora una línea negra que conecta la mediana del sueldo por cada año entero de experiencia (tendencia central descriptiva).

**Conclusión de cierre del ejercicio 2:** como último punto de las conclusiones, se responde explícitamente la pregunta general del ejercicio, integrando las herramientas usadas en los cuatro sub-ejercicios (histogramas, diagramas de caja, correlaciones, columnas derivadas, tablas de contingencia, probabilidades condicionales, scatterplots con hue).

Todas las conclusiones se redactan en términos descriptivos *"en esta muestra"*, *"se observa"*, *"sugiere"*, sin emplear herramientas inferenciales de la parte 2 del entregable (intervalos de confianza, tests de hipótesis, p-valores).

---

## 🚦 Archivos entregados oficialmente — Grupo 21

Estos son los dos archivos que el **Grupo 21** envió al aula virtual de la materia. **Son la versión oficial entregada al docente** y los que cuentan a efectos de evaluación.

| Archivo | Tipo | Descripción |
|---|---|---|
| 📄 [`Entregable_1_grupo_21.pdf`](Entregable_1_grupo_21.pdf) | PDF (≈ 15 MB) | Informe completo del entregable parte 1 con todas las visualizaciones y conclusiones del grupo |
| 🐍 [`entregable_parte_1_ayvd_g21.py`](entregable_parte_1_ayvd_g21.py) | Python (export Colab → .py) | Notebook del trabajo grupal exportado a script ejecutable. Contiene el código completo que produjo el informe |

> **Cómo abrir el `.py` como notebook:** el archivo es un export de un Colab y mantiene los marcadores `# %%` de celdas. Se puede abrir tal cual en VS Code (con el plugin Jupyter) o convertir a `.ipynb` con `jupytext --to ipynb entregable_parte_1_ayvd_g21.py`.

---

## 🗂️ Anexos personales — Rubén Rasi

Trabajo previo, individual y exhaustivo realizado durante la cursada. **No forma parte de la entrega oficial al aula virtual**, pero queda preservado en el repo como referencia técnica y metodológica. Es el material que más profundamente desarrolla la consigna y que sirvió de insumo para el trabajo grupal final.

Estos anexos son **el principal atractivo técnico del repositorio** y representan el grueso del trabajo invertido en la cursada.

| Archivo / carpeta | Tipo | Qué aporta |
|---|---|---|
| 📓 [`entregable_ayvd_parte1.ipynb`](entregable_ayvd_parte1.ipynb) | Notebook Jupyter | Consigna oficial del curso intacta + celdas de respuesta integradas después de cada ejercicio, con los gráficos embebidos desde `datos_parte1_img/`. Pensado como soporte de revisión académica. |
| 🌐 [`entregable_ayvd_parte1.html`](entregable_ayvd_parte1.html) | HTML autocontenido (≈ 800 KB) | Informe interactivo con 12 gráficos en **Plotly** (hover, zoom, desplazamiento), fórmulas matemáticas renderizadas con **KaTeX** y narrativa completa. Requiere conexión a internet para la primera visualización (CDN de Plotly y KaTeX). |
| 🐍 [`datos_parte1.py`](datos_parte1.py) | Script ejecutable | **Apéndice ejecutable de datos**: imprime por consola los 46 cuadros intermedios (filtros, estadísticos, tablas) que sustentan cada afirmación del informe, y regenera los 12 gráficos equivalentes en `matplotlib` + `seaborn`. Soporta `--csv` para exportar cada cuadro a su archivo CSV. |
| 🖼️ [`datos_parte1_img/`](datos_parte1_img/) | 12 PNGs | Versión estática de los gráficos del informe (G1–G11 + G4b), generados con las librerías vistas en clase. |

### Estructura de archivos completa

```
parte1/
├── README.md                               ← Este archivo
├── consigna_parte1.ipynb                   ← Consigna oficial del curso (intacta)
│
├── 🚦 ENTREGADOS AL AULA VIRTUAL (Grupo 21)
├── Entregable_1_grupo_21.pdf               ← PDF entregado oficialmente (15 MB)
├── entregable_parte_1_ayvd_g21.py          ← Script entregado oficialmente (export Colab)
│
├── 🗂️ ANEXOS PERSONALES — Rubén Rasi
├── entregable_ayvd_parte1.ipynb            ← Notebook con respuestas integradas
├── entregable_ayvd_parte1.html             ← Informe HTML interactivo (Plotly + KaTeX)
├── datos_parte1.py                         ← Apéndice ejecutable de datos
├── datos_parte1_img/                       ← 12 gráficos matplotlib/seaborn
│   ├── G1_ranking_mediana.png               ← ranking de lenguajes por mediana
│   ├── G2_violin_lenguajes.png              ← violin + box transparente + puntos
│   ├── G3_mediana_por_moneda.png            ← mediana por lenguaje y moneda
│   ├── G4_frecuencia_vs_mediana.png         ← bubble: frecuencia vs mediana
│   ├── G4b_sueldo_vs_n_lenguajes.png        ← sueldo NETO vs cantidad de lenguajes
│   ├── G5_histogramas_numericas.png         ← histogramas de las 3 numéricas
│   ├── G6_matriz_correlacion.png            ← heatmap de correlación Pearson
│   ├── G7_categoricas.png                   ← barras de seniority y género
│   ├── G8_bruto_vs_neto.png                 ← scatter BRUTO vs NETO + regresión
│   ├── G9_histogramas_subpob_estudios.png   ← histogramas comparativos 2c
│   ├── G10_exp_sueldo_seniority.png         ← exp vs sueldo + hue seniority
│   └── G11_exp_sueldo_genero.png            ← exp vs sueldo + hue grupo género
│
└── data/
    └── sysarmy_survey_2026_processed.csv   ← Dataset de entrada
```

---

## 🚀 Cómo revisar el entregable

### Opción 0 — Lectura directa del entregado oficial *(la que vio el docente)*

Abrir **`Entregable_1_grupo_21.pdf`** con cualquier lector de PDF. Es el material que el **Grupo 21** subió al aula virtual de FAMAF y el que cuenta a efectos de evaluación.

Para revisar el código que produjo ese informe, abrir **`entregable_parte_1_ayvd_g21.py`** (es un export de Colab a script Python con marcadores de celda `# %%`).

### Opción 1 — Notebook personal con respuestas integradas *(anexo)*

Abrir **`entregable_ayvd_parte1.ipynb`** en Jupyter, VS Code o Google Colab. El notebook se construye sobre la consigna oficial del curso (celdas originales intactas) e intercala después de cada ejercicio una celda de respuesta con los hallazgos clave y los gráficos correspondientes embebidos desde `datos_parte1_img/`. Desde ese mismo notebook se enlaza al informe HTML y al apéndice `datos_parte1.py` para el desarrollo completo.

### Opción 2 — Informe HTML interactivo *(anexo)*

Abrir **`entregable_ayvd_parte1.html`** en cualquier navegador moderno. El informe es autocontenido: los gráficos interactivos de Plotly se cargan desde CDN, por lo que se requiere conexión a internet para la primera visualización.

### Opción 3 — Cotejar los datos por consola *(anexo)*

El archivo **`datos_parte1.py`** es el apéndice de datos del informe personal. Imprime por consola los 46 cuadros intermedios (DataFrames, estadísticos, valores derivados) que sustentan cada afirmación del HTML, y regenera los 12 gráficos equivalentes con matplotlib/seaborn (las librerías vistas en clase).

```bash
# Desde esta carpeta (entregables/parte1/)
python datos_parte1.py
```

Para exportar todos los cuadros como CSV adicionalmente:

```bash
python datos_parte1.py --csv
# → crea datos_parte1_csv/ con un CSV por cuadro
```

### Opción 4 — Revisión cruzada HTML ↔ código *(anexo)*

Cada estadístico, gráfico o cuadro que aparece en el HTML se puede rastrear hasta su cálculo en `datos_parte1.py`. El archivo está organizado con los mismos identificadores de sección que el informe (1.0, 1.1, ..., 2.a, 2.b, 2.c, 2.d), lo que facilita el cotejo línea por línea.

---

## 🛠️ Stack técnico

| Uso | Librería |
|---|---|
| Manipulación de datos | `pandas`, `numpy` |
| Gráficos del informe HTML personal | `plotly` |
| Gráficos equivalentes estáticos | `matplotlib`, `seaborn` |

Dependencias: `pandas`, `numpy`, `plotly`, `matplotlib`, `seaborn`.

---

## 🔗 Material de referencia utilizado

| Fuente | Uso |
|---|---|
| **Clase 01 — Probabilidad** | Independencia y probabilidad condicional `P(A\|B)` (aplicado en 2c); filmina mirror local en `_site/filminas/clase1_probabilidad_y_estadistica.pdf` |
| **Clase 02 — Datos y Modelos** | Medidas de tendencia central, dispersión, IQR, boxplots, eliminación de atípicos por la regla de Tukey 1,5·IQR, coeficiente de variación; filmina mirror local en `_site/filminas/clase2_datos_y_modelos.pdf` |
| **Clase 03 — Varias Variables** | Histogramas, `crosstab`, histogramas superpuestos para subpoblaciones, `np.corrcoef` (Pearson), Spearman como alternativa para distribuciones no normales, columna derivada `DESCUENTOS`; filmina mirror local en `_site/filminas/clase2_varias_variables.pdf` |
| **Consigna oficial** | `consigna_parte1.ipynb` |

Todas las filminas del curso tienen un mirror local en `_site/filminas/` tanto en PDF como en TXT (para búsqueda rápida por texto).
