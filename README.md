# Digital Divide in Aguascalientes — INEGI Census 2020
# Brecha Digital en Aguascalientes — Censo INEGI 2020

---

## English

### What is this project?

We analyze the **digital divide** in Aguascalientes — who has internet, a cellphone, a computer, TV, streaming, and who doesn’t. Using the **INEGI 2020 Census**, we cover **2,022 real localities** across the state’s **11 municipalities**.

The goal: identify the gap between urban and rural communities and determine which factors (education, population size, location) drive it. The project applies five stages of data science methodology, from raw data exploration to PCA dimensionality reduction and K-Means clustering.

### Key Findings

- **93.6% of localities** fall in the “basic telecom only” cluster (cellphone + TV, but limited internet/PC).
- **Only 6.4%** of localities have high connectivity — concentrated in the capital and conurbated zones.
- Internet penetration ranges from **~20% in villages** to **~74% in cities** (3.7× gap).
- **Education (GRAPROES)** is the strongest predictor of digital access (r = 0.70 with PC ownership).
- Missing data is **MNAR** (censored by INEGI for privacy in small localities) — imputation was not appropriate for TIC variables.

### How to Run

```bash
python -X utf8 scripts/etapa3_datos_faltantes.py   # Stage 3 — Missing data analysis
python -X utf8 scripts/etapa4_visualizacion.py      # Stage 4 — Visualizations & EDA
python -X utf8 scripts/etapa5_pca_clustering.py     # Stage 5 — PCA + K-Means clustering

# Optional: regenerate HTML presentation guide
python -X utf8 scripts/_build_presentacion_v2.py
# Then open output/presentacion_guia_v2.html in a browser
```

**Requirements:** Python 3.8+, pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, geopandas.

### Project Stages

| Stage | Script | Description |
|---|---|---|
| 1 | `etapa1_comprension_datos.py` | Data comprehension — variable classification, data types, censoring detection |
| 2 | `etapa2_estadistica_descriptiva.py` | Descriptive statistics — means, medians, CVs, percentiles, VIF |
| 3 | `etapa3_datos_faltantes.py` | Missing data — MNAR mechanism, ICAD index construction |
| 4 | `etapa4_visualizacion.py` | EDA — histograms, boxplots, violin plots, geographic maps, correlation heatmaps |
| 5 | `etapa5_pca_clustering.py` | PCA (67.2% variance in 3 components) + K-Means k=2 (silhouette = 0.69) |

### Project Structure

```
├── data/
│   ├── conjunto_de_datos_iter_01CSV20.csv         # Main INEGI dataset (2,022 localities × 286 vars)
│   └── diccionario_datos_iter_01CSV20.csv         # Data dictionary
├── presentations/
│   └── Brecha digital en aguascalientes.pdf       # Final presentation slides
├── scripts/
│   ├── etapa1_comprension_datos.py
│   ├── etapa2_estadistica_descriptiva.py
│   ├── etapa2_reporte_html.py
│   ├── etapa3_datos_faltantes.py
│   ├── etapa4_visualizacion.py
│   ├── etapa5_pca_clustering.py
│   └── _build_presentacion_v2.py                  # Builds output/presentacion_guia_v2.html
└── output/                                         # Generated PNGs and HTML (gitignored)
```

---

## Español

### ¿De qué trata este proyecto?

Analizamos la **brecha digital** en Aguascalientes — quién tiene internet, celular, computadora, TV, streaming, y quién no. Usando el **Censo INEGI 2020**, cubrimos **2,022 localidades reales** en los **11 municipios** del estado.

El objetivo: identificar la diferencia entre comunidades urbanas y rurales, y determinar qué factores (educación, tamaño de localidad, ubicación geográfica) la explican. El proyecto aplica cinco etapas de metodología de ciencia de datos, desde la exploración inicial hasta reducción de dimensionalidad con PCA y agrupamiento K-Means.

### Hallazgos principales

- **El 93.6% de las localidades** pertenece al cluster “Solo telecom básica” (celular + TV, pero poco internet/PC).
- **Solo el 6.4%** tiene alta conectividad — concentrado en la capital y zonas conurbadas.
- El acceso a internet va del **~20% en localidades pequeñas** al **~74% en ciudades** (brecha de 3.7×).
- **La escolaridad (GRAPROES)** es el predictor más fuerte del acceso digital (r = 0.70 con PC).
- Los datos faltantes son **MNAR** (censurados por el INEGI por privacidad en localidades pequeñas) — la imputación no era apropiada para las variables TIC.

### Cómo ejecutar

```bash
python -X utf8 scripts/etapa3_datos_faltantes.py   # Etapa 3 — Análisis de datos faltantes
python -X utf8 scripts/etapa4_visualizacion.py      # Etapa 4 — Visualizaciones y EDA
python -X utf8 scripts/etapa5_pca_clustering.py     # Etapa 5 — PCA + Clustering K-Means

# Opcional: regenerar la guía HTML de presentación
python -X utf8 scripts/_build_presentacion_v2.py
# Luego abrir output/presentacion_guia_v2.html en el navegador
```

**Requisitos:** Python 3.8+, pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, geopandas.

### Etapas del proyecto

| Etapa | Script | Descripción |
|---|---|---|
| 1 | `etapa1_comprension_datos.py` | Comprensión de datos — clasificación de variables, tipos, detección de censura |
| 2 | `etapa2_estadistica_descriptiva.py` | Estadística descriptiva — medias, medianas, CVs, percentiles, VIF |
| 3 | `etapa3_datos_faltantes.py` | Datos faltantes — mecanismo MNAR, construcción del índice ICAD |
| 4 | `etapa4_visualizacion.py` | EDA — histogramas, boxplots, violin plots, mapas geográficos, heatmaps de correlación |
| 5 | `etapa5_pca_clustering.py` | PCA (67.2% varianza en 3 componentes) + K-Means k=2 (silueta = 0.69) |

### Estructura del proyecto

```
├── data/
│   ├── conjunto_de_datos_iter_01CSV20.csv         # Dataset principal INEGI (2,022 loc × 286 vars)
│   └── diccionario_datos_iter_01CSV20.csv         # Diccionario de datos
├── presentations/
│   └── Brecha digital en aguascalientes.pdf       # Diapositivas de la presentación final
├── scripts/
│   ├── etapa1_comprension_datos.py
│   ├── etapa2_estadistica_descriptiva.py
│   ├── etapa2_reporte_html.py
│   ├── etapa3_datos_faltantes.py
│   ├── etapa4_visualizacion.py
│   ├── etapa5_pca_clustering.py
│   └── _build_presentacion_v2.py                  # Genera output/presentacion_guia_v2.html
└── output/                                         # PNGs y HTML generados (gitignored)
```
