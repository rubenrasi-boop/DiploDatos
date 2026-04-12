# 📖 Guía teórica — Entregable AyVD Parte 2

> Todos los conceptos estadísticos y metodológicos necesarios para resolver
> los Ejercicios 1, 2 y 3 del entregable parte 2, explicados en profundidad.

---

## Índice

1. [Población, muestra y estimadores](#1-población-muestra-y-estimadores)
   - 1.1 Parámetro vs estimador
   - 1.2 Distribución muestral
   - 1.3 Teorema Central del Límite
   - 1.4 Error estándar
   - 1.5 Propiedades de los estimadores
2. [Estimación puntual e intervalar](#2-estimación-puntual-e-intervalar)
   - 2.1 Estimación puntual
   - 2.2 Intervalo de confianza
   - 2.3 IC para la media
   - 2.4 IC para la diferencia de medias
   - 2.5 Interpretación correcta del IC
3. [Test de hipótesis](#3-test-de-hipótesis)
   - 3.1 Componentes del test
   - 3.2 Hipótesis nula y alternativa
   - 3.3 Estadístico de prueba (pivote)
   - 3.4 Región de rechazo y valor crítico
   - 3.5 P-valor
   - 3.6 Decisión e interpretación
   - 3.7 Test t de Student
   - 3.8 Test de Welch
4. [Errores y potencia del test](#4-errores-y-potencia-del-test)
   - 4.1 Error Tipo I (α)
   - 4.2 Error Tipo II (β)
   - 4.3 Potencia del test (1 - β)
   - 4.4 Tamaño del efecto (effect size)
   - 4.5 Tamaño de muestra necesario
5. [Comunicación y visualización de resultados](#5-comunicación-y-visualización-de-resultados)
   - 5.1 Principios de comunicación efectiva
   - 5.2 Elegir la visualización adecuada
   - 5.3 Adaptar al público objetivo
   - 5.4 Las tres audiencias del entregable
6. [Mapa de conceptos por ejercicio](#6-mapa-de-conceptos-por-ejercicio)

---

## 1. Población, muestra y estimadores

### 1.1 Parámetro vs estimador

| Concepto | Definición | Ejemplo |
|----------|-----------|---------|
| **Parámetro** (θ) | Valor verdadero de la población (desconocido, fijo) | μ = salario promedio real de TODOS los trabajadores IT de Argentina |
| **Estimador** (θ̂) | Función de los datos muestrales que se usa para aproximar θ | x̄ = salario promedio de los 4.939 encuestados |
| **Estimación** | El valor numérico concreto que produce el estimador | x̄ = $2.403.162 |

El estimador es una **variable aleatoria** (cambia con cada muestra), mientras que el parámetro es un valor fijo que queremos conocer pero no podemos observar directamente.

### 1.2 Distribución muestral

Si tomáramos muchas muestras de la misma población y calculáramos la media de cada una, obtendríamos una **distribución de medias muestrales**. Esta distribución tiene propiedades conocidas que son la base de toda la inferencia estadística.

![Teorema Central del Límite](img/01_01_tcl_muestreo.png)
*Fig. 1.1 — Izquierda: distribución de la población (asimétrica). Derecha: distribución de las medias muestrales de 500 muestras de n=200. A pesar de que la población no es normal, la distribución de medias se aproxima a una campana de Gauss (TCL).*

### 1.3 Teorema Central del Límite (TCL)

El TCL es uno de los teoremas más importantes de la estadística:

> **Si X₁, X₂, ..., Xₙ son variables aleatorias independientes e idénticamente distribuidas con media μ y varianza σ², entonces la distribución de la media muestral x̄ se aproxima a una normal a medida que n crece:**

$$\bar{X} \xrightarrow{d} N\left(\mu, \frac{\sigma^2}{n}\right)$$

**¿Por qué importa?**
- No importa la forma de la distribución original (puede ser asimétrica, bimodal, etc.).
- Con n suficientemente grande (en la práctica, n ≥ 30 suele ser suficiente), la distribución de x̄ es aproximadamente normal.
- Esto nos permite construir intervalos de confianza y hacer tests de hipótesis **sin asumir normalidad de los datos originales**.

### 1.4 Error estándar

El **error estándar** (SE) mide cuánto varía el estimador de muestra en muestra:

$$SE(\bar{X}) = \frac{s}{\sqrt{n}}$$

- **s** = desvío estándar de la muestra
- **n** = tamaño de la muestra
- A mayor n → menor SE → estimaciones más precisas
- A mayor variabilidad (s) → mayor SE → estimaciones menos precisas

**En Python:** `se = df['salary_monthly_NETO'].std() / np.sqrt(len(df))`

### 1.5 Propiedades de los estimadores

Un buen estimador debe ser:

| Propiedad | Significado | ¿La media muestral lo cumple? |
|-----------|-------------|:----:|
| **Insesgado** | En promedio, acierta al parámetro real. E(θ̂) = θ | ✅ Sí |
| **Consistente** | Se acerca al parámetro real al aumentar n | ✅ Sí |
| **Eficiente** | Tiene la menor varianza posible entre los estimadores insesgados | ✅ Sí (bajo normalidad) |

![Estimador puntual](img/01_02_estimador_puntual.png)
*Fig. 1.2 — 30 muestras distintas de la misma población. Cada punto azul es la media de una muestra (estimación puntual). La línea roja es el parámetro real μ. Las estimaciones fluctúan alrededor del valor verdadero: el estimador es insesgado pero impreciso.*

---

## 2. Estimación puntual e intervalar

### 2.1 Estimación puntual

Es dar **un solo número** como aproximación del parámetro.

**Ejemplo del entregable:** La estimación puntual de la diferencia de medias salariales entre varones y mujeres es:

$$\hat{\Delta} = \bar{X}_A - \bar{X}_B$$

Un solo número que resume la brecha, pero **no dice nada sobre la incertidumbre** de esa estimación.

### 2.2 Intervalo de confianza (IC)

En vez de un solo número, damos un **rango de valores plausibles** para el parámetro, acompañado de un nivel de confianza.

**Estructura general:**

$$IC = \hat{\theta} \pm z_{\alpha/2} \cdot SE(\hat{\theta})$$

Donde:
- θ̂ = estimación puntual
- z_{α/2} = valor crítico de la distribución normal (1.96 para 95%)
- SE = error estándar del estimador

![Intervalos de confianza](img/02_01_intervalos_confianza.png)
*Fig. 2.1 — 25 intervalos de confianza al 95% construidos a partir de 25 muestras distintas. Los intervalos en verde contienen el parámetro real (línea punteada); los rojos no. En promedio, el 95% de los intervalos contienen el valor verdadero.*

### 2.3 IC para la media

$$IC_{1-\alpha}(\mu) = \bar{x} \pm z_{\alpha/2} \cdot \frac{s}{\sqrt{n}}$$

Para α = 0.05 (confianza 95%): z_{0.025} = 1.96

**En Python:**
```python
from scipy import stats
mean = data.mean()
se = data.std() / np.sqrt(len(data))
ci_low = mean - 1.96 * se
ci_high = mean + 1.96 * se
```

### 2.4 IC para la diferencia de medias

Este es el IC que pide el **Ejercicio 1** del entregable:

$$IC_{1-\alpha}(\mu_A - \mu_B) = (\bar{X}_A - \bar{X}_B) \pm z_{\alpha/2} \cdot SE_{diff}$$

Donde el error estándar de la diferencia es:

$$SE_{diff} = \sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}$$

![IC diferencia de medias](img/02_02_ic_diferencia_medias.png)
*Fig. 2.2 — Intervalo de confianza al 95% para la diferencia de medias salariales entre varones y mujeres. El rombo rojo es la estimación puntual. Si el IC no cruza el cero (línea gris), podemos decir que la diferencia es estadísticamente significativa.*

### 2.5 Interpretación correcta del IC

| Interpretación | ¿Correcta? |
|---------------|:-----------:|
| "Hay un 95% de probabilidad de que μ esté dentro de este intervalo" | ❌ **Incorrecta** |
| "Si repitiéramos el muestreo muchas veces, el 95% de los intervalos construidos contendrían μ" | ✅ **Correcta** |

El parámetro μ es fijo (no es aleatorio). Lo que varía es el intervalo (porque depende de la muestra). Un IC concreto o contiene a μ o no lo contiene; no hay "probabilidad" de que lo contenga.

**Relación con el test de hipótesis:**
- Si el IC para μ_A - μ_B **no contiene el 0** → rechazamos H₀: μ_A = μ_B
- Si el IC **contiene el 0** → no rechazamos H₀
- Esto es **equivalente** a hacer un test bilateral al mismo nivel α

---

## 3. Test de hipótesis

### 3.1 Componentes del test

Un test de hipótesis es un procedimiento formal para decidir, a partir de datos muestrales, si una afirmación sobre la población es plausible o no.

**Componentes:**
1. **Hipótesis** (H₀ y H₁)
2. **Estadístico de prueba** (pivote)
3. **Distribución bajo H₀**
4. **Regla de decisión** (valor crítico o p-valor)
5. **Nivel de significancia** (α)

### 3.2 Hipótesis nula y alternativa

| Hipótesis | Notación | Significado | En el entregable |
|-----------|----------|-------------|------------------|
| **Nula** | H₀ | "No hay efecto/diferencia" | H₀: μ_varones = μ_mujeres (no hay brecha salarial) |
| **Alternativa** | H₁ | "Sí hay efecto/diferencia" | H₁: μ_varones ≠ μ_mujeres (sí hay brecha) |

**Tipos de test según H₁:**

| Tipo | H₁ | Uso |
|------|-----|-----|
| **Bilateral** | μ_A ≠ μ_B | Cuando no sabemos la dirección de la diferencia |
| **Unilateral derecho** | μ_A > μ_B | Cuando sospechamos que A es mayor |
| **Unilateral izquierdo** | μ_A < μ_B | Cuando sospechamos que A es menor |

En el entregable se usa un **test bilateral** (no asumimos de antemano quién gana más).

### 3.3 Estadístico de prueba (pivote)

Es una función de los datos que resume la evidencia contra H₀. Para comparar dos medias, el estadístico t es:

$$t = \frac{\bar{X}_A - \bar{X}_B}{SE_{diff}} = \frac{\bar{X}_A - \bar{X}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}}$$

**Distribución bajo H₀:** Si H₀ es verdadera (no hay diferencia), el estadístico t sigue una distribución t de Student (que se aproxima a la normal para muestras grandes).

### 3.4 Región de rechazo y valor crítico

![Región de rechazo](img/03_01_region_rechazo.png)
*Fig. 3.1 — Distribución del estadístico bajo H₀. Las zonas rojas son las regiones de rechazo (α/2 = 2.5% en cada cola). Si el estadístico calculado cae en la zona roja, rechazamos H₀. Los valores críticos ±1.96 delimitan las regiones.*

**Regla de decisión:**
- Si |t_obs| > t_crit → **rechazamos H₀**
- Si |t_obs| ≤ t_crit → **no rechazamos H₀**

### 3.5 P-valor

El **p-valor** es la probabilidad de obtener un estadístico **tan o más extremo** que el observado, **asumiendo que H₀ es verdadera**.

$$p = P(|T| \geq |t_{obs}| \mid H_0)$$

![P-valor visual](img/03_02_pvalor_visual.png)
*Fig. 3.2 — El p-valor (áreas rojas) representa la probabilidad de obtener un resultado tan extremo o más bajo H₀. Cuanto menor es el p-valor, más evidencia contra H₀. La línea azul es el estadístico observado.*

**Interpretación:**
| P-valor | Interpretación |
|---------|---------------|
| p < 0.001 | Evidencia muy fuerte contra H₀ |
| p < 0.01 | Evidencia fuerte contra H₀ |
| p < 0.05 | Evidencia moderada contra H₀ |
| p ≥ 0.05 | Evidencia insuficiente para rechazar H₀ |

**Cuidado con el p-valor:**
- p < 0.05 **NO significa** que H₀ es falsa con 95% de certeza.
- p < 0.05 **NO significa** que el efecto es grande o importante.
- Un p-valor pequeño solo dice que el resultado es **poco probable bajo H₀**, no que H₁ sea verdadera.

### 3.6 Decisión e interpretación

| Resultado | Decisión | Redacción |
|-----------|----------|-----------|
| p < α | Rechazamos H₀ | "Hay evidencia estadísticamente significativa de que existe diferencia entre las medias (p = X)" |
| p ≥ α | No rechazamos H₀ | "No hay evidencia suficiente para afirmar que existe diferencia (p = X)" |

**Nota:** "No rechazar H₀" ≠ "H₀ es verdadera". Simplemente no tenemos evidencia suficiente para descartarla.

### 3.7 Test t de Student (varianzas iguales)

Asume que ambos grupos tienen la **misma varianza** (σ²_A = σ²_B).

$$t = \frac{\bar{X}_A - \bar{X}_B}{s_p \sqrt{\frac{1}{n_A} + \frac{1}{n_B}}}$$

Donde s_p es la varianza combinada (pooled):

$$s_p^2 = \frac{(n_A - 1)s_A^2 + (n_B - 1)s_B^2}{n_A + n_B - 2}$$

**En Python:** `stats.ttest_ind(groupA, groupB, equal_var=True)`

### 3.8 Test de Welch (varianzas distintas)

**No** asume varianzas iguales. Es más robusto y **recomendado por defecto**.

$$t = \frac{\bar{X}_A - \bar{X}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}}$$

Los grados de libertad se calculan con la aproximación de Welch-Satterthwaite (fórmula compleja, scipy lo hace automáticamente).

**En Python:** `stats.ttest_ind(groupA, groupB, equal_var=False)`

**¿Cuándo usar cada uno?**

| Situación | Usar |
|-----------|------|
| Varianzas similares, mismos tamaños de muestra | Student o Welch (dan resultados similares) |
| Varianzas distintas o tamaños de muestra diferentes | **Welch** (siempre más seguro) |
| Duda | **Welch** (es la recomendación general moderna) |

![Distribuciones de grupos](img/03_03_distribuciones_grupos.png)
*Fig. 3.3 — Histogramas superpuestos de salarios de varones (azul) y mujeres (rosa) del dataset. Las líneas punteadas marcan las medias de cada grupo. La separación visual sugiere una diferencia, pero el test formal cuantifica si es estadísticamente significativa.*

---

## 4. Errores y potencia del test

### 4.1 Error Tipo I (α)

| Situación | Decisión | Resultado |
|-----------|----------|-----------|
| H₀ es verdadera | Rechazamos H₀ | **Error Tipo I** (falso positivo) |
| Probabilidad: | | **α** (nivel de significancia) |

**Ejemplo:** Decir que hay brecha salarial de género cuando en realidad no la hay.

α lo fijamos nosotros (convencionalmente 0.05). Es el "riesgo que estamos dispuestos a tolerar" de equivocarnos al rechazar H₀.

### 4.2 Error Tipo II (β)

| Situación | Decisión | Resultado |
|-----------|----------|-----------|
| H₀ es falsa | No rechazamos H₀ | **Error Tipo II** (falso negativo) |
| Probabilidad: | | **β** |

**Ejemplo:** No detectar una brecha salarial que realmente existe.

β depende de: el tamaño del efecto real, el tamaño de la muestra, y α.

### 4.3 Potencia del test (1 - β)

La **potencia** es la probabilidad de rechazar H₀ **cuando es falsa** (es decir, detectar un efecto real).

$$\text{Potencia} = 1 - \beta = P(\text{Rechazar } H_0 \mid H_0 \text{ es falsa})$$

| Potencia | Interpretación |
|----------|---------------|
| 0.80 | Estándar mínimo aceptable |
| 0.90 | Buena potencia |
| 0.95 | Muy buena potencia |

**Factores que aumentan la potencia:**
- Mayor tamaño de muestra (n) → más potencia
- Mayor tamaño del efecto → más fácil de detectar
- Mayor α → más potencia (pero más riesgo de Error Tipo I)

![Errores Tipo I y II](img/04_01_errores_tipo_I_II.png)
*Fig. 4.1 — Curva azul: distribución bajo H₀. Curva roja: distribución bajo H₁ (efecto real). El área azul a la derecha del valor crítico es α (Error Tipo I). El área roja a la izquierda es β (Error Tipo II). La potencia (1-β) es el área roja a la derecha del valor crítico.*

**Tabla resumen:**

|  | H₀ verdadera | H₀ falsa |
|--|:----------:|:--------:|
| **No rechazar H₀** | ✅ Decisión correcta (1-α) | ❌ Error Tipo II (β) |
| **Rechazar H₀** | ❌ Error Tipo I (α) | ✅ Decisión correcta (potencia = 1-β) |

### 4.4 Tamaño del efecto (effect size)

El **effect size** (d de Cohen) estandariza la diferencia entre grupos, independientemente de las unidades:

$$d = \frac{\bar{X}_A - \bar{X}_B}{s_{pooled}}$$

| d | Interpretación |
|---|---------------|
| 0.2 | Efecto pequeño |
| 0.5 | Efecto mediano |
| 0.8 | Efecto grande |

**¿Por qué importa?** Porque con una muestra suficientemente grande, **cualquier diferencia** (por mínima que sea) puede resultar "estadísticamente significativa". El effect size dice si la diferencia es **prácticamente relevante**.

### 4.5 Tamaño de muestra necesario

Antes de recolectar datos, se debería calcular el **n mínimo** para detectar un efecto de cierto tamaño con una potencia deseada.

**En Python:**
```python
from statsmodels.stats.power import tt_ind_solve_power

n_needed = tt_ind_solve_power(
    effect_size=d,      # tamaño del efecto esperado
    alpha=0.05,         # nivel de significancia
    power=0.80,         # potencia deseada
    ratio=n_B/n_A       # relación entre tamaños de grupo
)
```

![Potencia vs tamaño de muestra](img/04_02_potencia_vs_n.png)
*Fig. 4.2 — Tamaño de muestra necesario (por grupo) para alcanzar distintos niveles de potencia, dado el effect size observado en los datos. A mayor potencia deseada, se necesitan más observaciones.*

---

## 5. Comunicación y visualización de resultados

El **Ejercicio 3** pide comunicar un resultado del análisis adaptado a una audiencia específica.

### 5.1 Principios de comunicación efectiva

1. **Un mensaje central:** ¿cuál es la conclusión más importante? Reducirla a una oración.
2. **Reducir el ruido:** eliminar todo lo que no aporte al mensaje.
3. **Jerarquía visual:** lo más importante se ve primero.
4. **Contexto necesario:** el receptor debe entender sin leer todo el informe.

### 5.2 Elegir la visualización adecuada

| Querés mostrar... | Usá... | NO usés... |
|-------------------|--------|-----------|
| Comparación entre 2 grupos | Barras, boxplot | Pie chart |
| Distribución | Histograma, KDE | Tabla de números |
| Tendencia temporal | Líneas | Barras |
| Proporción de un todo | Pie chart (max 5 categorías) | Pie chart con 15 categorías |
| Relación entre 2 variables | Scatterplot | Tabla |

![Comunicación limpia](img/05_01_comunicacion_limpia.png)
*Fig. 5.1 — Ejemplo de visualización limpia para comunicar la brecha salarial. Usa solo dos barras, colores intuitivos, valores numéricos visibles y un dato resumen destacado. El mensaje se entiende en segundos.*

![Bueno vs malo](img/05_02_bueno_vs_malo.png)
*Fig. 5.2 — Izquierda: un pie chart que no comunica la brecha salarial (mala elección). Derecha: un boxplot comparativo que muestra distribución, centro y dispersión de ambos grupos (buena elección). La visualización correcta depende del mensaje.*

### 5.3 Adaptar al público objetivo

| Audiencia | Nivel técnico | Énfasis en... |
|-----------|:------------:|---------------|
| Artículo de difusión | Bajo | Simpleza, impacto social, lenguaje accesible |
| Publicación científica | Alto | Rigor, significancia, limitaciones, metodología |
| Tweet / LinkedIn | Muy bajo | Un solo dato impactante, visual en segundos |

### 5.4 Las tres audiencias del entregable

**Opción 1 — Artículo de difusión (ONG):**
- Lenguaje simple, sin jerga estadística.
- Un gráfico limpio con colores significativos.
- Una oración de énfasis tipo: "Las mujeres en tecnología ganan un X% menos que los varones."
- No más de 1 página A4.

**Opción 2 — Publicación científica:**
- Incluir p-valor, intervalo de confianza, effect size.
- Justificar la validez: supuestos del test, potencia, limitaciones.
- Puede ser más denso y complejo.
- No más de 1 página A4.

**Opción 3 — Tweet / LinkedIn:**
- Un número impactante o un gráfico que se entienda en 3 segundos.
- Ejemplo: "En Argentina, los programadores varones ganan un X% más que las programadoras. Fuente: Sysarmy 2026."
- Aparte, una breve descripción de metodología (no en el tweet, sino adjunta).

---

## 6. Mapa de conceptos por ejercicio

| Concepto | Ej.1 (Estimación) | Ej.2 (Test) | Ej.3 (Comunicación) |
|----------|:--:|:--:|:--:|
| Parámetro vs estimador | ✅ | | |
| Error estándar | ✅ | ✅ | |
| Estimación puntual | ✅ | | |
| Intervalo de confianza | ✅ | | |
| IC para diferencia de medias | ✅ | | |
| Relación IC ↔ test | ✅ | ✅ | |
| Hipótesis nula y alternativa | | ✅ | |
| Estadístico de prueba (t) | | ✅ | |
| Distribución bajo H₀ | | ✅ | |
| P-valor | | ✅ | ✅ |
| Test de Welch | | ✅ | |
| Error Tipo I (α) | | ✅ | |
| Error Tipo II (β) | | ✅ | |
| Potencia (1-β) | | ✅ | |
| Effect size (d de Cohen) | | ✅ | ✅ |
| Tamaño de muestra necesario | | ✅ | |
| Principios de comunicación | | | ✅ |
| Elección de visualización | | | ✅ |
| Adaptación al público | | | ✅ |
