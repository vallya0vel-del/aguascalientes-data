# Digital Divide in Aguascalientes â€” INEGI Census 2020
# Brecha Digital en Aguascalientes â€” Censo INEGI 2020

---

## English

### What is this project?

We analyze the **digital divide** in Aguascalientes â€” who has internet, a cellphone, a computer, TV, streaming, and who doesn't. Using the **INEGI 2020 Census**, we cover **2,022 real localities** across the state's **11 municipalities**.

The goal: identify the gap between urban and rural communities and determine which factors (education, population size, location) drive it. The project applies five stages of data science methodology, from raw data exploration to PCA dimensionality reduction and K-Means clustering.

### Key Findings

- **93.6% of localities** fall in the "basic telecom only" cluster (cellphone + TV, but limited internet/PC).
- **Only 6.4%** of localities have high connectivity â€” concentrated in the capital and conurbated zones.
- Internet penetration ranges from **~20% in villages** to **~74% in cities** (3.7Ã— gap).
- **Education (GRAPROES)** is the strongest predictor of digital access (r = 0.70 with PC ownership).
- Missing data is **MNAR** (censored by INEGI for privacy in small localities) â€” imputation was not appropriate for TIC variables.

### How to Run

```bash
python -X utf8 scripts/etapa3_datos_faltantes.py   # Stage 3 â€” Missing data analysis
python -X utf8 scripts/etapa4_visualizacion.py      # Stage 4 â€” Visualizations & EDA
python -X utf8 scripts/etapa5_pca_clustering.py     # Stage 5 â€” PCA + K-Means clustering

# Optional: regenerate HTML presentation guide
python -X utf8 scripts/_build_presentacion_v2.py
# Then open output/presentacion_guia_v2.html in a browser
```

**Requirements:** Python 3.8+, pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, geopandas.

### Project Stages

| Stage | Script | Description |
|---|---|---|
| 1 | `etapa1_comprension_datos.py` | Data comprehension â€” variable classification, data types, censoring detection |
| 2 | `etapa2_estadistica_descriptiva.py` | Descriptive statistics â€” means, medians, CVs, percentiles, VIF |
| 3 | `etapa3_datos_faltantes.py` | Missing data â€” MNAR mechanism, ICAD index construction |
| 4 | `etapa4_visualizacion.py` | EDA â€” histograms, boxplots, violin plots, geographic maps, correlation heatmaps |
| 5 | `etapa5_pca_clustering.py` | PCA (67.2% variance in 3 components) + K-Means k=2 (silhouette = 0.69) |

### Project Structure

```
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ conjunto_de_datos_iter_01CSV20.csv         # Main INEGI dataset (2,022 localities Ã— 286 vars)
â”‚   â””â”€â”€ diccionario_datos_iter_01CSV20.csv         # Data dictionary
â”œâ”€â”€ presentations/
â”‚   â””â”€â”€ Brecha digital en aguascalientes.pdf       # Final presentation slides
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ etapa1_comprension_datos.py
â”‚   â”œâ”€â”€ etapa2_estadistica_descriptiva.py
â”‚   â”œâ”€â”€ etapa2_reporte_html.py
â”‚   â”œâ”€â”€ etapa3_datos_faltantes.py
â”‚   â”œâ”€â”€ etapa4_visualizacion.py
â”‚   â”œâ”€â”€ etapa5_pca_clustering.py
â”‚   â””â”€â”€ _build_presentacion_v2.py                  # Builds output/presentacion_guia_v2.html
â””â”€â”€ output/                                         # Generated PNGs and HTML (gitignored)
```

---

## EspaÃ±ol

### Â¿De quÃ© trata este proyecto?

Analizamos la **brecha digital** en Aguascalientes â€” quiÃ©n tiene internet, celular, computadora, TV, streaming, y quiÃ©n no. Usando el **Censo INEGI 2020**, cubrimos **2,022 localidades reales** en los **11 municipios** del estado.

El objetivo: identificar la diferencia entre comunidades urbanas y rurales, y determinar quÃ© factores (educaciÃ³n, tamaÃ±o de localidad, ubicaciÃ³n geogrÃ¡fica) la explican. El proyecto aplica cinco etapas de metodologÃ­a de ciencia de datos, desde la exploraciÃ³n inicial hasta reducciÃ³n de dimensionalidad con PCA y agrupamiento K-Means.

### Hallazgos principales

- **El 93.6% de las localidades** pertenece al cluster "Solo telecom bÃ¡sica" (celular + TV, pero poco internet/PC).
- **Solo el 6.4%** tiene alta conectividad â€” concentrado en la capital y zonas conurbadas.
- El acceso a internet va del **~20% en localidades pequeÃ±as** al **~74% en ciudades** (brecha de 3.7Ã—).
- **La escolaridad (GRAPROES)** es el predictor mÃ¡s fuerte del acceso digital (r = 0.70 con PC).
- Los datos faltantes son **MNAR** (censurados por el INEGI por privacidad en localidades pequeÃ±as) â€” la imputaciÃ³n no era apropiada para las variables TIC.

### CÃ³mo ejecutar

```bash
python -X utf8 scripts/etapa3_datos_faltantes.py   # Etapa 3 â€” AnÃ¡lisis de datos faltantes
python -X utf8 scripts/etapa4_visualizacion.py      # Etapa 4 â€” Visualizaciones y EDA
python -X utf8 scripts/etapa5_pca_clustering.py     # Etapa 5 â€” PCA + Clustering K-Means

# Opcional: regenerar la guÃ­a HTML de presentaciÃ³n
python -X utf8 scripts/_build_presentacion_v2.py
# Luego abrir output/presentacion_guia_v2.html en el navegador
```

**Requisitos:** Python 3.8+, pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, geopandas.

### Etapas del proyecto

| Etapa | Script | DescripciÃ³n |
|---|---|---|
| 1 | `etapa1_comprension_datos.py` | ComprensiÃ³n de datos â€” clasificaciÃ³n de variables, tipos, detecciÃ³n de censura |
| 2 | `etapa2_estadistica_descriptiva.py` | EstadÃ­stica descriptiva â€” medias, medianas, CVs, percentiles, VIF |
| 3 | `etapa3_datos_faltantes.py` | Datos faltantes â€” mecanismo MNAR, construcciÃ³n del Ã­ndice ICAD |
| 4 | `etapa4_visualizacion.py` | EDA â€” histogramas, boxplots, violin plots, mapas geogrÃ¡ficos, heatmaps de correlaciÃ³n |
| 5 | `etapa5_pca_clustering.py` | PCA (67.2% varianza en 3 componentes) + K-Means k=2 (silueta = 0.69) |

### Estructura del proyecto

```
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ conjunto_de_datos_iter_01CSV20.csv         # Dataset principal INEGI (2,022 loc Ã— 286 vars)
â”‚   â””â”€â”€ diccionario_datos_iter_01CSV20.csv         # Diccionario de datos
â”œâ”€â”€ presentations/
â”‚   â””â”€â”€ Brecha digital en aguascalientes.pdf       # Diapositivas de la presentaciÃ³n final
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ etapa1_comprension_datos.py
â”‚   â”œâ”€â”€ etapa2_estadistica_descriptiva.py
â”‚   â”œâ”€â”€ etapa2_reporte_html.py
â”‚   â”œâ”€â”€ etapa3_datos_faltantes.py
â”‚   â”œâ”€â”€ etapa4_visualizacion.py
â”‚   â”œâ”€â”€ etapa5_pca_clustering.py
â”‚   â””â”€â”€ _build_presentacion_v2.py                  # Genera output/presentacion_guia_v2.html
â””â”€â”€ output/                                         # PNGs y HTML generados (gitignored)
```

