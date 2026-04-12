# 🎞️ Filminas de la materia AyVD 2026

Mirror local de las 8 presentaciones de Google Slides referenciadas en el
[`README.md` principal de la materia](../../AnalisisyVisualizacion/README.md).
Cada clase del curso tiene **2 filminas** (una por cada mitad temática).

Cada presentación se descargó en dos formatos:

| Formato | Uso |
|---|---|
| `.pdf` | Visualización fiel al diseño original (gráficos, tablas, layout) |
| `.txt` | Búsqueda rápida por texto y cotejo contra las notebooks |

Fuente original: `docs.google.com/presentation/d/<id>` con el endpoint
`/export/<formato>` (los archivos son públicos del curso).

---

## 📑 Índice por clase

### Clase 1 — Introducción, Probabilidad y Estadística Descriptiva
*27 de marzo de 2026*

| Presentación | PDF | TXT | Google Slides |
|---|---|---|---|
| Introducción | [`clase1_introduccion.pdf`](clase1_introduccion.pdf) | [`clase1_introduccion.txt`](clase1_introduccion.txt) | [ver online](https://docs.google.com/presentation/d/1VeklzWjRLGgS1dEOwtETYX23G5nNC_WP/edit) |
| Probabilidad y Estadística | [`clase1_probabilidad_y_estadistica.pdf`](clase1_probabilidad_y_estadistica.pdf) | [`clase1_probabilidad_y_estadistica.txt`](clase1_probabilidad_y_estadistica.txt) | [ver online](https://docs.google.com/presentation/d/1do5BSgqE_lkesHfkrPLkun8KLLOQxPCi/edit) |

### Clase 2 — Datos, Modelos y Varias Variables
*28 de marzo de 2026*

| Presentación | PDF | TXT | Google Slides |
|---|---|---|---|
| Datos y Modelos | [`clase2_datos_y_modelos.pdf`](clase2_datos_y_modelos.pdf) | [`clase2_datos_y_modelos.txt`](clase2_datos_y_modelos.txt) | [ver online](https://docs.google.com/presentation/d/1LtWnr73XHih-UjcRjRjfEGGPZATJED9X/edit) |
| Varias Variables | [`clase2_varias_variables.pdf`](clase2_varias_variables.pdf) | [`clase2_varias_variables.txt`](clase2_varias_variables.txt) | [ver online](https://docs.google.com/presentation/d/1yhp_0p9Mun6Qjud4k0NWZt0tKxFcrQ86/edit) |

### Clase 3 — Estadísticos, Estadística y Estimación
*10 de abril de 2026*

| Presentación | PDF | TXT | Google Slides |
|---|---|---|---|
| Estadísticos y Estadística | [`clase3_estadisticos_y_estadistica.pdf`](clase3_estadisticos_y_estadistica.pdf) | [`clase3_estadisticos_y_estadistica.txt`](clase3_estadisticos_y_estadistica.txt) | [ver online](https://docs.google.com/presentation/d/1y57J0FW-uqJttYHsyesjGw63RYvfpN1c/edit) |
| Estimación | [`clase3_estimacion.pdf`](clase3_estimacion.pdf) | [`clase3_estimacion.txt`](clase3_estimacion.txt) | [ver online](https://docs.google.com/presentation/d/1BNcIQHCEfifmPcvJWblgGlrmYoO5-OEF/edit) |

### Clase 4 — Test de Hipótesis, Visualización y Comunicación
*11 de abril de 2026*

| Presentación | PDF | TXT | Google Slides |
|---|---|---|---|
| Test de Hipótesis | [`clase4_test_de_hipotesis.pdf`](clase4_test_de_hipotesis.pdf) | [`clase4_test_de_hipotesis.txt`](clase4_test_de_hipotesis.txt) | [ver online](https://docs.google.com/presentation/d/10RWp7bJl6HfXmc9ua8-Qypvh8lXPf8VO/edit) |
| Visualización y Comunicación | [`clase4_visualizacion_y_comunicacion.pdf`](clase4_visualizacion_y_comunicacion.pdf) | [`clase4_visualizacion_y_comunicacion.txt`](clase4_visualizacion_y_comunicacion.txt) | [ver online](https://docs.google.com/presentation/d/1FakW8yBFTPR3xrv_9pebBB9w4ZogYBtB/edit) |

---

## 🎯 Relevancia para cada entregable

| Clase | Filminas | Entregable cubierto |
|---|---|---|
| **Clase 1** | Introducción · Probabilidad y Estadística | 📘 Parte 1 (independencia condicional para ejercicio 2c) |
| **Clase 2** | Datos y Modelos · Varias Variables | 📘 Parte 1 (estadística descriptiva, IQR, boxplot, correlación, densidad conjunta) |
| **Clase 3** | Estadísticos · Estimación | 📗 Parte 2 (estimadores, intervalos de confianza) |
| **Clase 4** | Test de Hipótesis · Visualización y Comunicación | 📗 Parte 2 (tests de hipótesis, comunicación de resultados) |

---

## 🔄 Cómo actualizar el mirror

Si las filminas se actualizan en Google Slides, se pueden regenerar con:

```bash
cd _site/filminas
# para cada id de presentación:
ID="1LtWnr73XHih-UjcRjRjfEGGPZATJED9X"
curl -sL "https://docs.google.com/presentation/d/${ID}/export/pdf" -o clase2_datos_y_modelos.pdf
curl -sL "https://docs.google.com/presentation/d/${ID}/export/txt" -o clase2_datos_y_modelos.txt
```

Los identificadores de cada filmina están en el [`README.md` de la materia](../../AnalisisyVisualizacion/README.md).
