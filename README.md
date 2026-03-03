# Acceso Digital en Aguascalientes — Censo INEGI 2020

## What is this project?

We analyze how connected the people of Aguascalientes are — who has internet, a cellphone, a computer, TV, streaming — and who doesn't. We use the **2020 Census** from INEGI (Mexico's statistics institute) which covers **2,022 real localities** across the state's **11 municipalities**.

The goal: find the **digital divide** — the gap between urban and rural communities — and identify which factors (education, population size, location) explain it.

---

## How to run

```bash
# Stage 1 — Data comprehension
python -X utf8 scripts/etapa1_comprension_datos.py

# Stage 2 — Descriptive statistics + heatmaps
python -X utf8 scripts/etapa2_estadistica_descriptiva.py

# Stage 2 — HTML report (for presentation / PDF export)
python -X utf8 scripts/etapa2_reporte_html.py
# Then open output/etapa2_reporte.html in a browser
```

**Requirements:** Python 3.8+, pandas, numpy, matplotlib, seaborn.

---

## Stage 1 — Data Comprehension

### What we did

1. **Read both files** — the main dataset (2,058 rows × 286 columns) and the data dictionary that explains what each column means.
2. **Mapped every column code to its meaning** — e.g. `VPH_INTER` = "Homes with Internet."
3. **Classified all 286 variables** into 6 categories, highlighting the 13 digital access variables.
4. **Detected data problems** — wrong data types, censored values, and special rows.

### Table: Variable Classification

| Category | # Variables | What it covers |
|---|---|---|
| Geographic | 10 | Location codes, lat/lon, municipality names |
| Demographic | 153 | Population by age, gender, ethnicity, disability, religion |
| Education | 42 | School attendance, literacy, average schooling |
| Economic | 22 | Employment, social security |
| Housing | 46 | Dwelling conditions, services (water, electricity, drainage) |
| **Digital Access (TIC)** ★ | **13** | **Radio, TV, PC, phone, cellphone, internet, streaming, gaming, and "without" indicators** |

**Insight:** Our focus is the 13 TIC (Information and Communication Technology) variables. They split into two groups: **access** (Radio, TV, PC, Telephone, Cellphone, Internet, Pay TV, Streaming, Videogames) and **lack of access** (no radio/TV, no phone/cell, no PC/Internet, no TIC at all).

### Table: Data Problems Detected

| Problem | What we found | Why it matters |
|---|---|---|
| `*` values (censored) | 1,072 rows per column (~52%) | INEGI hides data when a locality has ≤2 homes to protect privacy. These aren't random — they're mostly tiny rural localities. |
| Wrong data types | 274 columns read as text | Because of the `*` symbols, pandas thinks numeric columns are text. We convert them. |
| Categorical as numeric | ENTIDAD, MUN, LOC, TAMLOC | These are codes/categories (e.g. municipality 1 = Aguascalientes), not numbers to average. |
| Special rows | 36 rows are totals/aggregates | Rows with LOC=0 (municipal totals), LOC=9998, LOC=9999 must be excluded to avoid double-counting. |

**Insight:** The 52% censoring is NOT random — it's concentrated in the smallest, most rural localities. This is important for Stage 3 (missing data analysis).

### Table: Digital Access Overview by Municipality

| Municipality | Homes with Internet | % |
|---|---|---|
| Aguascalientes (capital) | 159,785 | 69.3% |
| San Fco. de los Romo | 8,389 | 62.3% |
| Jesús María | 15,966 | 55.5% |
| Pabellón de Arteaga | 7,206 | 50.7% |
| Rincón de Romos | 6,765 | 43.9% |
| Asientos | 5,025 | 39.1% |
| Cosío | 1,224 | 38.1% |
| Calvillo | 5,685 | 36.7% |
| San José de Gracia | 977 | 36.3% |
| Tepezalá | 2,025 | 35.2% |
| **El Llano** | **1,605** | **25.9%** |

**Insight:** There's a **2.7x gap** between the capital (69%) and El Llano (26%). Urban municipalities clearly have more internet access. This pattern repeats for all digital technologies.

---

## Stage 2 — Descriptive Statistics

### What we did

1. Filtered to **2,022 real localities** (excluded totals and aggregate rows).
2. Created **13 rate variables** — instead of raw counts, we calculated the *proportion* of homes with each technology (e.g. homes with internet ÷ total homes = internet rate).
3. Calculated all statistics **manually** (no shortcuts) — mean, median, standard deviation, coefficient of variation, skewness, kurtosis, percentiles.
4. Analyzed categorical variables (municipality, locality size) with frequencies and Shannon entropy.
5. Built a **correlation matrix** and **collinearity analysis (VIF)**.
6. Generated **heatmaps** as PNG files and an **HTML report**.

### Table 1a: Demographic Context

Shows the basic profile of localities in Aguascalientes.

| What to highlight | Interpretation |
|---|---|
| **POBTOT** (Population) | Average locality has ~700 people, but median is only 34 — most localities are tiny, a few are huge cities. |
| **GRAPROES** (Avg. schooling in years) | Average ~6.1 years (primary school). Higher schooling = more digital access. |
| **VIVPAR_HAB** (Inhabited homes) | Average ~180, median ~9. Same pattern — very skewed toward small localities. |
| **CV% > 300%** for population/homes | Enormous variation — the state mixes tiny ranches with a capital of 900K+ people. |

**Slide focus:** "Most localities in Aguascalientes are very small — the median has only 34 people and 9 homes."

### Table 1b: Digital Access — Absolute Counts

Shows raw numbers (how many homes have each technology per locality).

| Variable | What to notice |
|---|---|
| **VPH_CEL** (Cellphone) | Highest average count. Cellphones are everywhere. |
| **VPH_TV** (Television) | Second most common technology. |
| **VPH_INTER** (Internet) | Lower than cellphone and TV — not yet universal. |
| **VPH_PC** (Computer) | Even lower. Computers are a luxury in small towns. |
| **VPH_SINTIC** (No TIC at all) | Very low average — almost every home has *something*. |
| **High skewness (>5)** | All variables are heavily skewed right — a few big cities drive the count up. |

**Slide focus:** "Cellphones dominate, but internet and computers lag behind — especially outside the capital."

### Table 1c: Digital Access — Rates (proportions)

This is the **most important table** — it shows the *percentage* of homes with each technology, removing the effect of locality size.

| Variable | Average rate | What it means |
|---|---|---|
| **TASA_CEL** | 92.8% | Almost every home with data has a cellphone. |
| **TASA_TV** | 78.1% | TV is widespread but not universal in rural areas. |
| **TASA_RADIO** | 53.2% | Radio is declining — half of homes still have one. |
| **TASA_INTER** | 33.2% | Only 1 in 3 homes has internet (per locality avg). |
| **TASA_PC** | 21.9% | Only 1 in 5 homes has a computer/laptop/tablet. |
| **TASA_SPMVPI** | 14.3% | Streaming (Netflix etc.) is still a luxury. |
| **TASA_CVJ** | 7.3% | Videogame consoles are rare outside cities. |
| **TASA_SINCINT** | 59.1% | **59% of homes lack both computer and internet.** |
| **TASA_SINTIC** | 1.4% | Very few homes have literally zero technology. |
| **CV% > 50% for all** | High variation between localities. |

**Slide focus:** "93% have cellphones, but only 33% have internet and 22% have a computer. The digital divide is about *quality* of access, not just *any* access."

### Table 2: Percentiles

Shows how rates are distributed across localities.

| What to read | Interpretation |
|---|---|
| **P25 of TASA_INTER = near 0** | The bottom quarter of localities have almost no internet. |
| **P50 (median) of TASA_INTER ≈ 0.20** | Half of all localities have ≤20% internet penetration. |
| **P75 of TASA_CEL ≈ 1.00** | 75% of localities have cellphones in all homes. |
| **IQR** (P75 − P25) | Large IQR = wide spread. Internet has the widest relative gap. |

**Slide focus:** "Half of localities have internet in less than 20% of homes. The median tells the real story — not the average."

### Table 3: Categorical — Municipality (MUN)

| What to highlight | Numbers |
|---|---|
| 11 municipalities | Aguascalientes capital has ~40% of all localities. |
| Shannon entropy = 3.13 bits | Close to max (3.46) = localities are reasonably spread across municipalities. |
| **Moda = Aguascalientes (1)** | The capital municipality dominates. |

**Slide focus:** "Localities are spread across all 11 municipalities, but Aguascalientes capital concentrates the most."

### Table 3: Categorical — Locality Size (TAMLOC)

| What to highlight | Numbers |
|---|---|
| 11 size categories present | From <250 people to 500K+ |
| **86% are category 1** (<250 hab.) | The vast majority of localities are tiny. |
| Shannon entropy = 1.42 bits | Low entropy = very concentrated in one category. |

**Slide focus:** "86% of localities have fewer than 250 inhabitants. Aguascalientes is a state of small rural communities."

### Table 3: Digital Access by Locality Size (TAMLOC)

This is where the **digital divide becomes crystal clear**.

| Locality size | Internet rate | Cellphone rate | PC rate |
|---|---|---|---|
| 1–249 people | ~20% | ~89% | ~14% |
| 2,500–4,999 | ~53% | ~97% | ~38% |
| 15,000–29,999 | ~66% | ~98% | ~51% |
| 100,000+ | ~74% | ~99% | ~59% |

**Insight:** Cellphones are universal (89%+ even in the smallest villages), but internet goes from 20% to 74% — a **3.7x gap**. Computers go from 14% to 59%. The bigger the town, the more connected it is.

**Slide focus:** "The digital divide is not about cellphones — it's about internet and computers. Small towns are left behind."

### Table 4a: Correlation Heatmap

The heatmap shows how digital access variables relate to each other. Numbers range from −1 (opposite) to +1 (move together).

| Strongest positive correlations | r value | Meaning |
|---|---|---|
| TV ↔ Cellphone | 0.84 | If a locality has TV, it has cellphones. |
| Streaming ↔ Videogames | 0.80 | Both are "advanced entertainment" — they go together. |
| Radio ↔ Cellphone | 0.78 | Basic technologies cluster together. |
| PC ↔ Streaming | 0.74 | Computer + streaming = "digital sophistication." |

| Strongest negative correlations | r value | Meaning |
|---|---|---|
| Internet ↔ No PC/Internet | -0.87 | Obvious inverse — more internet means fewer homes *without* it. |
| Cellphone ↔ No Telephone | -0.82 | Same logic. |

**Insight:** There are two clusters: a **"basic access" cluster** (cellphone, TV, radio) and an **"advanced access" cluster** (internet, PC, streaming, videogames). The advanced cluster is what separates urban from rural.

**Slide focus:** "Technologies cluster into 'basic' (cell, TV) and 'advanced' (internet, PC, streaming). The gap is in the advanced group."

### Table 4c: Correlation with Socioeconomic Variables

| Most interesting finding | r value | Meaning |
|---|---|---|
| **GRAPROES ↔ PC** | 0.70 | Education is the strongest predictor of having a computer. |
| **GRAPROES ↔ Streaming** | 0.64 | More educated = more streaming adoption. |
| **GRAPROES ↔ Internet** | 0.53 | Education correlates with internet access. |
| POBTOT ↔ all | 0.20–0.30 | Population size matters, but education matters more. |

**Slide focus:** "Education level is the #1 predictor of digital access — stronger than population size."

### Table 5: Collinearity (VIF)

VIF tells us which variables contain redundant information. A VIF ≥ 10 means "this variable is almost a copy of others."

| Variable | VIF | What it means |
|---|---|---|
| Cellphone | 21.07 | Heavily redundant — if you know TV and radio, you can predict cellphone. |
| No PC/Internet | 17.37 | The inverse of Internet — remove one. |
| Internet | 14.27 | Overlaps with PC, streaming, and cellphone. |
| TV | 9.00 | High but not critical. |
| Others | < 5 | Acceptable. |

**Insight:** For future modeling (Stage 3–4), we should NOT use all 13 variables simultaneously. We should either pick a subset or create a single "digital access index" combining them.

**Slide focus:** "Many variables overlap. For models, we need to simplify — use 4–5 key variables, or create a single digital access score."

### Heatmaps Generated

Two PNG files are saved in `output/`:

1. **`heatmap_correlacion_acceso_digital.png`** — Color-coded correlation matrix. Blue = positive, red = negative. Darker = stronger.
2. **`heatmap_acceso_digital_municipio.png`** — Access rates by municipality. Darker blue = higher percentage. Immediately shows Aguascalientes capital as the "hotspot" and El Llano as the "coldspot."

### HTML Report

Run `python -X utf8 scripts/etapa2_reporte_html.py` to generate `output/etapa2_reporte.html` — a self-contained file with all tables, charts, and KPI cards. Open it in Chrome/Edge and press **Ctrl+P** to export as PDF for the presentation.

---

## Key Takeaways (for the presentation)

1. **Aguascalientes is a state of small communities** — 86% of localities have <250 people.
2. **Cellphones are universal** (93%), but **internet reaches only 33%** and **computers only 22%** on average per locality.
3. **The digital divide is urban vs. rural** — internet goes from 20% in tiny villages to 74% in cities.
4. **Education is the strongest predictor** of digital access (r = 0.70 with PC ownership).
5. **52% of data is censored** by INEGI (privacy protection for small localities) — this is NOT random and needs special handling in Stage 3.
6. **For future models**, reduce the 13 digital variables to avoid redundancy (VIF analysis shows severe overlap).

---

## Project Structure

```
├── data/
│   ├── conjunto_de_datos_iter_01CSV20.csv    # Main INEGI dataset (2,058 × 286)
│   └── diccionario_datos_iter_01CSV20.csv    # Data dictionary
├── instructions/
│   └── RETO Tecnologico de Monterrey.pptx    # Project brief
├── scripts/
│   ├── etapa1_comprension_datos.py           # Stage 1: Data comprehension
│   ├── etapa2_estadistica_descriptiva.py     # Stage 2: Descriptive stats + heatmaps
│   └── etapa2_reporte_html.py                # Stage 2: HTML report generator
├── output/                                    # Generated files (gitignored)
│   ├── heatmap_correlacion_acceso_digital.png
│   ├── heatmap_acceso_digital_municipio.png
│   └── etapa2_reporte.html
└── README.md
```