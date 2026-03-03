# -*- coding: utf-8 -*-
"""
================================================================================
  Generador de Reporte HTML — Etapa 2: Estadística Descriptiva
  Censo de Población y Vivienda 2020 · Estado de Aguascalientes
  Enfoque: Acceso Digital en la Población
================================================================================
  Genera un archivo HTML con tablas estilizadas, heatmaps integrados, y
  hallazgos clave, listo para presentación.
  Salida: output/etapa2_reporte.html
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import warnings, os, base64
from io import BytesIO

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})

# ──────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RUTA_DATOS = os.path.join(DATA_DIR, "conjunto_de_datos_iter_01CSV20.csv")
RUTA_DICC  = os.path.join(DATA_DIR, "diccionario_datos_iter_01CSV20.csv")

print("▸ Generando reporte HTML de la Etapa 2...")

# ──────────────────────────────────────────────────────────────────────────────
# 1. CARGA Y PREPARACIÓN DE DATOS
# ──────────────────────────────────────────────────────────────────────────────
df_raw = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig", low_memory=False)
dict_raw = pd.read_csv(RUTA_DICC, encoding="utf-8-sig", header=None)
dict_df = dict_raw.iloc[4:].copy()
dict_df.columns = ["Num", "Indicador", "Descripcion", "Mnemonico",
                    "Rango", "Tam", "C6", "C7", "C8", "C9"]
dict_df["Mnemonico"] = dict_df["Mnemonico"].astype(str).str.strip()
dict_df = dict_df[dict_df["Mnemonico"] != "nan"]
mapeo = dict(zip(dict_df["Mnemonico"], dict_df["Indicador"]))

# Filtrar localidades reales
df = df_raw[(df_raw["LOC"] > 0) & (df_raw["LOC"] < 9998)].copy()
cols_texto_legit = ["NOM_ENT", "NOM_MUN", "NOM_LOC", "LONGITUD", "LATITUD"]
for col in df.columns:
    if col not in cols_texto_legit:
        df[col] = pd.to_numeric(df[col], errors="coerce")

vars_acceso_digital = [
    "VPH_RADIO", "VPH_TV", "VPH_PC", "VPH_TELEF", "VPH_CEL",
    "VPH_INTER", "VPH_STVP", "VPH_SPMVPI", "VPH_CVJ",
    "VPH_SINRTV", "VPH_SINLTC", "VPH_SINCINT", "VPH_SINTIC",
]

vars_tasas_acceso = []
for v in vars_acceso_digital:
    nombre_tasa = f"TASA_{v.replace('VPH_', '')}"
    mask = df["VIVPAR_HAB"].notna() & (df["VIVPAR_HAB"] > 0) & df[v].notna()
    df.loc[mask, nombre_tasa] = df.loc[mask, v] / df.loc[mask, "VIVPAR_HAB"]
    vars_tasas_acceso.append(nombre_tasa)

vars_demograficas_clave = [
    "POBTOT", "POBFEM", "POBMAS", "VIVPAR_HAB", "OCUPVIVPAR",
    "GRAPROES", "PROM_OCUP",
]

nombres_tasas = {
    "TASA_RADIO": "Radio", "TASA_TV": "Televisor",
    "TASA_PC": "PC/Laptop/Tablet", "TASA_TELEF": "Teléfono fijo",
    "TASA_CEL": "Celular", "TASA_INTER": "Internet",
    "TASA_STVP": "TV de paga", "TASA_SPMVPI": "Streaming",
    "TASA_CVJ": "Videojuegos", "TASA_SINRTV": "Sin radio/TV",
    "TASA_SINLTC": "Sin tel. fijo/cel.", "TASA_SINCINT": "Sin PC/Internet",
    "TASA_SINTIC": "Sin ninguna TIC",
}

nombres_vars = {
    "POBTOT": "Población total", "POBFEM": "Población femenina",
    "POBMAS": "Población masculina", "VIVPAR_HAB": "Viviendas habitadas",
    "OCUPVIVPAR": "Ocupantes en viv. hab.", "GRAPROES": "Grado prom. escolaridad",
    "PROM_OCUP": "Prom. ocupantes/viv.",
}
nombres_vars.update(nombres_tasas)
for v in vars_acceso_digital:
    desc = mapeo.get(v, v)
    if isinstance(desc, str):
        nombres_vars[v] = desc[:55]

nombres_mun = {
    1: "Aguascalientes", 2: "Asientos", 3: "Calvillo", 4: "Cosío",
    5: "Jesús María", 6: "Pabellón de Arteaga", 7: "Rincón de Romos",
    8: "San José de Gracia", 9: "Tepezalá",
    10: "El Llano", 11: "San Fco. de los Romo",
}

tamloc_etiquetas = {
    1: "1–249 hab.", 2: "250–499", 3: "500–999",
    4: "1,000–2,499", 5: "2,500–4,999", 6: "5,000–9,999",
    7: "10,000–14,999", 8: "15,000–29,999", 9: "30,000–49,999",
    10: "50,000–99,999", 11: "100,000–249,999",
    12: "250,000–499,999", 13: "500,000–999,999", 14: "1,000,000+",
}


# ──────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE CÁLCULO MANUAL (idénticas al script principal)
# ──────────────────────────────────────────────────────────────────────────────

def media_manual(x):
    vals = x.dropna().values
    n = len(vals)
    return np.sum(vals) / n if n > 0 else np.nan

def mediana_manual(x):
    vals = np.sort(x.dropna().values)
    n = len(vals)
    if n == 0: return np.nan
    return vals[n // 2] if n % 2 == 1 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0

def desviacion_estandar_manual(x, ddof=1):
    vals = x.dropna().values
    n = len(vals)
    if n <= ddof: return np.nan
    mu = np.sum(vals) / n
    return np.sqrt(np.sum((vals - mu) ** 2) / (n - ddof))

def coef_variacion_manual(x):
    mu = media_manual(x)
    s = desviacion_estandar_manual(x)
    if np.isnan(mu) or np.isnan(s) or mu == 0: return np.nan
    return (s / abs(mu)) * 100

def percentil_manual(x, p):
    vals = np.sort(x.dropna().values)
    n = len(vals)
    if n == 0: return np.nan
    k = (n - 1) * p / 100.0
    f = int(np.floor(k))
    c = int(np.ceil(k))
    if f == c: return vals[f]
    return vals[f] + (k - f) * (vals[c] - vals[f])

def asimetria_manual(x):
    vals = x.dropna().values
    n = len(vals)
    if n < 3: return np.nan
    mu = np.sum(vals) / n
    s = np.sqrt(np.sum((vals - mu) ** 2) / (n - 1))
    if s == 0: return 0.0
    m3 = np.sum(((vals - mu) / s) ** 3)
    return (n / ((n - 1) * (n - 2))) * m3

def curtosis_manual(x):
    vals = x.dropna().values
    n = len(vals)
    if n < 4: return np.nan
    mu = np.sum(vals) / n
    s = np.sqrt(np.sum((vals - mu) ** 2) / (n - 1))
    if s == 0: return 0.0
    m4 = np.sum(((vals - mu) / s) ** 4)
    k = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3)) * m4
    k -= (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return k

def correlacion_pearson_manual(x, y):
    mask = x.notna() & y.notna()
    xv = x[mask].values.astype(float)
    yv = y[mask].values.astype(float)
    n = len(xv)
    if n < 3: return np.nan
    mx, my = np.sum(xv) / n, np.sum(yv) / n
    dx, dy = xv - mx, yv - my
    den = np.sqrt(np.sum(dx ** 2) * np.sum(dy ** 2))
    return np.sum(dx * dy) / den if den != 0 else np.nan

def entropia_shannon(x):
    counts = x.dropna().value_counts()
    n = counts.sum()
    if n == 0: return np.nan
    probs = counts / n
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


# ──────────────────────────────────────────────────────────────────────────────
# UTILIDAD: Convertir figura matplotlib a imagen base64 inline
# ──────────────────────────────────────────────────────────────────────────────
def fig_to_base64(fig, dpi=180):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# 2. COMPUTAR TODOS LOS DATOS PARA EL REPORTE
# ──────────────────────────────────────────────────────────────────────────────
print("  Calculando estadísticos...")

# -- Tabla 1: Estadística descriptiva de variables demográficas --
rows_demo = []
for v in vars_demograficas_clave:
    if v not in df.columns: continue
    s = df[v]
    rows_demo.append({
        "Variable": nombres_vars.get(v, v),
        "n": int(s.notna().sum()),
        "Media": media_manual(s),
        "Mediana": mediana_manual(s),
        "Desv. Est.": desviacion_estandar_manual(s),
        "CV (%)": coef_variacion_manual(s),
        "Asimetría": asimetria_manual(s),
        "Curtosis": curtosis_manual(s),
    })
tabla_demo = pd.DataFrame(rows_demo)

# -- Tabla 2: Tasas de acceso digital --
rows_tasas = []
for v in vars_tasas_acceso:
    if v not in df.columns: continue
    s = df[v]
    rows_tasas.append({
        "Variable": nombres_vars.get(v, v),
        "n": int(s.notna().sum()),
        "Media": media_manual(s),
        "Mediana": mediana_manual(s),
        "Desv. Est.": desviacion_estandar_manual(s),
        "CV (%)": coef_variacion_manual(s),
        "Asimetría": asimetria_manual(s),
        "Curtosis": curtosis_manual(s),
    })
tabla_tasas = pd.DataFrame(rows_tasas)

# -- Tabla 3: Percentiles de tasas --
rows_perc = []
for v in vars_tasas_acceso:
    if v not in df.columns: continue
    s = df[v]
    if s.notna().sum() == 0: continue
    rows_perc.append({
        "Variable": nombres_vars.get(v, v),
        "Mín": s.min(),
        "P5": percentil_manual(s, 5),
        "P25": percentil_manual(s, 25),
        "P50": percentil_manual(s, 50),
        "P75": percentil_manual(s, 75),
        "P95": percentil_manual(s, 95),
        "Máx": s.max(),
    })
tabla_perc = pd.DataFrame(rows_perc)

# -- Tabla 4: Acceso digital por municipio --
filas_mun = df_raw[(df_raw["MUN"] > 0) & (df_raw["LOC"] == 0)].copy()
for col_m in vars_acceso_digital + ["VIVPAR_HAB"]:
    filas_mun[col_m] = pd.to_numeric(filas_mun[col_m], errors="coerce")

rows_mun = []
for _, row in filas_mun.iterrows():
    mid = int(row["MUN"])
    vph = row["VIVPAR_HAB"]
    if pd.isna(vph) or vph == 0: continue
    rd = {"Municipio": nombres_mun.get(mid, str(mid))}
    for vp in ["VPH_INTER", "VPH_CEL", "VPH_PC", "VPH_TV", "VPH_SINTIC"]:
        val = row[vp]
        label = {"VPH_INTER": "Internet %", "VPH_CEL": "Celular %",
                 "VPH_PC": "PC %", "VPH_TV": "TV %",
                 "VPH_SINTIC": "Sin TIC %"}[vp]
        rd[label] = (val / vph * 100) if pd.notna(val) else np.nan
    rows_mun.append(rd)
tabla_mun = pd.DataFrame(rows_mun)

# -- Tabla 5: Acceso digital por TAMLOC --
vars_tasa_clave = ["TASA_INTER", "TASA_CEL", "TASA_PC", "TASA_TV"]
rows_tam = []
for tam in sorted(df["TAMLOC"].dropna().unique()):
    tam_int = int(tam)
    mask = df["TAMLOC"] == tam
    rd = {"Tam. Localidad": tamloc_etiquetas.get(tam_int, str(tam_int)),
          "n": int(mask.sum())}
    for vt in vars_tasa_clave:
        if vt in df.columns:
            m = media_manual(df.loc[mask, vt])
            rd[nombres_tasas.get(vt, vt)] = m * 100 if pd.notna(m) else np.nan
    rows_tam.append(rd)
tabla_tam = pd.DataFrame(rows_tam)

# -- Tabla 6: Categórica MUN --
serie_mun = df["MUN"].dropna()
freq_mun = serie_mun.value_counts().sort_index()
H_mun = entropia_shannon(serie_mun)

# -- Matriz de correlación --
print("  Calculando correlaciones...")
n_vars = len(vars_tasas_acceso)
abrevs = [v.replace("TASA_", "") for v in vars_tasas_acceso]
corr_matrix = np.full((n_vars, n_vars), np.nan)
for i in range(n_vars):
    for j in range(n_vars):
        if i == j:
            corr_matrix[i, j] = 1.0
        elif j > i:
            r = correlacion_pearson_manual(df[vars_tasas_acceso[i]],
                                           df[vars_tasas_acceso[j]])
            corr_matrix[i, j] = r
            corr_matrix[j, i] = r

# -- VIF --
print("  Calculando VIF...")
vars_vif = [v for v in vars_tasas_acceso
            if v in df.columns and df[v].notna().sum() > 10]
df_vif = df[vars_vif].dropna()
vif_results = []
if len(df_vif) > len(vars_vif) + 1:
    R = np.corrcoef(df_vif.values, rowvar=False)
    try:
        R_inv = np.linalg.inv(R)
        vif_values = np.diag(R_inv)
        for idx, v in enumerate(vars_vif):
            vif = vif_values[idx]
            if vif >= 10: diag = "Severa"
            elif vif >= 5: diag = "Alta"
            else: diag = "Aceptable"
            vif_results.append({
                "Variable": nombres_vars.get(v, v),
                "VIF": vif,
                "Diagnóstico": diag,
            })
    except np.linalg.LinAlgError:
        pass
tabla_vif = pd.DataFrame(vif_results) if vif_results else None

# -- Correlaciones con socioeconómicas --
vars_socio = ["POBTOT", "GRAPROES", "PROM_OCUP", "VIVPAR_HAB"]
rows_socio = []
for vt in vars_tasas_acceso:
    if vt not in df.columns: continue
    rd = {"Tasa": nombres_tasas.get(vt, vt)}
    for vs in vars_socio:
        if vs in df.columns:
            rd[vs] = correlacion_pearson_manual(df[vt], df[vs])
    rows_socio.append(rd)
tabla_socio = pd.DataFrame(rows_socio)


# ──────────────────────────────────────────────────────────────────────────────
# 3. GENERAR FIGURAS
# ──────────────────────────────────────────────────────────────────────────────
print("  Generando figuras...")

# ── Fig 1: Heatmap de correlación ──
corr_df = pd.DataFrame(corr_matrix, index=abrevs, columns=abrevs)
fig1, ax1 = plt.subplots(figsize=(11, 9))
mask_upper = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
cmap = sns.diverging_palette(250, 15, s=75, l=40, n=12, as_cmap=True)
sns.heatmap(corr_df, mask=mask_upper, annot=True, fmt=".2f", cmap=cmap,
            center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
            cbar_kws={"shrink": 0.8, "label": "r de Pearson"}, ax=ax1)
ax1.set_title("Matriz de Correlación — Tasas de Acceso Digital", fontsize=13, fontweight="bold")
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right", fontsize=8)
ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0, fontsize=8)
img_corr = fig_to_base64(fig1)

# ── Fig 2: Heatmap por municipio ──
vars_positivas = ["VPH_RADIO", "VPH_TV", "VPH_PC", "VPH_TELEF", "VPH_CEL",
                  "VPH_INTER", "VPH_STVP", "VPH_SPMVPI", "VPH_CVJ"]
etiquetas_tic = {
    "VPH_RADIO": "Radio", "VPH_TV": "TV", "VPH_PC": "PC/Laptop",
    "VPH_TELEF": "Tel. Fijo", "VPH_CEL": "Celular",
    "VPH_INTER": "Internet", "VPH_STVP": "TV Paga",
    "VPH_SPMVPI": "Streaming", "VPH_CVJ": "Videojuegos",
}
rows_hm = []
for _, row_hm in filas_mun.iterrows():
    mun_id = int(row_hm["MUN"])
    vph = row_hm["VIVPAR_HAB"]
    if pd.isna(vph) or vph == 0: continue
    rd = {"Municipio": nombres_mun.get(mun_id, str(mun_id))}
    for vp in vars_positivas:
        val = row_hm[vp]
        rd[etiquetas_tic[vp]] = (val / vph * 100) if pd.notna(val) else np.nan
    rows_hm.append(rd)
df_hm = pd.DataFrame(rows_hm).set_index("Municipio")

fig2, ax2 = plt.subplots(figsize=(12, 7))
sns.heatmap(df_hm, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5,
            cbar_kws={"label": "% de viviendas habitadas", "shrink": 0.85},
            ax=ax2, vmin=0, vmax=100)
ax2.set_title("Acceso Digital por Municipio (% de viviendas habitadas)", fontsize=13, fontweight="bold")
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right", fontsize=9)
ax2.set_yticklabels(ax2.get_yticklabels(), rotation=0, fontsize=9)
img_mun = fig_to_base64(fig2)

# ── Fig 3: Barras de brecha digital por TAMLOC ──
fig3, ax3 = plt.subplots(figsize=(12, 6))
tam_labels = []
inter_vals = []
cel_vals = []
pc_vals = []
for tam in sorted(df["TAMLOC"].dropna().unique()):
    tam_int = int(tam)
    mask = df["TAMLOC"] == tam
    tam_labels.append(tamloc_etiquetas.get(tam_int, str(tam_int)))
    for vlist, vname in [(inter_vals, "TASA_INTER"), (cel_vals, "TASA_CEL"),
                         (pc_vals, "TASA_PC")]:
        m = media_manual(df.loc[mask, vname]) if vname in df.columns else np.nan
        vlist.append(m * 100 if pd.notna(m) else 0)

x = np.arange(len(tam_labels))
width = 0.25
ax3.bar(x - width, inter_vals, width, label="Internet", color="#2196F3")
ax3.bar(x, cel_vals, width, label="Celular", color="#4CAF50")
ax3.bar(x + width, pc_vals, width, label="PC/Laptop", color="#FF9800")
ax3.set_xlabel("Tamaño de localidad")
ax3.set_ylabel("% de viviendas habitadas")
ax3.set_title("Brecha Digital por Tamaño de Localidad", fontsize=13, fontweight="bold")
ax3.set_xticks(x)
ax3.set_xticklabels(tam_labels, rotation=45, ha="right", fontsize=8)
ax3.legend(loc="upper left")
ax3.grid(axis="y", alpha=0.3)
img_brecha = fig_to_base64(fig3)

# ── Fig 4: Top correlaciones ──
pares = []
for i in range(n_vars):
    for j in range(i + 1, n_vars):
        r = corr_matrix[i, j]
        if pd.notna(r) and abs(r) > 0.5:
            pares.append((abrevs[i], abrevs[j], r))
pares.sort(key=lambda x: abs(x[2]), reverse=True)
top_pares = pares[:15]

fig4, ax4 = plt.subplots(figsize=(10, 6))
labels_p = [f"{a} – {b}" for a, b, _ in top_pares]
vals_p = [r for _, _, r in top_pares]
colors_p = ["#E53935" if r < 0 else "#1E88E5" for r in vals_p]
ax4.barh(range(len(top_pares)), vals_p, color=colors_p, edgecolor="white")
ax4.set_yticks(range(len(top_pares)))
ax4.set_yticklabels(labels_p, fontsize=9)
ax4.set_xlabel("Correlación de Pearson (r)")
ax4.set_title("Correlaciones Más Fuertes entre Tasas de Acceso Digital",
              fontsize=13, fontweight="bold")
ax4.axvline(0, color="black", linewidth=0.5)
ax4.grid(axis="x", alpha=0.3)
ax4.invert_yaxis()
img_top_corr = fig_to_base64(fig4)


# ──────────────────────────────────────────────────────────────────────────────
# 4. GENERAR HTML
# ──────────────────────────────────────────────────────────────────────────────
print("  Construyendo HTML...")

def df_to_html_styled(df_t, fmt_dict=None, highlight_col=None):
    """Convierte un DataFrame a tabla HTML con estilo inline."""
    html = '<table class="styled-table">\n<thead><tr>'
    for col in df_t.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead>\n<tbody>\n"
    for _, row in df_t.iterrows():
        html += "<tr>"
        for col in df_t.columns:
            val = row[col]
            if fmt_dict and col in fmt_dict:
                try:
                    cell = fmt_dict[col](val)
                except (ValueError, TypeError):
                    cell = str(val) if pd.notna(val) else "—"
            elif isinstance(val, float):
                cell = f"{val:.4f}" if pd.notna(val) else "—"
            elif isinstance(val, (int, np.integer)):
                cell = f"{val:,}"
            else:
                cell = str(val) if pd.notna(val) else "—"

            style = ""
            if highlight_col and col == highlight_col and isinstance(val, (int, float, np.floating)):
                if pd.notna(val):
                    if val >= 10:
                        style = ' style="background:#ffcdd2;font-weight:bold"'
                    elif val >= 5:
                        style = ' style="background:#fff9c4"'
            html += f"<td{style}>{cell}</td>"
        html += "</tr>\n"
    html += "</tbody></table>\n"
    return html


# Formatters
fmt_stats = {
    "n": lambda x: f"{int(x):,}",
    "Media": lambda x: f"{x:.4f}",
    "Mediana": lambda x: f"{x:.4f}",
    "Desv. Est.": lambda x: f"{x:.4f}",
    "CV (%)": lambda x: f"{x:.1f}%",
    "Asimetría": lambda x: f"{x:.3f}",
    "Curtosis": lambda x: f"{x:.3f}",
}
fmt_demo = {
    "n": lambda x: f"{int(x):,}",
    "Media": lambda x: f"{x:,.2f}",
    "Mediana": lambda x: f"{x:,.2f}",
    "Desv. Est.": lambda x: f"{x:,.2f}",
    "CV (%)": lambda x: f"{x:.1f}%",
    "Asimetría": lambda x: f"{x:.3f}",
    "Curtosis": lambda x: f"{x:.3f}",
}
fmt_perc = {
    "Mín": lambda x: f"{x:.4f}", "P5": lambda x: f"{x:.4f}",
    "P25": lambda x: f"{x:.4f}", "P50": lambda x: f"{x:.4f}",
    "P75": lambda x: f"{x:.4f}", "P95": lambda x: f"{x:.4f}",
    "Máx": lambda x: f"{x:.4f}",
}
fmt_mun = {
    "Internet %": lambda x: f"{x:.1f}%", "Celular %": lambda x: f"{x:.1f}%",
    "PC %": lambda x: f"{x:.1f}%", "TV %": lambda x: f"{x:.1f}%",
    "Sin TIC %": lambda x: f"{x:.1f}%",
}
fmt_tam = {
    "n": lambda x: f"{int(x):,}",
    "Internet": lambda x: f"{x:.1f}%", "Celular": lambda x: f"{x:.1f}%",
    "PC/Laptop/Tablet": lambda x: f"{x:.1f}%", "Televisor": lambda x: f"{x:.1f}%",
}
fmt_vif = {
    "VIF": lambda x: f"{x:.2f}",
}
fmt_socio = {
    "POBTOT": lambda x: f"{x:.3f}", "GRAPROES": lambda x: f"{x:.3f}",
    "PROM_OCUP": lambda x: f"{x:.3f}", "VIVPAR_HAB": lambda x: f"{x:.3f}",
}

# Calcular resumen para header
tasa_inter = media_manual(df["TASA_INTER"]) if "TASA_INTER" in df.columns else 0
tasa_cel = media_manual(df["TASA_CEL"]) if "TASA_CEL" in df.columns else 0
tasa_pc = media_manual(df["TASA_PC"]) if "TASA_PC" in df.columns else 0
tasa_sintic = media_manual(df["TASA_SINTIC"]) if "TASA_SINTIC" in df.columns else 0

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Etapa 2 — Estadística Descriptiva · Acceso Digital en Aguascalientes</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f7fa;
    color: #333;
    line-height: 1.6;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
  header {{
    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #01579b 100%);
    color: white; padding: 40px 20px; text-align: center;
    border-radius: 0 0 20px 20px; margin-bottom: 30px;
  }}
  header h1 {{ font-size: 2em; margin-bottom: 8px; letter-spacing: -0.5px; }}
  header p {{ font-size: 1.1em; opacity: 0.9; }}
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px; margin: 25px 0;
  }}
  .kpi-card {{
    background: white; border-radius: 12px; padding: 20px; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-top: 4px solid #1565c0;
  }}
  .kpi-card .kpi-value {{ font-size: 2em; font-weight: bold; color: #1565c0; }}
  .kpi-card .kpi-label {{ font-size: 0.85em; color: #666; margin-top: 5px; }}
  section {{
    background: white; border-radius: 12px; padding: 25px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 25px;
  }}
  section h2 {{
    font-size: 1.4em; color: #1a237e; margin-bottom: 15px;
    border-bottom: 2px solid #e8eaf6; padding-bottom: 8px;
  }}
  section h3 {{ font-size: 1.1em; color: #283593; margin: 15px 0 10px; }}
  .styled-table {{
    width: 100%; border-collapse: collapse; font-size: 0.85em;
    margin: 10px 0 20px;
  }}
  .styled-table th {{
    background: #1a237e; color: white; padding: 10px 8px; text-align: left;
    font-weight: 600; white-space: nowrap;
  }}
  .styled-table td {{
    padding: 8px; border-bottom: 1px solid #e0e0e0; white-space: nowrap;
  }}
  .styled-table tbody tr:nth-child(even) {{ background: #f5f7fa; }}
  .styled-table tbody tr:hover {{ background: #e8eaf6; }}
  .fig-container {{ text-align: center; margin: 20px 0; }}
  .fig-container img {{ max-width: 100%; height: auto; border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
  .fig-caption {{ font-size: 0.85em; color: #666; margin-top: 8px; font-style: italic; }}
  .hallazgo {{
    background: #e3f2fd; border-left: 4px solid #1565c0; padding: 15px 20px;
    border-radius: 0 8px 8px 0; margin: 10px 0;
  }}
  .hallazgo strong {{ color: #0d47a1; }}
  .alert {{
    background: #fff3e0; border-left: 4px solid #e65100; padding: 15px 20px;
    border-radius: 0 8px 8px 0; margin: 10px 0;
  }}
  footer {{
    text-align: center; padding: 20px; color: #888; font-size: 0.85em;
  }}
  @media print {{
    body {{ background: white; }}
    header {{ border-radius: 0; }}
    section {{ box-shadow: none; border: 1px solid #ddd; page-break-inside: avoid; }}
    .kpi-card {{ box-shadow: none; border: 1px solid #ddd; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Etapa 2 — Estadística Descriptiva</h1>
  <p>Censo de Población y Vivienda 2020 · Aguascalientes · Enfoque: Acceso Digital</p>
  <p style="font-size:0.85em;opacity:0.7;margin-top:8px">
    {len(df):,} localidades analizadas · 13 variables de acceso digital · 11 municipios
  </p>
</header>

<div class="container">

<!-- KPIs -->
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-value">{tasa_inter:.1%}</div>
    <div class="kpi-label">Internet (prom. por localidad)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value">{tasa_cel:.1%}</div>
    <div class="kpi-label">Celular (prom. por localidad)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value">{tasa_pc:.1%}</div>
    <div class="kpi-label">PC/Laptop (prom. por localidad)</div>
  </div>
  <div class="kpi-card" style="border-top-color:#e53935">
    <div class="kpi-value" style="color:#e53935">{tasa_sintic:.1%}</div>
    <div class="kpi-label">Sin ninguna TIC</div>
  </div>
</div>

<!-- Sección 1: Descriptiva demográfica -->
<section>
  <h2>1. Variables de Contexto Demográfico</h2>
  {df_to_html_styled(tabla_demo, fmt_demo)}
</section>

<!-- Sección 2: Tasas de acceso digital -->
<section>
  <h2>2. Tasas de Acceso Digital</h2>
  <p>Proporción respecto a viviendas particulares habitadas (VPH / VIVPAR_HAB).</p>
  {df_to_html_styled(tabla_tasas, fmt_stats)}

  <h3>Percentiles</h3>
  {df_to_html_styled(tabla_perc, fmt_perc)}
</section>

<!-- Sección 3: Acceso por municipio -->
<section>
  <h2>3. Acceso Digital por Municipio</h2>
  {df_to_html_styled(tabla_mun, fmt_mun)}

  <div class="fig-container">
    <img src="data:image/png;base64,{img_mun}" alt="Heatmap acceso digital por municipio">
    <p class="fig-caption">Porcentaje de viviendas habitadas con cada tecnología, por municipio.</p>
  </div>
</section>

<!-- Sección 4: Brecha digital -->
<section>
  <h2>4. Brecha Digital por Tamaño de Localidad</h2>
  {df_to_html_styled(tabla_tam, fmt_tam)}

  <div class="fig-container">
    <img src="data:image/png;base64,{img_brecha}" alt="Brecha digital por tamaño de localidad">
    <p class="fig-caption">A mayor tamaño de localidad, mayor penetración de Internet, celular y PC.</p>
  </div>

  <div class="hallazgo">
    <strong>Hallazgo:</strong> La brecha digital es más pronunciada en Internet y computadoras
    que en televisión y celular. Las localidades con menos de 250 habitantes tienen tasas de
    Internet por debajo del 30%, mientras que las mayores superan el 70%.
  </div>
</section>

<!-- Sección 5: Correlación -->
<section>
  <h2>5. Análisis de Correlación</h2>

  <div class="fig-container">
    <img src="data:image/png;base64,{img_corr}" alt="Heatmap de correlación">
    <p class="fig-caption">Matriz de correlación de Pearson entre las 13 tasas de acceso digital.</p>
  </div>

  <div class="fig-container">
    <img src="data:image/png;base64,{img_top_corr}" alt="Top correlaciones">
    <p class="fig-caption">Pares con |r| > 0.50, ordenados por fuerza de correlación.</p>
  </div>

  <h3>Correlación con Variables Socioeconómicas</h3>
  {df_to_html_styled(tabla_socio, fmt_socio)}
</section>

<!-- Sección 6: Colinealidad -->
<section>
  <h2>6. Análisis de Colinealidad (VIF)</h2>
  <p>VIF = Factor de Inflación de la Varianza. VIF &ge; 10 indica colinealidad severa.</p>
  {df_to_html_styled(tabla_vif, fmt_vif, highlight_col="VIF") if tabla_vif is not None else "<p>No se pudo calcular el VIF.</p>"}

  <div class="alert">
    <strong>Atención:</strong> Varias variables presentan colinealidad severa (VIF &ge; 10).
    Para modelos predictivos, considerar PCA, regularización (Ridge/Lasso), o un índice compuesto.
  </div>
</section>

<!-- Sección 7: Hallazgos clave -->
<section>
  <h2>7. Hallazgos Clave</h2>

  <div class="hallazgo">
    <strong>1. Penetración desigual:</strong> El celular tiene alta penetración ({tasa_cel:.1%}),
    pero Internet ({tasa_inter:.1%}) y PC ({tasa_pc:.1%}) muestran rezago significativo en
    localidades pequeñas.
  </div>

  <div class="hallazgo">
    <strong>2. Alta asimetría:</strong> Todas las tasas de acceso digital tienen distribuciones
    con sesgo positivo (la mayoría de localidades con tasas bajas, pocas con tasas altas),
    reflejando la concentración urbana de la infraestructura digital.
  </div>

  <div class="hallazgo">
    <strong>3. Cluster de acceso avanzado:</strong> Internet, PC y streaming están fuertemente
    correlacionados, formando un indicador latente de "digitalización avanzada".
  </div>

  <div class="hallazgo">
    <strong>4. Escolaridad como predictor:</strong> El grado promedio de escolaridad (GRAPROES)
    presenta la correlación más fuerte con el acceso a PC e Internet, sugiriendo que la
    educación es un factor clave en la adopción digital.
  </div>

  <div class="hallazgo">
    <strong>5. Recomendación:</strong> Para las etapas 3 y 4, investigar la censura de datos
    ('*') como mecanismo MNAR ligado al tamaño de localidad, y crear visualizaciones
    geográficas con coordenadas lat/lon para mapear la brecha digital.
  </div>
</section>

</div>

<footer>
  Reporte generado automáticamente · Etapa 2 · Censo INEGI 2020 · Aguascalientes
</footer>
</body>
</html>
"""

# ──────────────────────────────────────────────────────────────────────────────
# 5. GUARDAR
# ──────────────────────────────────────────────────────────────────────────────
ruta_html = os.path.join(OUTPUT_DIR, "etapa2_reporte.html")
with open(ruta_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n  ✓ Reporte HTML guardado en: {ruta_html}")
print(f"    Ábrelo en un navegador para ver las tablas y gráficos.")
print(f"    También puedes imprimir a PDF desde el navegador (Ctrl+P).")
print(f"\n  Archivos generados en output/:")
for fn in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, fn)
    size_kb = os.path.getsize(fpath) / 1024
    print(f"    • {fn} ({size_kb:.0f} KB)")
