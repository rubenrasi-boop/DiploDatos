#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma el notebook entregable de la Parte 1 partiendo de la consigna
oficial del curso (consigna_parte1.ipynb) e insertando, después de
cada celda de consigna, una celda de respuesta breve que referencia
al informe HTML y al apéndice datos_parte1.py (donde está todo el
desarrollo completo).

El objetivo es que el notebook mantenga la estructura original del
curso (consigna intacta, celdas de ayuda conservadas) y sumar por
encima celdas de respuesta compactas con los hallazgos clave y las
referencias visuales (PNG del directorio datos_parte1_img/).

Salida:
    AnalisisyVisualizacion/entregables/parte1/entregable_ayvd_parte1.ipynb
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CONSIGNA = REPO / 'AnalisisyVisualizacion/entregables/parte1/consigna_parte1.ipynb'
DESTINO = REPO / 'AnalisisyVisualizacion/entregables/parte1/entregable_ayvd_parte1.ipynb'


def md(texto: str) -> dict:
    """Construye una celda markdown nbformat v4."""
    lineas = texto.splitlines(keepends=True)
    # Asegurar que cada línea termine en '\n' salvo la última
    if lineas and not lineas[-1].endswith('\n'):
        lineas[-1] = lineas[-1] + '\n'
    return {
        'cell_type': 'markdown',
        'metadata': {},
        'source': lineas,
    }


# ---------------------------------------------------------------
# Celdas de respuesta (breves, reutilizan el vocabulario del informe)
# ---------------------------------------------------------------

PORTADA = md("""\
---

## 📝 Entregable Parte 1 — Rubén Rasi

> **Estado:** 🟢 **Finalizado parcial** — el desarrollo, los datos y los \
gráficos no se modifican. Queda abierta únicamente la iteración de \
redacción y consistencia narrativa.

**Docente de seguimiento:** Fredy Alexander Restrepo Blandon

Este notebook es el entregable de la Parte 1. Se construyó sobre la \
consigna oficial del curso: las celdas originales se conservan \
intactas y se añaden a continuación celdas de respuesta breves que \
remiten al desarrollo completo.

**Materiales que acompañan este notebook:**

| Archivo | Contenido |
|---|---|
| [`entregable_ayvd_parte1.html`](entregable_ayvd_parte1.html) | 📄 Informe principal con gráficos interactivos Plotly y narrativa completa |
| [`datos_parte1.py`](datos_parte1.py) | 🐍 Apéndice ejecutable: imprime por consola los 46 cuadros intermedios (filtros, estadísticos, tablas) y regenera los 12 gráficos equivalentes en matplotlib/seaborn |
| [`datos_parte1_img/`](datos_parte1_img/) | 🖼️ Los 12 gráficos G1–G11 (+ G4b) en PNG, referenciados desde este notebook |
| [`README.md`](README.md) | 📋 Índice del entregable y decisiones metodológicas |

Para reproducir los cuadros por consola:

```bash
python datos_parte1.py          # imprime todos los cuadros
python datos_parte1.py --csv    # además exporta cada cuadro a CSV
```

---
""")


RESP_EJ1 = md("""\
---

### ✅ Respuesta al Ejercicio 1

**Enfoque adoptado:** combinación de las opciones *A (visualizaciones)* \
y *B (estadística descriptiva)*, declarada explícitamente en la \
sección 1.0 del informe HTML.

#### 🧹 Filtrado progresivo (F1 → F5)

| Filtro | Motivo | Criterio |
|---|---|---|
| **F1** | Descarte de filas sin lenguaje declarado o sin sueldo NETO | `notna()` |
| **F2** | Retención exclusiva de jornadas Full-Time | `work_dedication == 'Full-Time'` |
| **F3** | Retención de contratos con ingreso en forma de sueldo mensual | Staff, Contractor, Tercerizado (descarta Freelance y Cooperativa) |
| **F4** | Descarte de valores atípicos con regla de Tukey 1,5·IQR **estratificada** por grupo de moneda | ARS, USD parcial, USD total |
| **F5** | Piso de sueldo implausible (orden del SMVM argentino) | `salary_monthly_NETO ≥ 300 000 ARS` |

La kurtosis de Fisher del sueldo NETO se reporta en cada paso para \
evidenciar que ningún filtro distorsiona significativamente la forma \
de la distribución más allá del recorte de colas pesadas que el \
propio filtro se propone realizar.

#### 📊 Criterio de dispersión: CV robusto (IQR / mediana)

Sobre el conjunto final de lenguajes del ranking se calcula el \
**coeficiente de variación robusto** \
`CV = IQR / mediana` y se aplica la regla de Tukey 1,5·IQR **sobre la \
distribución de CVs** para marcar los lenguajes que se apartan del \
resto en términos de heterogeneidad salarial. Ambos elementos son \
directamente citables de la filmina de Clase 02.

Se adopta además un umbral de visualización `n ≥ 30` como exclusión de \
visualización (no filtro de datos), justificado por la estabilidad de \
los cuartiles.

#### 🖼️ Resultados visuales

**G1 — Ranking de lenguajes por sueldo NETO mediano**

![G1 — Ranking](datos_parte1_img/G1_ranking_mediana.png)

**G2 — Distribución por lenguaje** *(violín + boxplot transparente + todos los puntos con jitter)*

![G2 — Distribución por lenguaje](datos_parte1_img/G2_violin_lenguajes.png)

**G3 — Mediana por lenguaje y grupo de moneda**

![G3 — Mediana por moneda](datos_parte1_img/G3_mediana_por_moneda.png)

**G4 — Frecuencia vs sueldo mediano** *(tamaño del punto = dispersión IQR)*

![G4 — Frecuencia vs mediana](datos_parte1_img/G4_frecuencia_vs_mediana.png)

#### 🧪 Análisis complementario — sueldo NETO vs cantidad de lenguajes declarados (1.6.e)

A nivel persona se computa la cantidad de lenguajes que declara cada \
respondente y se resume el sueldo NETO para cada valor del conteo. \
En esta muestra la asociación aparenta ser **débil**: saber más \
lenguajes no se traduce linealmente en un sueldo mayor.

![G4b — Sueldo vs cantidad de lenguajes](datos_parte1_img/G4b_sueldo_vs_n_lenguajes.png)

#### 💬 Conclusión

Los valores literales del dataset se preservan: el `NaN` de \
`salary_in_usd` se interpreta como *"cobro en pesos"* apoyándose en la \
columna booleana `sueldo_dolarizado`, y los sueldos se analizan sobre \
la columna unificada `salary_monthly_NETO`. El detalle del ranking, \
las medianas por grupo de moneda y los lenguajes marcados por CV \
robusto están en la sección 1 del informe HTML y en las secciones \
`1.0` a `1.8` del apéndice `datos_parte1.py`.

---
""")


RESP_EJ2_INTRO = md("""\
---

### ✅ Respuesta al Ejercicio 2

El ejercicio 2 se desarrolla sobre el mismo `df` filtrado del ejercicio \
1 (a nivel persona, sin desanidar la lista de lenguajes). Antes de \
computar cualquier estadístico que involucre la edad biológica se \
aplica un **filtro local** `profile_age ∈ [15, 80]` años declarado en \
la sección 2.0.1 del informe; este filtro NO se propaga al ejercicio \
1 y sólo afecta los análisis que usan `profile_age` como variable \
numérica.

Todas las conclusiones se redactan en términos descriptivos *"en esta \
muestra"*, *"se observa"*, *"aparenta"*.

""")


RESP_2A = md("""\
#### 2.a) Densidad conjunta

**Variables seleccionadas:**

| Rol | Variable | Tipo |
|---|---|---|
| Respuesta principal | `salary_monthly_NETO` | numérica |
| Control | `profile_years_experience` | numérica |
| Control | `profile_age` | numérica |
| Factor | `work_seniority` | categórica |
| Factor | `profile_gender` (con agrupación *Diversidades*) | categórica |

**Herramientas usadas:** histogramas marginales, matriz de correlación \
de Pearson (heatmap), descripción por percentiles y tablas de \
frecuencia para las categóricas. La correlación de Spearman se \
reporta como alternativa robusta para distribuciones no normales \
(Clase 02 / Clase 03).

![G5 — Histogramas marginales](datos_parte1_img/G5_histogramas_numericas.png)

![G6 — Matriz de correlación Pearson](datos_parte1_img/G6_matriz_correlacion.png)

![G7 — Distribución de categóricas](datos_parte1_img/G7_categoricas.png)

La agrupación **Diversidades** reúne las identidades minoritarias del \
formulario (*No binarie, Trans, Queer, Agénero, Prefiero no decir*) \
que individualmente tienen baja cobertura muestral; su uso sigue la \
terminología empleada en la filmina de Clase 03 y permite que estén \
presentes en el análisis sin producir medianas inestables por grupo.

""")


RESP_2B = md("""\
#### 2.b) Asociación Bruto ↔ Neto

Se calculan correlaciones muestrales de **Pearson** y **Spearman**, \
se ajusta una **regresión lineal simple** `neto = a · bruto + b` \
(`np.polyfit`) como recurso descriptivo y se construye la columna \
derivada `DESCUENTOS = BRUTO − NETO` siguiendo el práctico de Clase \
03.

![G8 — BRUTO vs NETO](datos_parte1_img/G8_bruto_vs_neto.png)

**Respuesta explícita a la consigna:** en esta muestra, la \
correlación muy alta entre BRUTO y NETO (Pearson ≈ 0,947, Spearman \
≈ 0,954) y la estabilidad del ratio `NETO/BRUTO` sugieren que la \
columna BRUTO es altamente redundante con NETO. A los efectos del \
tipo de análisis realizado, **puede considerarse su remoción del \
formulario** sin pérdida sustancial.

""")


RESP_2C = md("""\
#### 2.c) Densidad condicional — sueldo según nivel de estudio

Se seleccionan las dos subpoblaciones más numerosas con nivel de \
estudio declarado: **Universitario** y **Terciario**. Se comparan \
histogramas, se calculan medidas de centralización y dispersión por \
subpoblación y se evalúa la independencia **chequeando las dos formas \
equivalentes** que da la Clase 01:

$$P(A \\cap B) = P(A)\\,P(B) \\;\\;\\Longleftrightarrow\\;\\; P(A \\mid B) = P(A) \\;\\;\\Longleftrightarrow\\;\\; P(B \\mid A) = P(B)$$

con `A = "sueldo NETO > mediana global"` y `B = "nivel de estudio = X"`.

![G9 — Histogramas comparativos](datos_parte1_img/G9_histogramas_subpob_estudios.png)

**Asimetría numérica de las distancias (masas marginales).** Aunque \
ambas condiciones son matemáticamente equivalentes, las magnitudes \
`|P(A|B) − P(A)|` y `|P(B|A) − P(B)|` **no coinciden**: de la \
identidad exacta

$$P(A\\mid B) - P(A) = \\frac{P(A,B) - P(A)\\,P(B)}{P(B)} \\;\\;,\\;\\; P(B\\mid A) - P(B) = \\frac{P(A,B) - P(A)\\,P(B)}{P(A)}$$

se ve que el numerador es el **mismo** en ambas direcciones (es la \
"sobrerepresentación" de la conjunta respecto del caso independiente), \
pero cada distancia se divide por la **masa marginal** del evento que \
se condiciona. Cuando `P(A)` y `P(B)` son muy distintas, las dos \
distancias se ven numéricamente disímiles aunque reflejen la misma \
asociación subyacente.

**Lectura en esta muestra:** para **Terciario** las dos distancias son \
claramente no nulas, por lo que cualquiera de las dos direcciones \
descarta la independencia. Para **Universitario** las dos son \
pequeñas pero tampoco nulas, de modo que la cercanía a la \
independencia es sólo aproximada. En términos descriptivos, nivel de \
estudio y sueldo **no son independientes** en esta muestra. Sólo el \
35 % de los respondentes del conjunto filtrado declararon su nivel de \
estudio, lo que acota el alcance de la observación.

""")


RESP_2D = md("""\
#### 2.d) Densidad conjunta condicional — experiencia vs sueldo con factor

Se grafica `profile_years_experience` vs `salary_monthly_NETO` \
coloreando por dos factores categóricos distintos: el nivel de \
seniority (G10) y el grupo analítico de género (G11).

![G10 — Experiencia × sueldo × seniority](datos_parte1_img/G10_exp_sueldo_seniority.png)

G10 incorpora una línea gris pizarra que conecta la mediana del \
sueldo por cada año entero de experiencia (tendencia central \
descriptiva). Dentro de cada nivel de seniority la relación \
experiencia ↔ sueldo se mantiene creciente en los datos observados.

![G11 — Experiencia × sueldo × grupo de género](datos_parte1_img/G11_exp_sueldo_genero.png)

Entre los tres grupos analíticos de género se registra, en esta \
muestra, una brecha relativa del **16,8 %** para Mujer Cis respecto \
de Hombre Cis y del **6,4 %** para el grupo Diversidades respecto del \
mismo grupo de referencia.

""")


CIERRE = md("""\
---

### 🧰 Herramientas usadas en el ejercicio 2 — respuesta de cierre

Respondiendo la pregunta general del ejercicio 2 \
(*«¿qué herramientas prácticas y teóricas son útiles para explorar \
la base, descubrir patrones y asociaciones?»*), el desarrollo de los \
cuatro sub-ejercicios muestra un conjunto mínimo y defendible \
compuesto por:

- **Histogramas** y **diagramas de caja** para describir \
distribuciones marginales.
- **Coeficientes de correlación** (Pearson y Spearman) y **matrices \
de correlación** para medir asociaciones entre numéricas.
- **Columnas derivadas** (como `DESCUENTOS = BRUTO − NETO`) para \
caracterizar redundancia entre variables.
- **Tablas de contingencia** para pares categóricos.
- Comparación de **probabilidades marginales y condicionales** \
`P(A)` vs `P(A|B)` para el análisis de independencia.
- **Scatterplots con hue categórico** para la densidad conjunta \
condicional.

Todas son herramientas estrictamente descriptivas y suficientes para \
responder las preguntas planteadas en esta parte del entregable.
""")


# ---------------------------------------------------------------
# Integración
# ---------------------------------------------------------------

def main() -> None:
    nb = json.loads(CONSIGNA.read_text(encoding='utf-8'))
    originales = nb['cells']

    # Mapeo por índice en la consigna original:
    #   0   : título
    #   1-4 : imports, lectura, df[:10]
    #   5   : consigna ej 1      → después insertar PORTADA justo ANTES de 5
    #   6-14: celdas de ayuda (relevant_columns, split_languages, ...)
    #   14  : filtrado demo      → después insertar RESP_EJ1
    #   15  : encabezado ej 2    → después insertar RESP_EJ2_INTRO
    #   16  : consigna 2a        → después RESP_2A
    #   17  : consigna 2b        → después RESP_2B
    #   18  : consigna 2c        → después RESP_2C
    #   19  : consigna 2d        → después RESP_2D  y luego CIERRE
    #
    # Para mantener la consigna intacta, insertamos las respuestas
    # DESPUÉS de las celdas correspondientes.

    nuevos: list[dict] = []
    for i, celda in enumerate(originales):
        celda = copy.deepcopy(celda)
        # Normalizar: el formato que traen algunas celdas de Colab usa
        # outputs y execution_count inexistentes en markdown.
        if celda['cell_type'] == 'markdown':
            celda.pop('execution_count', None)
            celda.pop('outputs', None)
        else:
            celda.setdefault('outputs', [])
            celda.setdefault('execution_count', None)
        # Portada se inserta ANTES del bloque Ejercicio 1 (índice 5)
        if i == 5:
            nuevos.append(PORTADA)
        nuevos.append(celda)
        if i == 14:
            nuevos.append(RESP_EJ1)
        elif i == 15:
            nuevos.append(RESP_EJ2_INTRO)
        elif i == 16:
            nuevos.append(RESP_2A)
        elif i == 17:
            nuevos.append(RESP_2B)
        elif i == 18:
            nuevos.append(RESP_2C)
        elif i == 19:
            nuevos.append(RESP_2D)
            nuevos.append(CIERRE)

    nb['cells'] = nuevos
    # Metadatos mínimos consistentes con nbformat 4
    nb.setdefault('metadata', {})
    nb['metadata'].setdefault('kernelspec', {
        'name': 'python3',
        'display_name': 'Python 3',
        'language': 'python',
    })
    nb['nbformat'] = 4
    nb['nbformat_minor'] = nb.get('nbformat_minor', 0)

    DESTINO.write_text(
        json.dumps(nb, ensure_ascii=False, indent=1),
        encoding='utf-8',
    )
    print(f'✅ Notebook generado: {DESTINO}')
    print(f'   celdas totales:  {len(nuevos)}')
    print(f'   tamaño:          {DESTINO.stat().st_size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
