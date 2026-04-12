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
| **Clase 01 — Probabilidad** | Independencia y probabilidad condicional `P(A\|B)` (aplicado en 2c); filmina mirror local en `_site/filminas/clase1_probabilidad_y_estadistica.pdf` |
| **Clase 02 — Datos y Modelos** | Medidas de tendencia central, dispersión, IQR, boxplots, eliminación de atípicos por la regla de Tukey 1,5·IQR, coeficiente de variación; filmina mirror local en `_site/filminas/clase2_datos_y_modelos.pdf` |
| **Clase 03 — Varias Variables** | Histogramas, `crosstab`, histogramas superpuestos para subpoblaciones, `np.corrcoef` (Pearson), Spearman como alternativa para distribuciones no normales, columna derivada `DESCUENTOS`; filmina mirror local en `_site/filminas/clase2_varias_variables.pdf` |
| **Consigna oficial** | `consigna_parte1.ipynb` |

Todas las filminas del curso tienen un mirror local en `_site/filminas/` tanto en PDF como en TXT (para búsqueda rápida por texto).
