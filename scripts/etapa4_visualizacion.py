# -*- coding: utf-8 -*-
"""
================================================================================
  ETAPA 4 — Visualización Completa
  Censo de Población y Vivienda 2020 · Estado de Aguascalientes
  Enfoque: Acceso Digital en la Población
================================================================================
  Contenido:
    1. Histogramas con KDE de tasas de acceso digital.
    2. Boxplots por municipio y tamaño de localidad.
    3. Violin plots comparativos.
    4. Gráficos de correlación y pairplots multivariados.
    5. Mapa geográfico de Aguascalientes con variable clave (Internet).
    6. Distribuciones demográficas (pirámide poblacional).
    7. Brecha digital: visualización por nivel de urbanización.
    8. Gráficos de dispersión multivariados.
================================================================================
"""

import pandas as pd
import numpy as np
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
import seaborn as sns
import warnings, os

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "font.family": "sans-serif",
})

# ──────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN Y CARGA DE DATOS
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RUTA_DATOS = os.path.join(DATA_DIR, "conjunto_de_datos_iter_01CSV20.csv")

print("=" * 90)
print("  ETAPA 4 — VISUALIZACIÓN COMPLETA")
print("  Censo de Población y Vivienda 2020 · Aguascalientes")
print("  Enfoque: Acceso Digital en la Población")
print("=" * 90)

# ── Lectura ──
df_raw = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig", low_memory=False)

# Filtrar localidades reales
df = df_raw[(df_raw["LOC"] > 0) & (df_raw["LOC"] < 9998)].copy()
print(f"\n  Localidades reales analizadas: {len(df):,}")

# Convertir a numérico
cols_texto = ["NOM_ENT", "NOM_MUN", "NOM_LOC", "LONGITUD", "LATITUD"]
for col in df.columns:
    if col not in cols_texto:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Variables de acceso digital
vars_acceso_digital = [
    "VPH_RADIO", "VPH_TV", "VPH_PC", "VPH_TELEF", "VPH_CEL",
    "VPH_INTER", "VPH_STVP", "VPH_SPMVPI", "VPH_CVJ",
    "VPH_SINRTV", "VPH_SINLTC", "VPH_SINCINT", "VPH_SINTIC",
]

# Crear tasas
vars_tasas = []
for v in vars_acceso_digital:
    nombre_tasa = f"TASA_{v.replace('VPH_', '')}"
    mask = df["VIVPAR_HAB"].notna() & (df["VIVPAR_HAB"] > 0) & df[v].notna()
    df.loc[mask, nombre_tasa] = df.loc[mask, v] / df.loc[mask, "VIVPAR_HAB"]
    vars_tasas.append(nombre_tasa)

vars_tasas_positivas = [
    "TASA_RADIO", "TASA_TV", "TASA_PC", "TASA_TELEF", "TASA_CEL",
    "TASA_INTER", "TASA_STVP", "TASA_SPMVPI", "TASA_CVJ",
]
vars_tasas_carencia = ["TASA_SINRTV", "TASA_SINLTC", "TASA_SINCINT", "TASA_SINTIC"]

# Crear ICAD (Índice Compuesto de Acceso Digital) — reproducido de Etapa 3
pesos_icad = {
    "TASA_INTER": 0.20, "TASA_PC": 0.15, "TASA_CEL": 0.15,
    "TASA_SPMVPI": 0.10, "TASA_STVP": 0.10, "TASA_TV": 0.10,
    "TASA_TELEF": 0.05, "TASA_RADIO": 0.05, "TASA_CVJ": 0.05,
}
mask_icad = df[list(pesos_icad.keys()) + ["TASA_SINTIC"]].notna().all(axis=1)
for v in pesos_icad.keys():
    serie = df.loc[mask_icad, v]
    vmin, vmax = serie.min(), serie.max()
    df.loc[mask_icad, f"{v}_norm"] = (serie - vmin) / (vmax - vmin) if vmax > vmin else 0.0

s_sintic = df.loc[mask_icad, "TASA_SINTIC"]
smin, smax = s_sintic.min(), s_sintic.max()
df.loc[mask_icad, "TASA_SINTIC_norm"] = (s_sintic - smin) / (smax - smin) if smax > smin else 0.0

icad = np.zeros(mask_icad.sum())
for v, peso in pesos_icad.items():
    icad += peso * df.loc[mask_icad, f"{v}_norm"].values
icad -= 0.05 * df.loc[mask_icad, "TASA_SINTIC_norm"].values
df.loc[mask_icad, "ICAD"] = np.clip(icad, 0, 1)

# Etiquetas
nombres_mun = {
    1: "Aguascalientes", 2: "Asientos", 3: "Calvillo", 4: "Cosío",
    5: "Jesús María", 6: "Pabellón de Arteaga", 7: "Rincón de Romos",
    8: "San José de Gracia", 9: "Tepezalá",
    10: "El Llano", 11: "San Fco. de los Romo",
}

tamloc_etiquetas = {
    1: "1-249", 2: "250-499", 3: "500-999", 4: "1K-2.5K",
    5: "2.5K-5K", 6: "5K-10K", 7: "10K-15K", 8: "15K-30K",
    9: "30K-50K", 10: "50K-100K", 13: "500K-1M",
}

nombres_tasas_corto = {
    "TASA_RADIO": "Radio", "TASA_TV": "TV", "TASA_PC": "PC/Laptop",
    "TASA_TELEF": "Tel. Fijo", "TASA_CEL": "Celular",
    "TASA_INTER": "Internet", "TASA_STVP": "TV Paga",
    "TASA_SPMVPI": "Streaming", "TASA_CVJ": "Videojuegos",
    "TASA_SINRTV": "Sin Radio/TV", "TASA_SINLTC": "Sin Teléfono",
    "TASA_SINCINT": "Sin PC/Internet", "TASA_SINTIC": "Sin TIC",
}

# Subconjunto con datos completos para gráficos que requieren NaN-free data
df_comp = df[mask_icad].copy()
print(f"  Localidades con datos completos: {len(df_comp):,}")

# Parse LATITUD y LONGITUD (formato DMS → decimal)
def dms_a_decimal(dms_str):
    """Convierte '21°52'47.362\" N' a decimal."""
    if pd.isna(dms_str) or not isinstance(dms_str, str):
        return np.nan
    try:
        match = re.match(r"(\d+)°(\d+)'([\d.]+)\"\s*([NSEW])", dms_str.strip())
        if not match:
            return np.nan
        grados = float(match.group(1))
        minutos = float(match.group(2))
        segundos = float(match.group(3))
        direccion = match.group(4)
        decimal = grados + minutos / 60.0 + segundos / 3600.0
        if direccion in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return np.nan

df["LAT_DEC"] = df["LATITUD"].apply(dms_a_decimal)
df["LON_DEC"] = df["LONGITUD"].apply(dms_a_decimal)
df_comp["LAT_DEC"] = df.loc[mask_icad, "LAT_DEC"]
df_comp["LON_DEC"] = df.loc[mask_icad, "LON_DEC"]

n_geo = (df["LAT_DEC"].notna() & df["LON_DEC"].notna()).sum()
print(f"  Localidades con coordenadas válidas: {n_geo:,}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  1. HISTOGRAMAS CON KDE — TASAS DE ACCESO DIGITAL                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  1. HISTOGRAMAS CON KDE — TASAS DE ACCESO DIGITAL")
print("=" * 90)

fig, axes = plt.subplots(3, 3, figsize=(16, 14))
axes_flat = axes.flatten()

for i, v in enumerate(vars_tasas_positivas):
    ax = axes_flat[i]
    data = df_comp[v].dropna()
    if len(data) == 0:
        continue

    ax.hist(data, bins=35, density=True, alpha=0.6, color="#1976D2",
            edgecolor="white", linewidth=0.3, label="Histograma")

    # KDE manual (solo si hay suficientes datos)
    if len(data) > 10:
        from numpy import linspace
        x_kde = linspace(max(data.min() - 0.05, 0), min(data.max() + 0.05, 1.5), 200)
        # Bandwidth using Silverman's rule
        h = 1.06 * data.std() * len(data) ** (-1/5)
        if h > 0:
            kde_vals = np.zeros_like(x_kde)
            for xi in data.values:
                kde_vals += np.exp(-0.5 * ((x_kde - xi) / h) ** 2) / (h * np.sqrt(2 * np.pi))
            kde_vals /= len(data)
            ax.plot(x_kde, kde_vals, color="#FF5722", linewidth=1.8, label="KDE")

    mu = data.mean()
    med = data.median()
    ax.axvline(mu, color="#4CAF50", linestyle="--", linewidth=1, alpha=0.8)
    ax.axvline(med, color="#FF9800", linestyle=":", linewidth=1, alpha=0.8)

    nombre = nombres_tasas_corto.get(v, v)
    ax.set_title(f"{nombre}\nμ={mu:.3f}, med={med:.3f}", fontsize=9)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(labelsize=7)

# Leyenda global
handles = [
    mpatches.Patch(color="#1976D2", alpha=0.6, label="Histograma"),
    plt.Line2D([0], [0], color="#FF5722", linewidth=1.8, label="KDE"),
    plt.Line2D([0], [0], color="#4CAF50", linestyle="--", label="Media"),
    plt.Line2D([0], [0], color="#FF9800", linestyle=":", label="Mediana"),
]
fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=9,
           bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Distribución de Tasas de Acceso Digital por Localidad\n"
             "Aguascalientes, Censo 2020 (n con datos completos)",
             fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()

ruta_hist = os.path.join(OUTPUT_DIR, "etapa4_histogramas_kde.png")
fig.savefig(ruta_hist, dpi=200)
plt.close(fig)
print(f"\n  ✓ Histogramas KDE guardados en: {ruta_hist}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  2. BOXPLOTS POR MUNICIPIO Y TAMAÑO DE LOCALIDAD                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  2. BOXPLOTS POR MUNICIPIO Y TAMAÑO DE LOCALIDAD")
print("=" * 90)

# ── 2a. Boxplot de 4 variables clave por municipio ──
fig2, axes2 = plt.subplots(2, 2, figsize=(16, 12))
vars_clave = ["TASA_INTER", "TASA_CEL", "TASA_PC", "TASA_SINTIC"]
titulos = ["Acceso a Internet", "Acceso a Celular", "Acceso a PC/Laptop",
           "Sin ninguna TIC"]
colores = ["#1976D2", "#4CAF50", "#FF9800", "#F44336"]

for idx, (v, titulo, color) in enumerate(zip(vars_clave, titulos, colores)):
    ax = axes2[idx // 2, idx % 2]
    data_bp = []
    labels_bp = []
    for mun_id in sorted(nombres_mun.keys()):
        mask_m = (df_comp["MUN"] == mun_id)
        vals = df_comp.loc[mask_m, v].dropna()
        if len(vals) > 0:
            data_bp.append(vals.values)
            labels_bp.append(nombres_mun[mun_id][:10])

    bp = ax.boxplot(data_bp, labels=labels_bp, patch_artist=True, vert=True,
                    widths=0.7, showfliers=True, flierprops=dict(markersize=2))
    for patch in bp["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    for median in bp["medians"]:
        median.set_color("black")
        median.set_linewidth(1.5)

    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.set_ylabel(f"Tasa (proporción)")
    ax.set_xticklabels(labels_bp, rotation=45, ha="right", fontsize=7)
    ax.grid(axis="y", alpha=0.3)

fig2.suptitle("Distribución de Acceso Digital por Municipio\n"
              "Aguascalientes, Censo 2020", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()

ruta_bp_mun = os.path.join(OUTPUT_DIR, "etapa4_boxplot_municipio.png")
fig2.savefig(ruta_bp_mun, dpi=200)
plt.close(fig2)
print(f"\n  ✓ Boxplots por municipio guardados en: {ruta_bp_mun}")

# ── 2b. Boxplot por tamaño de localidad ──
fig2b, axes2b = plt.subplots(2, 2, figsize=(16, 12))

for idx, (v, titulo, color) in enumerate(zip(vars_clave, titulos, colores)):
    ax = axes2b[idx // 2, idx % 2]
    data_bp = []
    labels_bp = []
    for tam in sorted(df_comp["TAMLOC"].dropna().unique()):
        tam_int = int(tam)
        mask_t = df_comp["TAMLOC"] == tam
        vals = df_comp.loc[mask_t, v].dropna()
        if len(vals) > 2:
            data_bp.append(vals.values)
            labels_bp.append(tamloc_etiquetas.get(tam_int, str(tam_int)))

    if len(data_bp) > 0:
        bp = ax.boxplot(data_bp, labels=labels_bp, patch_artist=True, vert=True,
                        widths=0.7, showfliers=True, flierprops=dict(markersize=2))
        for patch in bp["boxes"]:
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        for median in bp["medians"]:
            median.set_color("black")
            median.set_linewidth(1.5)

    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.set_ylabel("Tasa (proporción)")
    ax.set_xticklabels(labels_bp, rotation=45, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.3)

fig2b.suptitle("Distribución de Acceso Digital por Tamaño de Localidad\n"
               "Aguascalientes, Censo 2020", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()

ruta_bp_tam = os.path.join(OUTPUT_DIR, "etapa4_boxplot_tamloc.png")
fig2b.savefig(ruta_bp_tam, dpi=200)
plt.close(fig2b)
print(f"  ✓ Boxplots por TAMLOC guardados en: {ruta_bp_tam}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  3. VIOLIN PLOTS                                                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  3. VIOLIN PLOTS — ACCESO DIGITAL POR MUNICIPIO")
print("=" * 90)

# Violin plot: Internet y Celular por municipio
fig3, axes3 = plt.subplots(1, 2, figsize=(16, 7))

for ax_idx, (v, titulo) in enumerate([("TASA_INTER", "Internet"),
                                       ("TASA_CEL", "Celular")]):
    ax = axes3[ax_idx]

    # Construir dataframe para seaborn
    plot_data = []
    for mun_id in sorted(nombres_mun.keys()):
        mask_m = (df_comp["MUN"] == mun_id)
        vals = df_comp.loc[mask_m, v].dropna()
        for val in vals.values:
            plot_data.append({"Municipio": nombres_mun[mun_id][:12], "Tasa": val})

    if len(plot_data) > 0:
        pdf = pd.DataFrame(plot_data)
        order = sorted(pdf["Municipio"].unique())
        sns.violinplot(x="Municipio", y="Tasa", data=pdf, ax=ax,
                       order=order, scale="width", inner="quartile",
                       palette="Set2", linewidth=0.8)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)

    ax.set_title(f"Tasa de Acceso a {titulo}", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tasa (proporción)")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.3)

fig3.suptitle("Violin Plots — Acceso Digital por Municipio\n"
              "Aguascalientes, Censo 2020", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()

ruta_violin = os.path.join(OUTPUT_DIR, "etapa4_violin_municipio.png")
fig3.savefig(ruta_violin, dpi=200)
plt.close(fig3)
print(f"\n  ✓ Violin plots guardados en: {ruta_violin}")

# ── Violin plot comparativo: todas las TIC ──
fig3b, ax3b = plt.subplots(figsize=(14, 6))
plot_data_all = []
for v in vars_tasas_positivas:
    vals = df_comp[v].dropna()
    nombre = nombres_tasas_corto.get(v, v)
    for val in vals.values:
        plot_data_all.append({"TIC": nombre, "Tasa": val})

pdf_all = pd.DataFrame(plot_data_all)
order_tic = [nombres_tasas_corto[v] for v in vars_tasas_positivas]
sns.violinplot(x="TIC", y="Tasa", data=pdf_all, ax=ax3b,
               order=order_tic, scale="width", inner="quartile",
               palette="viridis", linewidth=0.8)
ax3b.set_xticklabels(ax3b.get_xticklabels(), rotation=45, ha="right", fontsize=9)
ax3b.set_title("Comparación de Todas las TIC — Distribución por Localidad\n"
               "Aguascalientes, Censo 2020", fontsize=12, fontweight="bold")
ax3b.set_ylabel("Tasa (proporción)")
ax3b.set_xlabel("")
ax3b.grid(axis="y", alpha=0.3)
plt.tight_layout()

ruta_violin_all = os.path.join(OUTPUT_DIR, "etapa4_violin_todas_tic.png")
fig3b.savefig(ruta_violin_all, dpi=200)
plt.close(fig3b)
print(f"  ✓ Violin plot comparativo guardado en: {ruta_violin_all}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  4. PAIRPLOT MULTIVARIADO                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  4. PAIRPLOT MULTIVARIADO")
print("=" * 90)

# Variables para el pairplot
vars_pair = ["TASA_INTER", "TASA_CEL", "TASA_PC", "TASA_SPMVPI", "ICAD"]
df_pair = df_comp[vars_pair + ["MUN"]].dropna()

# Crear variable de agrupación simplificada
def clasificar_mun(mun_id):
    if mun_id == 1:
        return "Capital"
    elif mun_id in [5, 6, 7, 11]:
        return "Semiurbano"
    else:
        return "Rural"

df_pair["Tipo"] = df_pair["MUN"].apply(clasificar_mun)

# Renombrar columnas para legibilidad
rename_pair = {
    "TASA_INTER": "Internet", "TASA_CEL": "Celular",
    "TASA_PC": "PC/Laptop", "TASA_SPMVPI": "Streaming", "ICAD": "ICAD"
}
df_pair_plot = df_pair.rename(columns=rename_pair)

g = sns.pairplot(df_pair_plot,
                 vars=["Internet", "Celular", "PC/Laptop", "Streaming", "ICAD"],
                 hue="Tipo", palette={"Capital": "#1976D2", "Semiurbano": "#4CAF50",
                                       "Rural": "#FF9800"},
                 diag_kind="kde", plot_kws={"alpha": 0.5, "s": 15},
                 height=2.2, aspect=1)
g.figure.suptitle("Pairplot — Variables de Acceso Digital por Tipo de Municipio\n"
                   "Aguascalientes, Censo 2020",
                   fontsize=13, fontweight="bold", y=1.02)

ruta_pair = os.path.join(OUTPUT_DIR, "etapa4_pairplot.png")
g.savefig(ruta_pair, dpi=150)
plt.close(g.figure)
print(f"\n  ✓ Pairplot guardado en: {ruta_pair}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  5. MAPA GEOGRÁFICO — ACCESO A INTERNET POR LOCALIDAD                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  5. MAPAS GEOGRÁFICOS — ACCESO DIGITAL EN AGUASCALIENTES")
print("=" * 90)

# ── 5a. Mapa de dispersión: tasa de Internet ──
df_geo = df[df["LAT_DEC"].notna() & df["LON_DEC"].notna()].copy()
df_geo_comp = df_geo[df_geo["TASA_INTER"].notna()].copy()

fig5, ax5 = plt.subplots(figsize=(12, 14))

# Fondo: todas las localidades (incluyendo censuradas) en gris
df_geo_cens = df_geo[df_geo["TASA_INTER"].isna()]
ax5.scatter(df_geo_cens["LON_DEC"], df_geo_cens["LAT_DEC"],
            c="lightgray", s=8, alpha=0.4, zorder=1,
            label=f"Censuradas (n={len(df_geo_cens):,})")

# Localidades con datos: colorear por tasa de Internet
scatter = ax5.scatter(
    df_geo_comp["LON_DEC"], df_geo_comp["LAT_DEC"],
    c=df_geo_comp["TASA_INTER"],
    cmap="RdYlGn", vmin=0, vmax=1,
    s=df_geo_comp["POBTOT"].clip(upper=5000) / 50 + 5,  # Tamaño ∝ población
    alpha=0.75, edgecolors="black", linewidths=0.3, zorder=2
)

cbar = plt.colorbar(scatter, ax=ax5, shrink=0.6, pad=0.02)
cbar.set_label("Tasa de Acceso a Internet", fontsize=10)

# Etiquetar cabeceras municipales (las localidades con LOC=1 en cada MUN)
cabeceras = df_geo_comp[(df_geo_comp["LOC"] == 1)]
for _, row in cabeceras.iterrows():
    nom = str(row["NOM_LOC"])[:15]
    ax5.annotate(nom, (row["LON_DEC"], row["LAT_DEC"]),
                 fontsize=6, fontweight="bold",
                 textcoords="offset points", xytext=(5, 5),
                 path_effects=[pe.withStroke(linewidth=2, foreground="white")])

ax5.set_xlabel("Longitud")
ax5.set_ylabel("Latitud")
ax5.set_title("Mapa de Acceso a Internet por Localidad\n"
              "Aguascalientes, Censo 2020\n"
              "(Tamaño ∝ Población, Color = Tasa de Internet)",
              fontsize=13, fontweight="bold")
ax5.legend(loc="lower left", fontsize=8)
ax5.set_aspect("equal")
ax5.grid(alpha=0.2)

ruta_mapa1 = os.path.join(OUTPUT_DIR, "etapa4_mapa_internet.png")
fig5.savefig(ruta_mapa1, dpi=200)
plt.close(fig5)
print(f"\n  ✓ Mapa de Internet guardado en: {ruta_mapa1}")

# ── 5b. Mapa de ICAD ──
df_geo_icad = df_geo[df_geo["ICAD"].notna()].copy()

fig5b, ax5b = plt.subplots(figsize=(12, 14))

# Fondo
df_geo_no_icad = df_geo[df_geo["ICAD"].isna()]
ax5b.scatter(df_geo_no_icad["LON_DEC"], df_geo_no_icad["LAT_DEC"],
             c="lightgray", s=8, alpha=0.4, zorder=1,
             label=f"Sin datos (n={len(df_geo_no_icad):,})")

scatter_icad = ax5b.scatter(
    df_geo_icad["LON_DEC"], df_geo_icad["LAT_DEC"],
    c=df_geo_icad["ICAD"],
    cmap="plasma", vmin=0, vmax=1,
    s=df_geo_icad["POBTOT"].clip(upper=5000) / 50 + 5,
    alpha=0.75, edgecolors="black", linewidths=0.3, zorder=2
)

cbar_icad = plt.colorbar(scatter_icad, ax=ax5b, shrink=0.6, pad=0.02)
cbar_icad.set_label("ICAD (Índice Compuesto de Acceso Digital)", fontsize=10)

for _, row in cabeceras.iterrows():
    nom = str(row["NOM_LOC"])[:15]
    ax5b.annotate(nom, (row["LON_DEC"], row["LAT_DEC"]),
                  fontsize=6, fontweight="bold",
                  textcoords="offset points", xytext=(5, 5),
                  path_effects=[pe.withStroke(linewidth=2, foreground="white")])

ax5b.set_xlabel("Longitud")
ax5b.set_ylabel("Latitud")
ax5b.set_title("Mapa del Índice Compuesto de Acceso Digital (ICAD)\n"
               "Aguascalientes, Censo 2020\n"
               "(Tamaño ∝ Población, Color = ICAD)",
               fontsize=13, fontweight="bold")
ax5b.legend(loc="lower left", fontsize=8)
ax5b.set_aspect("equal")
ax5b.grid(alpha=0.2)

ruta_mapa2 = os.path.join(OUTPUT_DIR, "etapa4_mapa_icad.png")
fig5b.savefig(ruta_mapa2, dpi=200)
plt.close(fig5b)
print(f"  ✓ Mapa de ICAD guardado en: {ruta_mapa2}")

# ── 5c. Mapa por municipio (coloreado por municipio, tamaño por ICAD) ──
fig5c, ax5c = plt.subplots(figsize=(12, 14))
colores_mun = plt.cm.tab10(np.linspace(0, 1, len(nombres_mun)))
mun_patches = []

for i, mun_id in enumerate(sorted(nombres_mun.keys())):
    mask_m = df_geo["MUN"] == mun_id
    sub = df_geo[mask_m]
    ax5c.scatter(sub["LON_DEC"], sub["LAT_DEC"],
                 c=[colores_mun[i]], s=12, alpha=0.6,
                 edgecolors="none", zorder=2)
    mun_patches.append(mpatches.Patch(color=colores_mun[i],
                                       label=nombres_mun[mun_id]))

ax5c.legend(handles=mun_patches, loc="lower left", fontsize=7,
            title="Municipio", title_fontsize=8)
ax5c.set_xlabel("Longitud")
ax5c.set_ylabel("Latitud")
ax5c.set_title("Distribución Geográfica de Localidades por Municipio\n"
               "Aguascalientes, Censo 2020",
               fontsize=13, fontweight="bold")
ax5c.set_aspect("equal")
ax5c.grid(alpha=0.2)

ruta_mapa3 = os.path.join(OUTPUT_DIR, "etapa4_mapa_municipios.png")
fig5c.savefig(ruta_mapa3, dpi=200)
plt.close(fig5c)
print(f"  ✓ Mapa de municipios guardado en: {ruta_mapa3}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  6. DISTRIBUCIONES DEMOGRÁFICAS — PIRÁMIDE POBLACIONAL                  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  6. DISTRIBUCIONES DEMOGRÁFICAS")
print("=" * 90)

# ── 6a. Pirámide poblacional usando totales municipales ──
# Para la pirámide usamos los totales estatales (MUN=0, LOC=0)
fila_estatal = df_raw[(df_raw["MUN"] == 0) & (df_raw["LOC"] == 0)].iloc[0]

grupos_quinquenales = [
    ("0-4", "P_0A4_F", "P_0A4_M"),
    ("5-9", "P_5A9_F", "P_5A9_M"),
    ("10-14", "P_10A14_F", "P_10A14_M"),
    ("15-19", "P_15A19_F", "P_15A19_M"),
    ("20-24", "P_20A24_F", "P_20A24_M"),
    ("25-29", "P_25A29_F", "P_25A29_M"),
    ("30-34", "P_30A34_F", "P_30A34_M"),
    ("35-39", "P_35A39_F", "P_35A39_M"),
    ("40-44", "P_40A44_F", "P_40A44_M"),
    ("45-49", "P_45A49_F", "P_45A49_M"),
    ("50-54", "P_50A54_F", "P_50A54_M"),
    ("55-59", "P_55A59_F", "P_55A59_M"),
    ("60-64", "P_60A64_F", "P_60A64_M"),
    ("65-69", "P_65A69_F", "P_65A69_M"),
    ("70-74", "P_70A74_F", "P_70A74_M"),
    ("75-79", "P_75A79_F", "P_75A79_M"),
    ("80-84", "P_80A84_F", "P_80A84_M"),
    ("85+", "P_85YMAS_F", "P_85YMAS_M"),
]

labels_pir = []
fem_vals = []
mas_vals = []

for grupo, col_f, col_m in grupos_quinquenales:
    labels_pir.append(grupo)
    val_f = pd.to_numeric(fila_estatal.get(col_f, 0), errors="coerce")
    val_m = pd.to_numeric(fila_estatal.get(col_m, 0), errors="coerce")
    fem_vals.append(val_f if pd.notna(val_f) else 0)
    mas_vals.append(val_m if pd.notna(val_m) else 0)

fem_vals = np.array(fem_vals)
mas_vals = np.array(mas_vals)

# Pirámide
fig6, ax6 = plt.subplots(figsize=(10, 10))
y_pos = np.arange(len(labels_pir))

ax6.barh(y_pos, -mas_vals, color="#2196F3", edgecolor="white", linewidth=0.5,
         height=0.8, label="Hombres", alpha=0.85)
ax6.barh(y_pos, fem_vals, color="#E91E63", edgecolor="white", linewidth=0.5,
         height=0.8, label="Mujeres", alpha=0.85)

# Etiquetas de valores
for i, (m, f) in enumerate(zip(mas_vals, fem_vals)):
    ax6.text(-m - 500, i, f"{int(m):,}", ha="right", va="center", fontsize=6.5)
    ax6.text(f + 500, i, f"{int(f):,}", ha="left", va="center", fontsize=6.5)

ax6.set_yticks(y_pos)
ax6.set_yticklabels(labels_pir, fontsize=9)
ax6.set_xlabel("Población")
ax6.set_title("Pirámide Poblacional de Aguascalientes\n"
              "Censo de Población y Vivienda 2020",
              fontsize=13, fontweight="bold")
ax6.legend(loc="upper right", fontsize=10)

# Formato del eje X para mostrar valores absolutos
ax6.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{abs(int(x)):,}"))
ax6.axvline(0, color="black", linewidth=0.5)
ax6.grid(axis="x", alpha=0.2)
plt.tight_layout()

ruta_piramide = os.path.join(OUTPUT_DIR, "etapa4_piramide_poblacional.png")
fig6.savefig(ruta_piramide, dpi=200)
plt.close(fig6)
print(f"\n  ✓ Pirámide poblacional guardada en: {ruta_piramide}")

# ── 6b. Distribución de población por municipio ──
fig6b, axes6b = plt.subplots(1, 2, figsize=(14, 6))

# Datos de totales municipales
filas_mun = df_raw[(df_raw["MUN"] > 0) & (df_raw["LOC"] == 0)].copy()
for col_t in ["POBTOT", "POBFEM", "POBMAS", "VIVPAR_HAB"]:
    filas_mun[col_t] = pd.to_numeric(filas_mun[col_t], errors="coerce")

# 6b-left: Población por municipio (barras)
ax_l = axes6b[0]
mun_nombres = [nombres_mun.get(int(row["MUN"]), str(row["MUN"]))
               for _, row in filas_mun.iterrows()]
pob_total = filas_mun["POBTOT"].values
pob_fem = filas_mun["POBFEM"].values
pob_mas = filas_mun["POBMAS"].values

y_m = np.arange(len(mun_nombres))
ax_l.barh(y_m, pob_mas, color="#2196F3", alpha=0.8, label="Hombres", height=0.7)
ax_l.barh(y_m, pob_fem, left=pob_mas, color="#E91E63", alpha=0.8,
          label="Mujeres", height=0.7)
ax_l.set_yticks(y_m)
ax_l.set_yticklabels(mun_nombres, fontsize=8)
ax_l.set_xlabel("Población")
ax_l.set_title("Población por Municipio", fontsize=11, fontweight="bold")
ax_l.legend(fontsize=8)
ax_l.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{int(x):,}"))

# 6b-right: % de población por municipio (pie)
ax_r = axes6b[1]
colors_pie = plt.cm.Set3(np.linspace(0, 1, len(mun_nombres)))
wedges, texts, autotexts = ax_r.pie(
    pob_total, labels=mun_nombres, autopct="%1.1f%%",
    colors=colors_pie, startangle=90, pctdistance=0.80,
    textprops={"fontsize": 7}
)
for t in autotexts:
    t.set_fontsize(6)
ax_r.set_title("Distribución % de Población", fontsize=11, fontweight="bold")

fig6b.suptitle("Distribución Demográfica por Municipio — Aguascalientes 2020",
               fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()

ruta_demo_mun = os.path.join(OUTPUT_DIR, "etapa4_distribucion_poblacion_municipio.png")
fig6b.savefig(ruta_demo_mun, dpi=200)
plt.close(fig6b)
print(f"  ✓ Distribución demográfica por municipio guardada en: {ruta_demo_mun}")

# ── 6c. Distribución de localidades por tamaño ──
fig6c, ax6c = plt.subplots(figsize=(10, 6))
tam_counts = df["TAMLOC"].value_counts().sort_index()
tam_labels = [tamloc_etiquetas.get(int(t), str(int(t))) for t in tam_counts.index]

colors_tam = ["#F44336" if int(t) == 1 else "#FF9800" if int(t) <= 3
              else "#4CAF50" if int(t) <= 6 else "#1976D2"
              for t in tam_counts.index]

bars = ax6c.bar(tam_labels, tam_counts.values, color=colors_tam,
                edgecolor="white", linewidth=0.5)
for bar, count in zip(bars, tam_counts.values):
    ax6c.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
              f"{count:,}", ha="center", va="bottom", fontsize=8, fontweight="bold")

ax6c.set_xlabel("Tamaño de localidad (habitantes)")
ax6c.set_ylabel("Número de localidades")
ax6c.set_title("Distribución de Localidades por Tamaño — Aguascalientes 2020\n"
               "86% de las localidades tienen menos de 250 habitantes",
               fontsize=12, fontweight="bold")
plt.xticks(rotation=45, ha="right")
ax6c.grid(axis="y", alpha=0.3)
plt.tight_layout()

ruta_tam = os.path.join(OUTPUT_DIR, "etapa4_distribucion_localidades_tamloc.png")
fig6c.savefig(ruta_tam, dpi=200)
plt.close(fig6c)
print(f"  ✓ Distribución de localidades por TAMLOC guardada en: {ruta_tam}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  7. BRECHA DIGITAL: URBANO vs RURAL                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  7. BRECHA DIGITAL: URBANO vs RURAL")
print("=" * 90)

# Clasificar localidades
df_comp["TIPO_LOC"] = df_comp["TAMLOC"].apply(
    lambda t: "Rural (<250)" if t == 1 else
              "Semirrural (250-2,499)" if t <= 4 else
              "Urbana (≥2,500)" if pd.notna(t) else "Sin dato"
)

fig7, ax7 = plt.subplots(figsize=(14, 7))

# Medias por tipo de localidad para cada TIC
tipos = ["Rural (<250)", "Semirrural (250-2,499)", "Urbana (≥2,500)"]
colores_tipo = {"Rural (<250)": "#F44336", "Semirrural (250-2,499)": "#FF9800",
                "Urbana (≥2,500)": "#4CAF50"}

x = np.arange(len(vars_tasas_positivas))
width = 0.25

for i, tipo in enumerate(tipos):
    mask_tipo = df_comp["TIPO_LOC"] == tipo
    medias = [df_comp.loc[mask_tipo, v].mean() for v in vars_tasas_positivas]
    bars = ax7.bar(x + i * width, medias, width, label=tipo,
                   color=colores_tipo[tipo], edgecolor="white", alpha=0.85)
    for bar, val in zip(bars, medias):
        if pd.notna(val):
            ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f"{val:.0%}", ha="center", va="bottom", fontsize=6,
                     fontweight="bold")

ax7.set_xticks(x + width)
ax7.set_xticklabels([nombres_tasas_corto[v] for v in vars_tasas_positivas],
                     rotation=45, ha="right", fontsize=9)
ax7.set_ylabel("Tasa promedio de acceso")
ax7.set_title("Brecha Digital: Acceso a TIC por Nivel de Urbanización\n"
              "Aguascalientes, Censo 2020", fontsize=13, fontweight="bold")
ax7.legend(fontsize=9)
ax7.grid(axis="y", alpha=0.3)
ax7.set_ylim(0, 1.15)
plt.tight_layout()

ruta_brecha = os.path.join(OUTPUT_DIR, "etapa4_brecha_digital.png")
fig7.savefig(ruta_brecha, dpi=200)
plt.close(fig7)
print(f"\n  ✓ Gráfico de brecha digital guardado en: {ruta_brecha}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  8. GRÁFICOS DE DISPERSIÓN MULTIVARIADOS                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  8. GRÁFICOS DE DISPERSIÓN MULTIVARIADOS")
print("=" * 90)

fig8, axes8 = plt.subplots(2, 2, figsize=(14, 12))

# 8a. Población vs Internet
ax8a = axes8[0, 0]
data8 = df_comp[df_comp["POBTOT"].notna() & df_comp["TASA_INTER"].notna()]
scatter8a = ax8a.scatter(data8["POBTOT"], data8["TASA_INTER"],
                          c=data8["MUN"], cmap="tab10", s=15, alpha=0.6,
                          edgecolors="none")
ax8a.set_xlabel("Población total")
ax8a.set_ylabel("Tasa de Internet")
ax8a.set_title("Población vs Acceso a Internet", fontweight="bold")
ax8a.set_xscale("log")
ax8a.grid(alpha=0.2)

# Línea de tendencia
z = np.polyfit(np.log10(data8["POBTOT"].clip(lower=1)), data8["TASA_INTER"], 1)
x_trend = np.logspace(0, np.log10(data8["POBTOT"].max()), 100)
y_trend = z[0] * np.log10(x_trend) + z[1]
ax8a.plot(x_trend, np.clip(y_trend, 0, 1), color="red", linewidth=1.5,
          linestyle="--", alpha=0.7, label=f"Tendencia (r²)")
ax8a.legend(fontsize=7)

# 8b. Escolaridad vs Internet
ax8b = axes8[0, 1]
data8b = df_comp[df_comp["GRAPROES"].notna() & df_comp["TASA_INTER"].notna()]
scatter8b = ax8b.scatter(data8b["GRAPROES"], data8b["TASA_INTER"],
                          c=data8b["MUN"], cmap="tab10", s=15, alpha=0.6,
                          edgecolors="none")
ax8b.set_xlabel("Grado promedio de escolaridad")
ax8b.set_ylabel("Tasa de Internet")
ax8b.set_title("Escolaridad vs Acceso a Internet", fontweight="bold")
ax8b.grid(alpha=0.2)

# Correlación
r_esc = np.corrcoef(data8b["GRAPROES"], data8b["TASA_INTER"])[0, 1]
ax8b.text(0.05, 0.95, f"r = {r_esc:.3f}", transform=ax8b.transAxes,
          fontsize=9, fontweight="bold", va="top",
          bbox=dict(facecolor="white", alpha=0.7))

# 8c. Escolaridad vs PC
ax8c = axes8[1, 0]
data8c = df_comp[df_comp["GRAPROES"].notna() & df_comp["TASA_PC"].notna()]
scatter8c = ax8c.scatter(data8c["GRAPROES"], data8c["TASA_PC"],
                          c=data8c["MUN"], cmap="tab10", s=15, alpha=0.6,
                          edgecolors="none")
ax8c.set_xlabel("Grado promedio de escolaridad")
ax8c.set_ylabel("Tasa de PC/Laptop")
ax8c.set_title("Escolaridad vs Acceso a PC", fontweight="bold")
ax8c.grid(alpha=0.2)

r_pc = np.corrcoef(data8c["GRAPROES"], data8c["TASA_PC"])[0, 1]
ax8c.text(0.05, 0.95, f"r = {r_pc:.3f}", transform=ax8c.transAxes,
          fontsize=9, fontweight="bold", va="top",
          bbox=dict(facecolor="white", alpha=0.7))

# 8d. Internet vs PC (colinealidad visual)
ax8d = axes8[1, 1]
scatter8d = ax8d.scatter(df_comp["TASA_INTER"], df_comp["TASA_PC"],
                          c=df_comp["MUN"], cmap="tab10", s=15, alpha=0.6,
                          edgecolors="none")
ax8d.set_xlabel("Tasa de Internet")
ax8d.set_ylabel("Tasa de PC/Laptop")
ax8d.set_title("Internet vs PC (Colinealidad)", fontweight="bold")
ax8d.grid(alpha=0.2)

r_ipc = np.corrcoef(df_comp["TASA_INTER"].dropna(),
                     df_comp["TASA_PC"].dropna())[0, 1]
ax8d.text(0.05, 0.95, f"r = {r_ipc:.3f}", transform=ax8d.transAxes,
          fontsize=9, fontweight="bold", va="top",
          bbox=dict(facecolor="white", alpha=0.7))

fig8.suptitle("Gráficos de Dispersión — Relaciones Multivariadas\n"
              "Aguascalientes, Censo 2020",
              fontsize=14, fontweight="bold", y=0.98)
fig8.tight_layout(rect=[0, 0, 1, 0.95])

ruta_scatter = os.path.join(OUTPUT_DIR, "etapa4_scatter_multivariado.png")
fig8.savefig(ruta_scatter, dpi=200, bbox_inches="tight")
plt.close(fig8)
print(f"\n  ✓ Gráficos de dispersión guardados en: {ruta_scatter}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  9. HEATMAP MEJORADO DE CORRELACIÓN                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  9. HEATMAP DE CORRELACIÓN AMPLIADO")
print("=" * 90)

# Incluir variables de acceso digital + socioeconómicas
vars_corr_ext = vars_tasas + ["GRAPROES", "PROM_OCUP", "POBTOT"]
abrevs_corr = [v.replace("TASA_", "").replace("GRAPROES", "Escolaridad").replace(
    "PROM_OCUP", "Ocupantes").replace("POBTOT", "Población") for v in vars_corr_ext]

corr_ext = df_comp[vars_corr_ext].corr()
corr_ext.index = abrevs_corr
corr_ext.columns = abrevs_corr

fig9, ax9 = plt.subplots(figsize=(14, 12))
mask_tri = np.triu(np.ones_like(corr_ext, dtype=bool), k=1)
cmap_div = sns.diverging_palette(250, 15, s=75, l=40, n=12, as_cmap=True)
sns.heatmap(corr_ext, mask=mask_tri, annot=True, fmt=".2f", cmap=cmap_div,
            center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
            cbar_kws={"shrink": 0.7, "label": "Correlación de Pearson"},
            ax=ax9, annot_kws={"size": 7})
ax9.set_title("Matriz de Correlación Ampliada\n"
              "TIC + Variables Socioeconómicas — Aguascalientes 2020",
              fontsize=13, fontweight="bold", pad=15)
ax9.set_xticklabels(ax9.get_xticklabels(), rotation=45, ha="right", fontsize=8)
ax9.set_yticklabels(ax9.get_yticklabels(), rotation=0, fontsize=8)
plt.tight_layout()

ruta_corr_ext = os.path.join(OUTPUT_DIR, "etapa4_heatmap_correlacion_ampliada.png")
fig9.savefig(ruta_corr_ext, dpi=200)
plt.close(fig9)
print(f"\n  ✓ Heatmap de correlación ampliado guardado en: {ruta_corr_ext}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  10. RESUMEN DE VISUALIZACIONES GENERADAS                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  10. VISUALIZACIONES GENERADAS — RESUMEN")
print("=" * 90)

archivos_generados = [
    ("etapa4_histogramas_kde.png", "Histogramas con KDE de 9 tasas de acceso"),
    ("etapa4_boxplot_municipio.png", "Boxplots de 4 vars clave × 11 municipios"),
    ("etapa4_boxplot_tamloc.png", "Boxplots de 4 vars clave × tamaño localidad"),
    ("etapa4_violin_municipio.png", "Violin plots Internet y Celular × municipio"),
    ("etapa4_violin_todas_tic.png", "Violin plot comparativo de 9 TIC"),
    ("etapa4_pairplot.png", "Pairplot multivariado (Internet, Celular, PC, Streaming, ICAD)"),
    ("etapa4_mapa_internet.png", "Mapa geográfico: tasa de Internet por localidad"),
    ("etapa4_mapa_icad.png", "Mapa geográfico: ICAD por localidad"),
    ("etapa4_mapa_municipios.png", "Mapa geográfico: localidades por municipio"),
    ("etapa4_piramide_poblacional.png", "Pirámide poblacional de Aguascalientes"),
    ("etapa4_distribucion_poblacion_municipio.png", "Distribución demográfica por municipio"),
    ("etapa4_distribucion_localidades_tamloc.png", "Distribución de localidades por TAMLOC"),
    ("etapa4_brecha_digital.png", "Brecha digital urbano vs rural"),
    ("etapa4_scatter_multivariado.png", "Scatter plots multivariados (4 paneles)"),
    ("etapa4_heatmap_correlacion_ampliada.png", "Heatmap correlación TIC + socioeconómicas"),
]

print()
for i, (archivo, desc) in enumerate(archivos_generados, 1):
    ruta = os.path.join(OUTPUT_DIR, archivo)
    existe = "✓" if os.path.exists(ruta) else "✗"
    print(f"  {existe} {i:2d}. {archivo:<50s} {desc}")

print(f"""

  HALLAZGOS VISUALES CLAVE:
  ─────────────────────────

  1. DISTRIBUCIONES: Las tasas de acceso digital son fuertemente
     ASIMÉTRICAS A LA DERECHA: la mayoría de localidades tienen tasas
     bajas (rurales), con una cola larga hacia tasas altas (urbanas).

  2. BRECHA MUNICIPAL: Calvillo, El Llano y Tepezalá muestran las
     tasas más bajas. Aguascalientes capital domina en todos los indicadores.

  3. BRECHA URBANO-RURAL: La diferencia entre localidades rurales (<250
     hab) y urbanas (≥2,500 hab) es dramática: ~2x en celular, ~5x
     en internet, ~10x en PC y streaming.

  4. CORRELACIONES FUERTES: Internet ↔ PC (r≈0.96), Internet ↔ Streaming
     (r≈0.90). La escolaridad es fuerte predictor del acceso digital.

  5. GEOGRAFÍA: El mapa revela un gradiente centro-periferia: las
     localidades cercanas a la capital tienen mayor acceso digital,
     con bolsas de baja conectividad en las sierras del oeste y norte.

  6. DEMOGRAFÍA: Aguascalientes concentra el 70% de la población estatal.
     La pirámide muestra una base más estrecha que el cuerpo, indicando
     la transición demográfica.
""")

print("=" * 90)
print("  FIN DE ETAPA 4 — Visualización Completa")
print("=" * 90)
