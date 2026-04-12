#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma el notebook entregable de la Parte 2 partiendo de la consigna
oficial del curso (consigna_parte2.ipynb). Mantiene las celdas
originales intactas e inserta después de cada ejercicio celdas de
respuesta breves que remiten al apéndice datos_parte2.py (todos los
cálculos), al PDF comunicacion_ej3.pdf (ejercicio 3) y a las
visualizaciones embebidas desde datos_parte2_img/.

Salida:
    AnalisisyVisualizacion/entregables/parte2/entregable_ayvd_parte2.ipynb
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CONSIGNA = REPO / 'AnalisisyVisualizacion/entregables/parte2/consigna_parte2.ipynb'
DESTINO = REPO / 'AnalisisyVisualizacion/entregables/parte2/entregable_ayvd_parte2.ipynb'


def md(texto: str) -> dict:
    lineas = texto.splitlines(keepends=True)
    if lineas and not lineas[-1].endswith('\n'):
        lineas[-1] = lineas[-1] + '\n'
    return {
        'cell_type': 'markdown',
        'metadata': {},
        'source': lineas,
    }


# ---------------------------------------------------------------
# Celdas de respuesta
# ---------------------------------------------------------------

PORTADA = md("""\
---

## 📝 Entregable Parte 2 — Rubén Rasi

> **Estado:** 🟡 **Borrador inicial** — todos los cálculos, tests, IC y \
gráficos están implementados y son funcionales. Queda pendiente una \
iteración de revisión de redacción y ajustes finales.

**Docente de seguimiento:** Fredy Alexander Restrepo Blandon

Este notebook se construye sobre la consigna oficial del curso: las \
celdas originales se conservan intactas y se añaden a continuación \
celdas de respuesta que remiten al desarrollo completo.

**Materiales que acompañan este notebook:**

| Archivo | Contenido |
|---|---|
| [`datos_parte2.py`](datos_parte2.py) | 🐍 Apéndice ejecutable: imprime por consola los 16 cuadros intermedios (filtros, estadísticos, IC, test, potencia) y regenera los 5 gráficos matplotlib |
| [`datos_parte2_img/`](datos_parte2_img/) | 🖼️ Los 5 gráficos G1–G5 en PNG, referenciados desde este notebook |
| [`comunicacion_ej3.pdf`](comunicacion_ej3.pdf) | 📄 Reporte técnico de una página A4 para el ejercicio 3 |
| [`README.md`](README.md) | 📋 Índice del entregable y decisiones metodológicas |

Para reproducir los cuadros por consola:

```bash
python datos_parte2.py          # imprime todos los cuadros y regenera los PNG
python datos_parte2.py --csv    # además exporta cada cuadro a CSV

python generar_comunicacion_ej3.py   # regenera el PDF del ejercicio 3
```

### 🧱 Decisiones metodológicas de fondo

Se heredan los filtros F1, F2, F3 y F5 de parte 1 (lenguaje declarado, \
Full-Time, contratos con sueldo mensual, piso SMVM de 300 000 ARS) y se \
agrega un **techo simétrico** de 15 000 000 ARS aplicado a *ambos grupos* \
—la consigna lo aplica sólo a `groupA`, lo que contaminaría la \
diferencia de medias con un artefacto de recorte asimétrico—. El filtro \
F4 de parte 1 (Tukey 1,5·IQR estratificado por moneda) se **omite** en \
parte 2 porque los tests necesitan ver la varianza legítima de la cola \
para calibrar correctamente el IC y el p-valor.

Los grupos analíticos son `groupA = Varón cis` y `groupB = Mujer cis` \
tal como pide la consigna.

---
""")


RESP_EJ1 = md("""\
---

### ✅ Respuesta al Ejercicio 1 — Estimación puntual e IC

#### 🎯 Estimador puntual

El estimador puntual para la diferencia de medias poblacionales es la \
diferencia de medias muestrales:

$$\\widehat{\\Delta} = \\bar{X}_A - \\bar{X}_B$$

Es el estimador insesgado de mínima varianza para la diferencia de \
medias (Clase 03 — Estimación puntual).

#### 📐 Intervalo de confianza: Welch t con varianzas desiguales

Dado que los dos grupos tienen tamaños muestrales muy distintos y \
varianzas muestrales también distintas, el IC se construye con el \
procedimiento de **Welch** (t con varianzas desiguales), usando los \
grados de libertad de **Satterthwaite**:

$$\\widehat{\\Delta} \\pm t_{\\alpha/2,\\;\\nu_W}\\,\\sqrt{\\frac{s_A^2}{n_A} + \\frac{s_B^2}{n_B}}$$

$$\\nu_W = \\frac{\\left(s_A^2/n_A + s_B^2/n_B\\right)^2}{\\dfrac{(s_A^2/n_A)^2}{n_A-1} + \\dfrac{(s_B^2/n_B)^2}{n_B-1}}$$

La elección de Welch sobre el t de Student pooled sigue la \
recomendación del link del propio profesor (Lakens, 2015): usar Welch \
por defecto salvo que haya razones fuertes para asumir igualdad de \
varianzas.

#### 🎲 IC bootstrap percentil (verificación de robustez)

Como control de robustez se calcula también un IC del 95 % por \
**bootstrap percentil** (10 000 resamples con reposición de cada grupo, \
semilla fija). Si el IC paramétrico y el bootstrap son similares, la \
aproximación de Welch es razonable para estos tamaños muestrales.

#### 🔢 Resultados

| | Welch paramétrico | Bootstrap percentil |
|---|---|---|
| **Estimador puntual** | $ 646.851 | ≈ $ 645.800 |
| **IC 95 % inferior** | $ 516.664 | $ 517.447 |
| **IC 95 % superior** | $ 777.037 | $ 774.168 |

Los dos IC son prácticamente coincidentes, lo que indica que la \
aproximación de Welch es adecuada para `n_A = 3134` y `n_B = 773`.

![G1 — Histogramas por grupo](datos_parte2_img/G1_histogramas_grupos.png)

![G2 — Boxplot comparativo](datos_parte2_img/G2_boxplot_comparativo.png)

![G4 — Forest plot con los dos IC](datos_parte2_img/G4_forest_plot_IC.png)

#### 🔗 Relación IC ↔ test de hipótesis

Un IC del $(1-\\alpha)$ para $\\mu_A - \\mu_B$ está en **dualidad exacta** \
con el test bilateral al nivel $\\alpha$ para $H_0: \\mu_A - \\mu_B = 0$. \
Concretamente: **si el IC no contiene el valor 0, el test bilateral al \
mismo nivel rechaza H₀**.

En este caso el IC del 95 % es `[$ 516.664 , $ 777.037]` y **no incluye \
el 0**, por lo que el test bilateral al 5 % rechaza H₀. El ejercicio 2 \
verifica numéricamente esta equivalencia.

---
""")


RESP_2_1 = md("""\
---

### ✅ Respuesta al Ejercicio 2.1 — Formalización del test

| Componente | Especificación |
|---|---|
| **Hipótesis nula** | $H_0:\\;\\mu_A - \\mu_B = 0$ — las medias poblacionales son iguales |
| **Hipótesis alternativa** | $H_1:\\;\\mu_A - \\mu_B \\neq 0$ — bilateral, sin asumir dirección a priori |
| **Estadístico (pivote)** | $T = \\dfrac{\\bar{X}_A - \\bar{X}_B}{\\sqrt{s_A^2/n_A + s_B^2/n_B}}$ |
| **Distribución bajo $H_0$** | $T \\sim t_{\\nu_W}$ con $\\nu_W$ grados de libertad de Welch–Satterthwaite |
| **Nivel de significancia** | $\\alpha = 0{,}05$ *(la consigna lo fija)* |
| **Zona de rechazo** | $\\{\\, \\lvert T \\rvert > t_{\\alpha/2,\\,\\nu_W} \\,\\}$ |

**Por qué bilateral.** La consigna pregunta si la distribución es \
*distinta*, sin prejuzgar la dirección. Un test unilateral ganaría \
potencia a costa de no poder detectar sesgos en el sentido contrario; \
el bilateral es metodológicamente más honesto cuando no hay hipótesis \
previa.

**Justificación del pivote.** Con varianzas muestrales distintas y \
tamaños de grupo desiguales, el estadístico natural es el de Welch y \
su distribución bajo $H_0$ es aproximadamente t de Student con $\\nu_W$ \
grados de libertad calculados por la fórmula de Satterthwaite.

El chequeo visual del supuesto de normalidad se encuentra en los QQ-\
plots del apéndice:

![G3 — QQ-plots contra la normal](datos_parte2_img/G3_qq_plots.png)

Los dos grupos se apartan de la normal en las colas (típico de \
distribuciones de ingreso). Por ese motivo el ejercicio 2.2 suma un \
test **no paramétrico** (Mann-Whitney U) como verificación de robustez \
que no depende del supuesto de normalidad.

""")


RESP_2_2 = md("""\
---

### ✅ Respuesta al Ejercicio 2.2 — P-valor, decisión e interpretación

#### 🔢 Resultado del test de Welch

| Métrica | Valor |
|---|---|
| Estadístico observado $t$ | **9,746** |
| Grados de libertad $\\nu_W$ | **1575,4** |
| P-valor bilateral | **7,84 × 10⁻²²** |
| Nivel $\\alpha$ | 0,05 |
| **Decisión** | **se rechaza H₀** |

#### 🧭 Interpretación correcta del p-valor

> Bajo $H_0$ (medias poblacionales iguales), la probabilidad de \
observar una diferencia de medias **tan o más extrema** que la de esta \
muestra es aproximadamente $7{,}8 \\times 10^{-22}$. Este valor es \
enormemente inferior al nivel $\\alpha = 0{,}05$ fijado, por lo que los \
datos son **incompatibles** con $H_0$ al nivel elegido y la hipótesis \
nula se **rechaza**.

Errores de interpretación a evitar:
- ❌ *"p es la probabilidad de que $H_0$ sea cierta"* → incorrecto.
- ❌ *"los datos prueban que existe una diferencia"* → los datos son \
*compatibles* con la existencia de una diferencia; no la prueban en \
sentido absoluto.
- ✅ *"los datos son incompatibles con $H_0$ al nivel $\\alpha$ elegido"*.

#### 🛡️ Verificación no paramétrica — Mann-Whitney U

Dado que los QQ-plots muestran apartamientos de la normal en las colas, \
se complementa el test con **Mann-Whitney U** bilateral (no asume \
normalidad): p-valor $\\approx 1{,}12 \\times 10^{-15}$. **Arroja la \
misma decisión** que el Welch, lo que indica que el resultado no es \
artefacto del supuesto de normalidad y que la conclusión es robusta al \
procedimiento.

""")


RESP_2_3 = md("""\
---

### ✅ Respuesta al Ejercicio 2.3 — Potencia del test

#### 📏 Tamaño del efecto y tamaños muestrales

Se calcula el effect size de **Cohen's d** con desvío pooled y se \
resuelve el tamaño muestral $n_A$ necesario para alcanzar potencias \
convencionales, manteniendo el mismo ratio $n_B/n_A$ observado:

| Métrica | Valor |
|---|---|
| Cohen's d | **0,324** *(efecto moderado según convención)* |
| $n_A$ necesario para $1-\\beta = 0{,}80$ | **380** |
| $n_A$ necesario para $1-\\beta = 0{,}90$ | **507** |
| $n_A$ necesario para $1-\\beta = 0{,}95$ | **627** |
| $n_A$ real de la muestra | **3 134** |
| **Potencia observada con el $n_A$ real** | **≈ 1,0000** |

![G5 — Curva de potencia](datos_parte2_img/G5_curva_potencia.png)

#### 🧠 ¿Qué significa "potencia"?

La potencia $1 - \\beta$ es la probabilidad de **rechazar $H_0$ cuando \
$H_1$ es cierta** (es decir, detectar una diferencia real del tamaño \
asumido). Una potencia alta implica baja probabilidad de falso \
negativo.

**Cuidado con la interpretación inversa:** un test con baja potencia \
que *no rechaza* $H_0$ **no es evidencia de igualdad** — puede reflejar \
que el $n$ es insuficiente para detectar la diferencia.

#### 🧭 ¿Es esta muestra suficiente?

**Para describir una tendencia general** en la encuesta: **sí, con \
margen**. El $n_A$ real (3 134) supera varias veces el necesario para \
cualquier umbral convencional de potencia. La potencia observada al \
effect size real es prácticamente 1.

**Para una causa legal contra una empresa por discriminación salarial: \
no alcanza.** En ese contexto harían falta:

1. **Potencia ≥ 0,95** y control estricto del error tipo I (α ≤ 0,01 o \
corrección por comparaciones múltiples).
2. **Análisis multivariado** que controle por experiencia, seniority, \
especialización, provincia y otras variables correlacionadas, para \
separar el efecto del género del de los confounders.
3. **Marco metodológico formal**: protocolo preregistrado, auditoría \
de datos, expertos independientes, replicación.

El test bivariado presentado describe una **diferencia en la muestra**, \
no establece **causalidad por género** y no debería usarse de manera \
aislada como prueba en un proceso legal.

---
""")


RESP_EJ3 = md("""\
---

### ✅ Respuesta al Ejercicio 3 — Comunicación y visualización

#### 🎯 Elección del medio: **Opción 2 — Publicación científica / reporte técnico interno**

La elección del medio no es por gusto sino por **compatibilidad entre \
lo que el informe puede afirmar con honestidad y lo que cada medio \
típicamente hace con las cifras**:

| Medio | Qué afirmaciones permite honestamente | Tendencia habitual del medio | ¿Encaja? |
|---|---|---|---|
| **Tweet / LinkedIn** | Una frase impactante, un número grande | Buscar atención, simplificar, **exacerbar o distorsionar** | ❌ La reducción a *"las mujeres ganan X % menos"* pierde el *"en esta muestra y sin controlar por otros factores"*. La afirmación se vuelve una generalización causal que el informe **no sostiene**. |
| **Difusión ONG** | Narrativa con cifras apoyando una causa | Advocar, movilizar, emocionar | ⚠️ Permite limitaciones pero tiende a subordinarlas al mensaje. El informe soporta una afirmación descriptiva bivariada, que en un artículo de difusión queda diluida. |
| **Reporte técnico / publicación científica** | Resultado numérico preciso, IC, test, tamaño del efecto, **limitaciones metodológicas explícitas** | Precisión, reproducibilidad, nuance | ✅ Es **exactamente** el envase que pide el contenido del informe. El medio *espera* y *celebra* las limitaciones en vez de castigarlas. |

> **La opción 2 es la única que permite comunicar exactamente lo que los \
datos soportan, sin exagerar ni subestimar.** Las otras dos forzarían \
distorsión para encajar en sus convenciones.

#### 📄 Resultado

El PDF generado está en [`comunicacion_ej3.pdf`](comunicacion_ej3.pdf) \
(una página A4, formato reporte técnico). Contiene:

- **Título y resumen** con la cifra central.
- **Figura principal** (forest plot con IC Welch y bootstrap).
- **Tabla técnica** con n, medias, desvíos, t, ν, p-valor, Mann-Whitney, \
Cohen's d y potencia.
- **Limitaciones** con 4 bullets: análisis bivariado, sesgo de \
autoselección, filtros declarados, implicancia legal.
- **Oración con énfasis** que resume el mensaje central respetando el \
alcance real del análisis.

Para regenerarlo:

```bash
python generar_comunicacion_ej3.py
```

---

### 🧾 Cierre

Los tres ejercicios se resolvieron de manera consistente: la estimación \
del ejercicio 1 (Welch + bootstrap) dialoga con el test del ejercicio \
2 (dualidad IC ↔ test), y el ejercicio 3 comunica el resultado en el \
único formato que admite las limitaciones que el propio análisis \
declara.

""")


# ---------------------------------------------------------------
# Integración
# ---------------------------------------------------------------

def main() -> None:
    nb = json.loads(CONSIGNA.read_text(encoding='utf-8'))
    originales = nb['cells']

    # Mapeo de índices relevantes en la consigna original:
    #   0   : título
    #   1-12: imports, lectura, construcción de groupA/groupB, describe, hist
    #   13  : consigna ejercicio 1 (markdown)
    #   14  : celda de código vacía para responder ej 1
    #   15  : encabezado ejercicio 2
    #   16  : consigna 2.1 formalización
    #   17  : consigna 2.2 p-valor
    #   18  : consigna 2.3 potencia
    #   19-21: código de potencia (imports, effect_size, tt_ind_solve_power)
    #   22  : consigna ejercicio 3
    #   23  : celda de código vacía

    nuevos: list[dict] = []
    for i, celda in enumerate(originales):
        celda = copy.deepcopy(celda)
        if celda['cell_type'] == 'markdown':
            celda.pop('execution_count', None)
            celda.pop('outputs', None)
        else:
            celda.setdefault('outputs', [])
            celda.setdefault('execution_count', None)
        # Portada antes del primer encabezado de ejercicios (consigna ej 1)
        if i == 13:
            nuevos.append(PORTADA)
        nuevos.append(celda)
        if i == 14:
            nuevos.append(RESP_EJ1)
        elif i == 16:
            nuevos.append(RESP_2_1)
        elif i == 17:
            nuevos.append(RESP_2_2)
        elif i == 18:
            nuevos.append(RESP_2_3)
        elif i == 22:
            nuevos.append(RESP_EJ3)

    nb['cells'] = nuevos
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
