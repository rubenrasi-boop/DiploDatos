# 📝 Entregable AyVD — Parte 2

**Materia:** Análisis y Visualización de Datos 2026
**Alumno:** Rubén Rasi
**Docente de seguimiento:** Fredy Alexander Restrepo Blandon

> **🟡 Estado: Borrador inicial.** Todos los cálculos, tests, intervalos de confianza, gráficos y el PDF de comunicación ya están implementados y son funcionales. Queda una iteración pendiente de revisión de redacción y consistencia narrativa antes de considerarlo definitivo.

---

## 📅 Fechas

| Campo | Detalle |
|-------|---------|
| **Apertura** | Viernes 17/04/2026, 06:00 |
| **Entrega** | Domingo 27/04/2026, 23:59 |
| **Consigna** | [Ver en Google Drive](https://drive.google.com/file/d/1FBA-CVfB-EUfHtpOCndy_wCI4u2kFya7/view?usp=sharing) |

---

## 🎯 Objetivos

1. Describir y analizar la base desde múltiples ángulos *(ya abordado en parte 1)*.
2. Diferenciar datos de modelos.
3. Realizar inferencia: estimación y testeo.
4. Comunicar resultados en el formato adecuado a la capacidad del análisis.

---

## 📋 Ejercicios resueltos

### Ejercicio 1 — Estimación puntual e intervalo de confianza

**Consigna:** estimar puntualmente y con intervalo de confianza del 95 % la diferencia de medias del sueldo NETO entre varones cis y mujeres cis.

- **Estimador puntual:** Δ̂ = x̄_A − x̄_B = $ 646.851.
- **IC del 95 % por Welch** (t con varianzas desiguales, grados de libertad de Satterthwaite): `[$ 516.664 , $ 777.037]`.
- **IC del 95 % por bootstrap percentil** (10 000 resamples, semilla fija) como verificación de robustez: `[$ 517.447 , $ 774.168]`. La coincidencia con el IC paramétrico indica que la aproximación de Welch es adecuada para los tamaños muestrales.
- **Relación IC ↔ test:** se explicita la dualidad exacta entre el IC del (1−α) y el test bilateral al nivel α. El IC no contiene el 0, por lo que el test del ejercicio 2 rechaza H₀.

### Ejercicio 2 — Test de hipótesis

- **2.1 Formalización:** H₀: μ_A = μ_B · H₁: μ_A ≠ μ_B (bilateral) · pivote T = (x̄_A − x̄_B) / √(s_A²/n_A + s_B²/n_B) con distribución t de Student bajo H₀ (grados de libertad de Welch–Satterthwaite) · α = 0,05.
- **2.2 P-valor y decisión:** t observado = 9,746 · ν = 1575,4 · p-valor bilateral ≈ 7,84 × 10⁻²² → se rechaza H₀ al nivel α = 0,05. Se agrega test de **Mann-Whitney U** (p ≈ 1,12 × 10⁻¹⁵) como verificación no paramétrica de robustez: coincide en la decisión.
- **2.3 Potencia:** Cohen's d = 0,324 (efecto moderado) · n_A necesario para potencia 0,80 / 0,90 / 0,95 = 380 / 507 / 627 · n_A real = 3 134 · potencia observada ≈ 1,0000. Se discute explícitamente la diferencia entre *tendencia general* (la muestra alcanza con holgura) y *causa legal por discriminación* (no alcanza: hace falta análisis multivariado, control de confounders y marco metodológico formal).

### Ejercicio 3 — Comunicación y visualización

**Opción elegida: 2 — Publicación científica / reporte técnico interno.** Se justifica en el notebook con una tabla comparativa de los tres medios: es el único que permite comunicar con honestidad lo que los datos soportan (diferencia bivariada con IC, test, potencia y limitaciones explícitas) sin caer en la tendencia natural de los otros dos medios a simplificar o exacerbar.

El PDF `comunicacion_ej3.pdf` contiene en una página A4: título, resumen numérico, figura principal (forest plot con Welch y bootstrap), tabla técnica completa, cuatro bullets de limitaciones y una oración con énfasis que respeta el alcance real del análisis.

---

## 🧱 Decisiones metodológicas

### Filtros aplicados (versus la consigna)

| Filtro | Criterio | Justificación |
|--------|---------|---------------|
| **F1** | `tools_programming_languages.notna() & NETO.notna()` | Heredado de parte 1 — misma base muestral, comparabilidad directa. |
| **F2** | `work_dedication == 'Full-Time'` | Un sueldo mensual Part-Time no es comparable con uno Full-Time. |
| **F3** | `work_contract_type ∈ {Staff, Contractor, Tercerizado}` | Descarta Freelance y Cooperativa (rentas variables no representan un salario). |
| **F5** | `NETO ≥ 300.000 ARS` | Piso SMVM argentino 2026. **Reemplaza al piso de 100 000 de la consigna**, que está por debajo del SMVM y captura respuestas erróneas. |
| **F6** | `NETO ≤ 15.000.000 ARS` **simétrico** | La consigna lo aplica sólo a `groupA`, lo que contaminaría la diferencia de medias con un recorte asimétrico. Aplicarlo a ambos grupos mantiene la ventana de comparación honesta. |
| **F4** *omitido* | Tukey 1,5·IQR por moneda (usado en parte 1) | Los tests del ej 2 necesitan ver la varianza legítima de la cola para calibrar correctamente IC y p-valores. Recortarla sería esconder información al procedimiento inferencial. |

### Grupos analíticos

- `groupA` = **Varón cis** (`profile_gender == 'Hombre Cis'`)
- `groupB` = **Mujer cis** (`profile_gender == 'Mujer Cis'`)

La agrupación "Diversidades" usada en parte 1 no se incluye acá porque la consigna pide específicamente diferencia entre los dos grupos mayoritarios.

---

## 📂 Archivos del entregable

```
parte2/
├── README.md                           ← Este archivo
├── consigna_parte2.ipynb               ← Consigna oficial del curso (intacta)
│
├── entregable_ayvd_parte2.ipynb        ← 📓 NOTEBOOK ENTREGABLE
│                                         (consigna + respuestas integradas)
│
├── datos_parte2.py                     ← 🐍 Apéndice ejecutable de datos
│
├── datos_parte2_img/                   ← Gráficos matplotlib/seaborn
│   ├── G1_histogramas_grupos.png        ← histogramas comparativos por grupo
│   ├── G2_boxplot_comparativo.png       ← boxplot + puntos con jitter + medias
│   ├── G3_qq_plots.png                  ← QQ-plots contra la normal
│   ├── G4_forest_plot_IC.png            ← forest plot de los IC Welch y bootstrap
│   └── G5_curva_potencia.png            ← curva de potencia vs tamaño muestral
│
├── comunicacion_ej3.pdf                ← 📄 PDF del ejercicio 3 (una página A4)
│
└── data/
    └── sysarmy_survey_2026_processed.csv   ← Dataset de entrada
```

---

## 🚀 Cómo revisar el entregable

### Opción 1 — Notebook entregable (recomendada)

Abrir **`entregable_ayvd_parte2.ipynb`** en Jupyter, VS Code o Google Colab. El notebook se construye sobre la consigna oficial (celdas intactas) e intercala después de cada ejercicio una celda de respuesta con los hallazgos clave y los gráficos embebidos desde `datos_parte2_img/`. Las limitaciones y la discusión sobre "tendencia general vs juicio penal" están incorporadas como parte de la respuesta al ejercicio 2.3.

### Opción 2 — PDF del ejercicio 3

Abrir **`comunicacion_ej3.pdf`** directamente. Es una página A4 autocontenida con el reporte técnico pedido por el ejercicio 3: título, resumen, figura principal, tabla técnica, limitaciones y oración con énfasis.

### Opción 3 — Cotejar los datos por consola

El archivo **`datos_parte2.py`** es el apéndice de datos del entregable. Imprime por consola los 16 cuadros intermedios (filtros, estadísticos, componentes del IC, test de Welch, Mann-Whitney, potencia) y regenera los 5 gráficos matplotlib.

```bash
# Desde esta carpeta (entregables/parte2/)
python datos_parte2.py          # imprime todos los cuadros y regenera los PNG
python datos_parte2.py --csv    # además exporta cada cuadro a CSV
```

---

## 🛠️ Stack técnico

| Uso | Librería |
|---|---|
| Manipulación de datos | `pandas`, `numpy` |
| Tests estadísticos | `scipy.stats` (t de Welch, Mann-Whitney U) |
| Potencia estadística | `statsmodels.stats.power` (Cohen's d, tt_ind_solve_power) |
| Gráficos | `matplotlib`, `seaborn` |

Dependencias: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`.

---

## 🔗 Material de referencia utilizado

| Fuente | Uso |
|---|---|
| **Clase 03 — Estimación** | Estimación puntual e intervalar, ley de los grandes números, t de Student. |
| **Clase 04 — Test de Hipótesis** | Formalización de H₀/H₁, pivote, p-valor, potencia, error tipo I y tipo II. |
| **Clase 04 — Visualización y Comunicación** | Elección del medio en función del mensaje; jerarquía visual en gráficos estadísticos. |
| **Consigna oficial** | `consigna_parte2.ipynb` |
| **Daniel Lakens (2015)** | *"Always use Welch's t-test instead of Student's t-test"* — link sugerido por el profesor. |

Todas las filminas del curso tienen un mirror local en `_site/filminas/` en PDF y TXT.
