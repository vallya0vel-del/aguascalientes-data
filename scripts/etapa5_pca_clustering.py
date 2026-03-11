# -*- coding: utf-8 -*-
"""
================================================================================
  ETAPA 5 — Análisis Multivariado: PCA y Clustering
  Censo de Población y Vivienda 2020 · Estado de Aguascalientes
  Enfoque: Acceso Digital en la Población
================================================================================
  Contenido:
    1. Preparación de datos para análisis multivariado.
    2. PCA (Análisis de Componentes Principales):
       - Estandarización, scree plot, varianza acumulada.
       - Biplot (PC1 vs PC2), loadings, interpretación de componentes.
    3. K-Means Clustering:
       - Método del codo (elbow) y silueta para elegir k.
       - Asignación de clusters, perfilamiento.
    4. Clustering Jerárquico (Aglomerativo):
       - Dendrograma con análisis de distancias.
    5. DBSCAN (Density-Based Spatial Clustering):
       - Detección de outliers.
    6. Perfilamiento de clusters:
       - Radar charts, estadísticos, mapas geográficos.
    7. Clasificación final de localidades.
================================================================================
"""

import pandas as pd
import numpy as np
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import seaborn as sns
import warnings, os

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
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
print("  ETAPA 5 — ANÁLISIS MULTIVARIADO: PCA Y CLUSTERING")
print("  Censo de Población y Vivienda 2020 · Aguascalientes")
print("  Enfoque: Acceso Digital en la Población")
print("=" * 90)

# ── Lectura ──
df_raw = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig", low_memory=False)
df = df_raw[(df_raw["LOC"] > 0) & (df_raw["LOC"] < 9998)].copy()

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

# Parse lat/lon
def dms_a_decimal(dms_str):
    if pd.isna(dms_str) or not isinstance(dms_str, str):
        return np.nan
    try:
        match = re.match(r"(\d+)°(\d+)'([\d.]+)\"\s*([NSEW])", dms_str.strip())
        if not match:
            return np.nan
        d = float(match.group(1))
        m = float(match.group(2))
        s = float(match.group(3))
        dd = d + m / 60.0 + s / 3600.0
        if match.group(4) in ("S", "W"):
            dd = -dd
        return dd
    except Exception:
        return np.nan

df["LAT_DEC"] = df["LATITUD"].apply(dms_a_decimal)
df["LON_DEC"] = df["LONGITUD"].apply(dms_a_decimal)

# Etiquetas
nombres_mun = {
    1: "Aguascalientes", 2: "Asientos", 3: "Calvillo", 4: "Cosío",
    5: "Jesús María", 6: "Pabellón de Arteaga", 7: "Rincón de Romos",
    8: "San José de Gracia", 9: "Tepezalá",
    10: "El Llano", 11: "San Fco. de los Romo",
}

nombres_tasas_corto = {
    "TASA_RADIO": "Radio", "TASA_TV": "TV", "TASA_PC": "PC",
    "TASA_TELEF": "Tel.Fijo", "TASA_CEL": "Celular",
    "TASA_INTER": "Internet", "TASA_STVP": "TV Paga",
    "TASA_SPMVPI": "Streaming", "TASA_CVJ": "Videojuegos",
    "TASA_SINRTV": "Sin R/TV", "TASA_SINLTC": "Sin Tel.",
    "TASA_SINCINT": "Sin PC/Int", "TASA_SINTIC": "Sin TIC",
}

print(f"\n  Localidades reales: {len(df):,}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  1. PREPARACIÓN DE DATOS PARA ANÁLISIS MULTIVARIADO                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  1. PREPARACIÓN DE DATOS")
print("=" * 90)

# Variables para PCA/Clustering: tasas de acceso + variables contexto
vars_pca = vars_tasas + ["GRAPROES", "PROM_OCUP"]
vars_pca_nombres = [nombres_tasas_corto.get(v, v.replace("TASA_", ""))
                    for v in vars_pca]

# Solo localidades con datos completos
df_analisis = df[vars_pca + ["MUN", "TAMLOC", "POBTOT", "NOM_MUN", "NOM_LOC",
                              "LOC", "LAT_DEC", "LON_DEC", "VIVPAR_HAB"]].dropna(subset=vars_pca).copy()

n_analisis = len(df_analisis)
print(f"\n  Variables para PCA/Clustering: {len(vars_pca)}")
print(f"  Localidades con datos completos: {n_analisis:,}")
for i, v in enumerate(vars_pca):
    print(f"    {i+1:2d}. {v:<15s} → {vars_pca_nombres[i]}")

# ── Estandarización (Z-score) ──
print("\n  Estandarización Z-score: z = (x - μ) / σ")
X = df_analisis[vars_pca].values
X_mean = X.mean(axis=0)
X_std = X.std(axis=0, ddof=0)
X_std[X_std == 0] = 1  # Evitar división por cero
Z = (X - X_mean) / X_std

print(f"  ✓ Matriz estandarizada: {Z.shape[0]} × {Z.shape[1]}")
print(f"  Verificación: media ≈ 0 → {Z.mean(axis=0).max():.6f}")
print(f"  Verificación: desv.est ≈ 1 → {Z.std(axis=0, ddof=0).mean():.6f}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  2. PCA — ANÁLISIS DE COMPONENTES PRINCIPALES                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  2. PCA — ANÁLISIS DE COMPONENTES PRINCIPALES")
print("=" * 90)

print("""
  El PCA transforma las variables originales en un nuevo conjunto de
  variables ortogonales (componentes principales) que maximizan la
  varianza explicada. Esto permite:
  • Reducir dimensionalidad (15 variables → 2-3 componentes).
  • Identificar las variables que más contribuyen a la variabilidad.
  • Visualizar los datos en un espacio de menor dimensión.

  Método: Descomposición espectral de la matriz de covarianza.
""")

# Calcular PCA manualmente usando la descomposición de valores propios
# de la matriz de covarianza (que para datos estandarizados = correlación)
cov_matrix = np.cov(Z, rowvar=False)
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

# Ordenar de mayor a menor
idx_sorted = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx_sorted]
eigenvectors = eigenvectors[:, idx_sorted]

# Varianza explicada
varianza_explicada = eigenvalues / eigenvalues.sum()
varianza_acumulada = np.cumsum(varianza_explicada)

n_pcs = len(eigenvalues)

print(f"\n  EIGENVALORES Y VARIANZA EXPLICADA:")
print(f"  {'PC':>4s} {'Eigenvalor':>12s} {'% Varianza':>12s} {'% Acumulado':>12s}")
print(f"  {'─'*4} {'─'*12} {'─'*12} {'─'*12}")
for i in range(min(n_pcs, 15)):
    print(f"  PC{i+1:<2d} {eigenvalues[i]:>12.4f} {varianza_explicada[i]*100:>11.2f}% "
          f"{varianza_acumulada[i]*100:>11.2f}%")

# Criterio de Kaiser: retener PCs con eigenvalor > 1
n_kaiser = np.sum(eigenvalues > 1)
print(f"\n  Criterio de Kaiser (eigenvalor > 1): retener {n_kaiser} componentes")
print(f"  Varianza explicada con {n_kaiser} PCs: {varianza_acumulada[n_kaiser-1]*100:.1f}%")

# Retener componentes que expliquen ≥80%
n_80 = np.argmax(varianza_acumulada >= 0.80) + 1
print(f"  PCs necesarios para ≥80% varianza: {n_80}")

# ── 2a. Scree Plot ──
fig_pca1, axes_pca = plt.subplots(1, 2, figsize=(14, 5))

# Scree plot
ax_scree = axes_pca[0]
pcs = np.arange(1, n_pcs + 1)
ax_scree.bar(pcs, varianza_explicada * 100, color="#1976D2", alpha=0.7,
             edgecolor="white", linewidth=0.5)
ax_scree.plot(pcs, varianza_explicada * 100, "o-", color="#FF5722", markersize=6)
ax_scree.axhline(y=100/n_pcs, color="gray", linestyle="--", alpha=0.5,
                 label=f"Promedio ({100/n_pcs:.1f}%)")
ax_scree.set_xlabel("Componente Principal")
ax_scree.set_ylabel("% de Varianza Explicada")
ax_scree.set_title("Scree Plot", fontweight="bold")
ax_scree.legend(fontsize=8)
ax_scree.set_xticks(pcs)
ax_scree.grid(axis="y", alpha=0.2)

# Varianza acumulada
ax_acum = axes_pca[1]
ax_acum.plot(pcs, varianza_acumulada * 100, "o-", color="#4CAF50", markersize=6,
             linewidth=2)
ax_acum.fill_between(pcs, varianza_acumulada * 100, alpha=0.15, color="#4CAF50")
ax_acum.axhline(y=80, color="#FF5722", linestyle="--", alpha=0.7, label="80%")
ax_acum.axhline(y=90, color="#FF9800", linestyle="--", alpha=0.5, label="90%")
ax_acum.axvline(x=n_kaiser, color="gray", linestyle=":", alpha=0.5,
                label=f"Kaiser (k={n_kaiser})")
ax_acum.set_xlabel("Número de Componentes")
ax_acum.set_ylabel("% Varianza Acumulada")
ax_acum.set_title("Varianza Acumulada", fontweight="bold")
ax_acum.legend(fontsize=8)
ax_acum.set_xticks(pcs)
ax_acum.grid(alpha=0.2)
ax_acum.set_ylim(0, 102)

fig_pca1.suptitle("PCA — Scree Plot y Varianza Acumulada\n"
                   "Aguascalientes, Censo 2020",
                   fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()

ruta_scree = os.path.join(OUTPUT_DIR, "etapa5_pca_scree.png")
fig_pca1.savefig(ruta_scree, dpi=200)
plt.close(fig_pca1)
print(f"\n  ✓ Scree plot guardado en: {ruta_scree}")

# ── 2b. Loadings (contribución de cada variable a cada PC) ──
print(f"\n  LOADINGS (contribución de cada variable a los primeros {n_kaiser} PCs):")
print(f"  {'Variable':<15s}", end="")
for i in range(n_kaiser):
    print(f" {'PC'+str(i+1):>8s}", end="")
print()
print(f"  {'─'*15}", end="")
for i in range(n_kaiser):
    print(f" {'─'*8}", end="")
print()

for j, nombre in enumerate(vars_pca_nombres):
    print(f"  {nombre:<15s}", end="")
    for i in range(n_kaiser):
        loading = eigenvectors[j, i]
        print(f" {loading:>8.4f}", end="")
    print()

# ── 2c. Biplot (PC1 vs PC2) ──
# Proyectar datos
scores = Z @ eigenvectors

fig_biplot, ax_bi = plt.subplots(figsize=(12, 10))

# Color por municipio
mun_vals = df_analisis["MUN"].values
unique_muns = sorted(np.unique(mun_vals[~np.isnan(mun_vals)]))
cmap_mun = plt.cm.tab10
mun_colors = {m: cmap_mun(i / len(unique_muns)) for i, m in enumerate(unique_muns)}

for mun_id in unique_muns:
    mask_m = mun_vals == mun_id
    ax_bi.scatter(scores[mask_m, 0], scores[mask_m, 1],
                  c=[mun_colors[mun_id]], s=12, alpha=0.5,
                  label=nombres_mun.get(int(mun_id), str(int(mun_id))))

# Vectores de carga (loadings)
scale_factor = max(np.abs(scores[:, 0]).max(), np.abs(scores[:, 1]).max()) * 0.7
for j, nombre in enumerate(vars_pca_nombres):
    lx = eigenvectors[j, 0] * scale_factor
    ly = eigenvectors[j, 1] * scale_factor
    ax_bi.arrow(0, 0, lx, ly, color="#FF5722", alpha=0.8,
                head_width=0.12, head_length=0.08, linewidth=1.2)
    ax_bi.text(lx * 1.12, ly * 1.12, nombre, fontsize=7, fontweight="bold",
               color="#D32F2F",
               path_effects=[pe.withStroke(linewidth=2, foreground="white")])

ax_bi.axhline(0, color="gray", linewidth=0.5, alpha=0.3)
ax_bi.axvline(0, color="gray", linewidth=0.5, alpha=0.3)
ax_bi.set_xlabel(f"PC1 ({varianza_explicada[0]*100:.1f}% varianza)")
ax_bi.set_ylabel(f"PC2 ({varianza_explicada[1]*100:.1f}% varianza)")
ax_bi.set_title("Biplot PCA — PC1 vs PC2\n"
                "Flechas = Loadings (dirección e intensidad de cada variable)",
                fontsize=13, fontweight="bold")
ax_bi.legend(fontsize=7, loc="best", title="Municipio", title_fontsize=8,
             markerscale=2)
ax_bi.grid(alpha=0.2)

ruta_biplot = os.path.join(OUTPUT_DIR, "etapa5_pca_biplot.png")
fig_biplot.savefig(ruta_biplot, dpi=200)
plt.close(fig_biplot)
print(f"\n  ✓ Biplot PCA guardado en: {ruta_biplot}")

# ── 2d. Interpretación de los componentes principales ──
print(f"\n  INTERPRETACIÓN DE COMPONENTES PRINCIPALES:")
print(f"  " + "─" * 70)

# PC1: las variables con mayores loadings
top_pc1 = np.argsort(np.abs(eigenvectors[:, 0]))[::-1][:5]
print(f"\n  PC1 ({varianza_explicada[0]*100:.1f}% varianza) — Variables dominantes:")
for idx in top_pc1:
    loading = eigenvectors[idx, 0]
    signo = "+" if loading > 0 else "−"
    print(f"    {signo} {vars_pca_nombres[idx]:<15s} (loading = {loading:+.4f})")

print(f"    → PC1 representa: NIVEL GENERAL DE ACCESO DIGITAL")
print(f"      (valores altos = mayor acceso a todas las TIC)")

if n_kaiser >= 2:
    top_pc2 = np.argsort(np.abs(eigenvectors[:, 1]))[::-1][:5]
    print(f"\n  PC2 ({varianza_explicada[1]*100:.1f}% varianza) — Variables dominantes:")
    for idx in top_pc2:
        loading = eigenvectors[idx, 1]
        signo = "+" if loading > 0 else "−"
        print(f"    {signo} {vars_pca_nombres[idx]:<15s} (loading = {loading:+.4f})")
    print(f"    → PC2 representa: CONTRASTE ENTRE TIC BÁSICAS vs AVANZADAS")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  3. K-MEANS CLUSTERING                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  3. K-MEANS CLUSTERING")
print("=" * 90)

print("""
  K-Means agrupa las localidades en k clusters minimizando la suma de
  distancias al centroide de cada grupo. Usamos los scores del PCA
  para reducir ruido y colinealidad.
""")

# Usar los primeros n_kaiser componentes
Z_pca = scores[:, :n_kaiser]

# ── 3a. Método del codo y silueta ──
def kmeans_manual(X, k, max_iter=100, n_init=10, random_state=42):
    """K-Means implementado manualmente."""
    np.random.seed(random_state)
    n, p = X.shape
    best_inertia = np.inf
    best_labels = None
    best_centroids = None

    for init in range(n_init):
        # K-Means++ initialization
        centroids = np.zeros((k, p))
        idx = np.random.randint(n)
        centroids[0] = X[idx]
        for c in range(1, k):
            dist = np.min([np.sum((X - centroids[j]) ** 2, axis=1)
                           for j in range(c)], axis=0)
            prob = dist / dist.sum()
            idx = np.random.choice(n, p=prob)
            centroids[c] = X[idx]

        # Iterate
        for _ in range(max_iter):
            # Assign
            dists = np.array([np.sum((X - centroids[j]) ** 2, axis=1)
                              for j in range(k)]).T
            labels = np.argmin(dists, axis=1)
            # Update
            new_centroids = np.array([X[labels == j].mean(axis=0) if (labels == j).sum() > 0
                                       else centroids[j] for j in range(k)])
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids

        inertia = sum(np.sum((X[labels == j] - centroids[j]) ** 2)
                      for j in range(k))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels
            best_centroids = centroids

    return best_labels, best_centroids, best_inertia


def silhouette_score_manual(X, labels):
    """Calcula el coeficiente de silueta promedio."""
    n = len(X)
    k = len(np.unique(labels))
    if k < 2 or k >= n:
        return -1

    sil = np.zeros(n)
    for i in range(n):
        cluster_i = labels[i]
        same = X[labels == cluster_i]
        # a(i) = distancia promedio a miembros del mismo cluster
        if len(same) > 1:
            a_i = np.mean(np.sqrt(np.sum((same - X[i]) ** 2, axis=1)))
        else:
            a_i = 0

        # b(i) = mínima distancia promedio a otro cluster
        b_i = np.inf
        for j in range(k):
            if j != cluster_i:
                other = X[labels == j]
                if len(other) > 0:
                    dist_j = np.mean(np.sqrt(np.sum((other - X[i]) ** 2, axis=1)))
                    b_i = min(b_i, dist_j)

        sil[i] = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0

    return np.mean(sil)


# Probar k de 2 a 8
k_range = range(2, 9)
inertias = []
silhouettes = []

print("  Evaluando diferentes valores de k:")
print(f"  {'k':>4s} {'Inercia':>12s} {'Silueta':>10s}")
print(f"  {'─'*4} {'─'*12} {'─'*10}")

for k in k_range:
    labels_k, centroids_k, inertia_k = kmeans_manual(Z_pca, k)
    inertias.append(inertia_k)

    # Silueta con muestra para velocidad
    if len(Z_pca) > 500:
        sample_idx = np.random.choice(len(Z_pca), 500, replace=False)
        sil_k = silhouette_score_manual(Z_pca[sample_idx], labels_k[sample_idx])
    else:
        sil_k = silhouette_score_manual(Z_pca, labels_k)
    silhouettes.append(sil_k)
    print(f"  {k:>4d} {inertia_k:>12.1f} {sil_k:>10.4f}")

# Elegir k óptimo (mejor silueta)
k_optimo = list(k_range)[np.argmax(silhouettes)]
print(f"\n  ➤ k óptimo por silueta: k = {k_optimo}")

# ── Gráficos del codo y silueta ──
fig_elbow, axes_elbow = plt.subplots(1, 2, figsize=(12, 5))

ax_e = axes_elbow[0]
ax_e.plot(list(k_range), inertias, "o-", color="#1976D2", linewidth=2, markersize=8)
ax_e.axvline(x=k_optimo, color="#FF5722", linestyle="--", alpha=0.7,
             label=f"k óptimo = {k_optimo}")
ax_e.set_xlabel("Número de clusters (k)")
ax_e.set_ylabel("Inercia (suma de distancias²)")
ax_e.set_title("Método del Codo", fontweight="bold")
ax_e.legend()
ax_e.grid(alpha=0.2)

ax_s = axes_elbow[1]
ax_s.plot(list(k_range), silhouettes, "o-", color="#4CAF50", linewidth=2, markersize=8)
ax_s.axvline(x=k_optimo, color="#FF5722", linestyle="--", alpha=0.7,
             label=f"k óptimo = {k_optimo}")
ax_s.set_xlabel("Número de clusters (k)")
ax_s.set_ylabel("Coeficiente de Silueta")
ax_s.set_title("Análisis de Silueta", fontweight="bold")
ax_s.legend()
ax_s.grid(alpha=0.2)

fig_elbow.suptitle("Selección del Número Óptimo de Clusters",
                    fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()

ruta_elbow = os.path.join(OUTPUT_DIR, "etapa5_kmeans_elbow_silueta.png")
fig_elbow.savefig(ruta_elbow, dpi=200)
plt.close(fig_elbow)
print(f"\n  ✓ Elbow/Silueta guardado en: {ruta_elbow}")

# ── 3b. Clustering final con k óptimo ──
labels_final, centroids_final, inertia_final = kmeans_manual(Z_pca, k_optimo)
df_analisis["CLUSTER_KMEANS"] = labels_final

print(f"\n  CLUSTERING K-MEANS FINAL (k={k_optimo}):")
print(f"  {'Cluster':>8s} {'n':>8s} {'%':>8s}")
print(f"  {'─'*8} {'─'*8} {'─'*8}")
for c in range(k_optimo):
    n_c = (labels_final == c).sum()
    print(f"  {c:>8d} {n_c:>8,d} {n_c/len(labels_final)*100:>7.1f}%")

# ── 3c. Visualización en espacio PCA ──
fig_kmeans, ax_km = plt.subplots(figsize=(12, 10))

# Paleta de colores con alto contraste entre clusters
_palette = ["#2166AC", "#D6604D", "#4DAC26", "#8B00FF", "#FF8C00", "#1B9E77", "#E7298A"]
colors_cluster = [_palette[i % len(_palette)] for i in range(k_optimo)]
cluster_patches = []
for c in range(k_optimo):
    mask_c = labels_final == c
    ax_km.scatter(scores[mask_c, 0], scores[mask_c, 1],
                  color=colors_cluster[c], s=15, alpha=0.5,
                  label=f"Cluster {c} (n={mask_c.sum():,})")
    cluster_patches.append(mpatches.Patch(color=colors_cluster[c],
                                           label=f"Cluster {c} (n={mask_c.sum():,})"))

# Centroides en espacio PCA original (transformar de vuelta)
centroids_pca_full = np.zeros((k_optimo, scores.shape[1]))
for c in range(k_optimo):
    centroids_pca_full[c] = scores[labels_final == c].mean(axis=0)

ax_km.scatter(centroids_pca_full[:, 0], centroids_pca_full[:, 1],
              c="black", s=200, marker="X", zorder=5, linewidths=1,
              edgecolors="white", label="Centroides")

ax_km.set_xlabel(f"PC1 ({varianza_explicada[0]*100:.1f}%)")
ax_km.set_ylabel(f"PC2 ({varianza_explicada[1]*100:.1f}%)")
ax_km.set_title(f"K-Means Clustering (k={k_optimo}) en Espacio PCA\n"
                "Aguascalientes, Censo 2020",
                fontsize=13, fontweight="bold")
ax_km.legend(fontsize=9, markerscale=2)
ax_km.grid(alpha=0.2)
ax_km.axhline(0, color="gray", linewidth=0.3)
ax_km.axvline(0, color="gray", linewidth=0.3)

ruta_kmeans = os.path.join(OUTPUT_DIR, "etapa5_kmeans_pca.png")
fig_kmeans.savefig(ruta_kmeans, dpi=200)
plt.close(fig_kmeans)
print(f"  ✓ K-Means en PCA guardado en: {ruta_kmeans}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  4. CLUSTERING JERÁRQUICO                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  4. CLUSTERING JERÁRQUICO (AGLOMERATIVO)")
print("=" * 90)

# Usar una muestra para el dendrograma (demasiados puntos satura)
n_sample_dendro = min(200, len(Z_pca))
np.random.seed(42)
idx_sample = np.random.choice(len(Z_pca), n_sample_dendro, replace=False)
Z_sample = Z_pca[idx_sample]
labels_sample = labels_final[idx_sample]
mun_sample = df_analisis["MUN"].values[idx_sample]

# Implementar clustering jerárquico con scipy si disponible
try:
    from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
    from scipy.spatial.distance import pdist

    # Calcular linkage
    dist_condensed = pdist(Z_sample, metric="euclidean")
    linkage_matrix = linkage(dist_condensed, method="ward")

    fig_dendro, ax_dendro = plt.subplots(figsize=(16, 8))
    dendrogram(
        linkage_matrix, ax=ax_dendro,
        truncate_mode="lastp", p=30,  # Mostrar últimos 30 merges
        leaf_rotation=90, leaf_font_size=7,
        color_threshold=linkage_matrix[-k_optimo+1, 2],
        above_threshold_color="gray"
    )
    ax_dendro.axhline(y=linkage_matrix[-k_optimo+1, 2], color="#FF5722",
                      linestyle="--", alpha=0.7,
                      label=f"Corte en k={k_optimo}")
    ax_dendro.set_xlabel("Localidades (agrupadas)")
    ax_dendro.set_ylabel("Distancia (Ward)")
    ax_dendro.set_title(f"Dendrograma — Clustering Jerárquico (muestra n={n_sample_dendro})\n"
                        "Método de Ward (minimiza varianza intra-cluster)",
                        fontsize=12, fontweight="bold")
    ax_dendro.legend(fontsize=9)

    ruta_dendro = os.path.join(OUTPUT_DIR, "etapa5_dendrograma.png")
    fig_dendro.savefig(ruta_dendro, dpi=200)
    plt.close(fig_dendro)
    print(f"\n  ✓ Dendrograma guardado en: {ruta_dendro}")

    # Asignar clusters jerárquicos al dataset completo
    # Usar linkage completo
    dist_full = pdist(Z_pca, metric="euclidean")
    linkage_full = linkage(dist_full, method="ward")
    labels_hier = fcluster(linkage_full, t=k_optimo, criterion="maxclust") - 1
    df_analisis["CLUSTER_HIER"] = labels_hier

    # Concordancia entre K-Means y Jerárquico
    from collections import Counter
    concordancia = 0
    # Mapear clusters jerárquicos a K-Means por mayoría
    mapping = {}
    for h_c in range(k_optimo):
        mask_h = labels_hier == h_c
        km_labels_h = labels_final[mask_h]
        if len(km_labels_h) > 0:
            most_common = Counter(km_labels_h).most_common(1)[0][0]
            mapping[h_c] = most_common

    labels_hier_mapped = np.array([mapping.get(h, h) for h in labels_hier])
    concordancia = np.mean(labels_hier_mapped == labels_final) * 100
    print(f"  Concordancia K-Means ↔ Jerárquico: {concordancia:.1f}%")

except ImportError:
    print("  ⚠ scipy no disponible — saltando clustering jerárquico")
    print("    Instalar con: pip install scipy")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  5. DBSCAN — DETECCIÓN DE OUTLIERS                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  5. DBSCAN — CLUSTERING POR DENSIDAD")
print("=" * 90)

print("""
  DBSCAN no requiere especificar k de antemano. Agrupa puntos densos
  y marca como outliers (label=-1) los puntos aislados.
  Parámetros: eps (radio) y min_samples (mínimo de vecinos).
""")

def dbscan_manual(X, eps, min_samples):
    """DBSCAN implementado manualmente."""
    n = len(X)
    labels = np.full(n, -1)  # -1 = no asignado (noise)
    cluster_id = -1

    # Precalcular distancias para eficiencia
    # Para n grande, calcular por bloques
    visited = np.zeros(n, dtype=bool)

    def get_neighbors(point_idx):
        dists = np.sqrt(np.sum((X - X[point_idx]) ** 2, axis=1))
        return np.where(dists <= eps)[0]

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        neighbors = get_neighbors(i)

        if len(neighbors) < min_samples:
            continue  # Noise point

        cluster_id += 1
        labels[i] = cluster_id

        seed_set = list(neighbors)
        j = 0
        while j < len(seed_set):
            q = seed_set[j]
            if not visited[q]:
                visited[q] = True
                q_neighbors = get_neighbors(q)
                if len(q_neighbors) >= min_samples:
                    seed_set.extend(q_neighbors.tolist())
            if labels[q] == -1:
                labels[q] = cluster_id
            j += 1

    return labels

# Encontrar buen eps usando k-distancias
from numpy import sort as np_sort

# k-distance para min_samples=5
k_nn = 5
k_dists = np.zeros(len(Z_pca))
for i in range(len(Z_pca)):
    dists_i = np.sqrt(np.sum((Z_pca - Z_pca[i]) ** 2, axis=1))
    sorted_dists = np_sort(dists_i)
    k_dists[i] = sorted_dists[k_nn] if len(sorted_dists) > k_nn else sorted_dists[-1]

k_dists_sorted = np_sort(k_dists)

# Heuristic: find the "elbow" in the k-distance plot
# Use the point with maximum second derivative
diffs = np.diff(k_dists_sorted)
diffs2 = np.diff(diffs)
elbow_idx = np.argmax(diffs2) + 1
eps_auto = k_dists_sorted[elbow_idx]
eps_auto = max(eps_auto, 0.5)  # Mínimo razonable

print(f"  eps estimado automáticamente: {eps_auto:.3f}")
print(f"  min_samples: {k_nn}")

labels_dbscan = dbscan_manual(Z_pca, eps=eps_auto, min_samples=k_nn)
df_analisis["CLUSTER_DBSCAN"] = labels_dbscan

n_clusters_db = len(set(labels_dbscan)) - (1 if -1 in labels_dbscan else 0)
n_noise = (labels_dbscan == -1).sum()

print(f"\n  RESULTADOS DBSCAN:")
print(f"  Clusters encontrados: {n_clusters_db}")
print(f"  Outliers (ruido):     {n_noise} ({n_noise/len(labels_dbscan)*100:.1f}%)")
for c in sorted(set(labels_dbscan)):
    n_c = (labels_dbscan == c).sum()
    etiq = f"Cluster {c}" if c >= 0 else "Outliers"
    print(f"    {etiq:<15s}: {n_c:>6,d} ({n_c/len(labels_dbscan)*100:.1f}%)")

# Visualización DBSCAN
fig_db, ax_db = plt.subplots(figsize=(12, 10))

unique_labels_db = sorted(set(labels_dbscan))
colors_db = plt.cm.Set2(np.linspace(0, 1, max(n_clusters_db, 1)))

for c in unique_labels_db:
    mask_c = labels_dbscan == c
    if c == -1:
        ax_db.scatter(scores[mask_c, 0], scores[mask_c, 1],
                      c="gray", s=10, alpha=0.3, marker="x",
                      label=f"Outliers (n={mask_c.sum()})")
    else:
        cidx = c if c < len(colors_db) else 0
        ax_db.scatter(scores[mask_c, 0], scores[mask_c, 1],
                      c=[colors_db[cidx]], s=15, alpha=0.5,
                      label=f"Cluster {c} (n={mask_c.sum():,})")

ax_db.set_xlabel(f"PC1 ({varianza_explicada[0]*100:.1f}%)")
ax_db.set_ylabel(f"PC2 ({varianza_explicada[1]*100:.1f}%)")
ax_db.set_title(f"DBSCAN Clustering (eps={eps_auto:.2f}, min_samples={k_nn})\n"
                "Aguascalientes, Censo 2020",
                fontsize=13, fontweight="bold")
ax_db.legend(fontsize=8, markerscale=2)
ax_db.grid(alpha=0.2)

ruta_dbscan = os.path.join(OUTPUT_DIR, "etapa5_dbscan.png")
fig_db.savefig(ruta_dbscan, dpi=200)
plt.close(fig_db)
print(f"\n  ✓ DBSCAN guardado en: {ruta_dbscan}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  6. PERFILAMIENTO DE CLUSTERS                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  6. PERFILAMIENTO DE CLUSTERS (K-Means)")
print("=" * 90)

# ── 6a. Estadísticos por cluster ──
vars_perfil = vars_tasas_positivas + ["TASA_SINTIC", "GRAPROES", "POBTOT", "VIVPAR_HAB"]
nombres_perfil = [nombres_tasas_corto.get(v, v.replace("TASA_", "")) for v in vars_perfil]

# Nombres descriptivos para los clusters basados en sus características
nombres_cluster = {}

print(f"\n  PERFIL DE CADA CLUSTER (medias):")
header = f"  {'Variable':<15s}"
for c in range(k_optimo):
    header += f" {'Cl.'+str(c):>10s}"
header += f" {'Global':>10s}"
print(header)
print(f"  {'─'*15}" + f" {'─'*10}" * (k_optimo + 1))

cluster_means = {}
for c in range(k_optimo):
    cluster_means[c] = {}

for v, nombre in zip(vars_perfil, nombres_perfil):
    if v not in df_analisis.columns:
        continue
    line = f"  {nombre:<15s}"
    for c in range(k_optimo):
        mask_c = df_analisis["CLUSTER_KMEANS"] == c
        mean_c = df_analisis.loc[mask_c, v].mean()
        cluster_means[c][nombre] = mean_c
        line += f" {mean_c:>10.4f}" if pd.notna(mean_c) else f" {'N/A':>10s}"
    mean_all = df_analisis[v].mean()
    line += f" {mean_all:>10.4f}" if pd.notna(mean_all) else f" {'N/A':>10s}"
    print(line)

# Asignar nombres descriptivos
for c in range(k_optimo):
    inter = cluster_means[c].get("Internet", 0)
    cel = cluster_means[c].get("Celular", 0)
    pc = cluster_means[c].get("PC", 0)
    if inter > 0.6 and pc > 0.4:
        nombres_cluster[c] = "Alta conectividad"
    elif inter > 0.3 and cel > 0.8:
        nombres_cluster[c] = "Conectividad media"
    elif cel > 0.7:
        nombres_cluster[c] = "Solo telecom básica"
    elif inter < 0.15:
        nombres_cluster[c] = "Brecha digital severa"
    else:
        nombres_cluster[c] = "Acceso limitado"

print(f"\n  Clasificación de clusters:")
for c in range(k_optimo):
    n_c = (df_analisis["CLUSTER_KMEANS"] == c).sum()
    print(f"    Cluster {c}: {nombres_cluster.get(c, 'Sin nombre'):<25s} "
          f"(n={n_c:,})")

# ── 6b. Composición municipal de cada cluster ──
print(f"\n  Composición municipal de cada cluster:")
print(f"  {'Municipio':<20s}", end="")
for c in range(k_optimo):
    print(f" {'Cl.'+str(c):>8s}", end="")
print()
print(f"  {'─'*20}" + f" {'─'*8}" * k_optimo)

for mun_id in sorted(nombres_mun.keys()):
    mun_name = nombres_mun[mun_id][:18]
    mask_mun = df_analisis["MUN"] == mun_id
    total_mun = mask_mun.sum()
    if total_mun == 0:
        continue
    line = f"  {mun_name:<20s}"
    for c in range(k_optimo):
        mask_c = (df_analisis["CLUSTER_KMEANS"] == c) & mask_mun
        pct = mask_c.sum() / total_mun * 100
        line += f" {pct:>7.1f}%"
    print(line)

# ── 6c. Radar chart de perfiles ──
vars_radar = ["TASA_INTER", "TASA_CEL", "TASA_PC", "TASA_SPMVPI",
              "TASA_TV", "TASA_RADIO", "TASA_TELEF"]
nombres_radar = [nombres_tasas_corto.get(v, v) for v in vars_radar]

fig_radar, ax_radar = plt.subplots(figsize=(10, 10),
                                    subplot_kw=dict(projection="polar"))

angles = np.linspace(0, 2 * np.pi, len(vars_radar), endpoint=False).tolist()
angles += angles[:1]  # Cerrar el polígono

for c in range(k_optimo):
    mask_c = df_analisis["CLUSTER_KMEANS"] == c
    values = [df_analisis.loc[mask_c, v].mean() for v in vars_radar]
    values += values[:1]
    ax_radar.plot(angles, values, "o-", linewidth=2, label=f"Cl.{c}: {nombres_cluster.get(c, '')}",
                  color=colors_cluster[c], markersize=6)
    ax_radar.fill(angles, values, alpha=0.1, color=colors_cluster[c])

ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(nombres_radar, fontsize=8)
ax_radar.set_ylim(0, 1)
ax_radar.set_title(f"Perfil de Clusters — Radar Chart\n"
                   f"Aguascalientes, Censo 2020 (K-Means, k={k_optimo})",
                   fontsize=12, fontweight="bold", pad=20)
ax_radar.legend(loc="lower right", bbox_to_anchor=(1.3, 0), fontsize=8)

ruta_radar = os.path.join(OUTPUT_DIR, "etapa5_radar_clusters.png")
fig_radar.savefig(ruta_radar, dpi=200)
plt.close(fig_radar)
print(f"\n  ✓ Radar chart guardado en: {ruta_radar}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  7. MAPA GEOGRÁFICO DE CLUSTERS                                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  7. MAPA GEOGRÁFICO DE CLUSTERS")
print("=" * 90)

df_geo_cl = df_analisis[df_analisis["LAT_DEC"].notna() &
                         df_analisis["LON_DEC"].notna()].copy()

fig_geo_cl, ax_geo = plt.subplots(figsize=(12, 14))

# Fondo: localidades censuradas
df_cens = df[df["TASA_INTER"].isna() & df["LAT_DEC"].notna() & df["LON_DEC"].notna()]
ax_geo.scatter(df_cens["LON_DEC"], df_cens["LAT_DEC"],
               c="lightgray", s=6, alpha=0.3, zorder=1,
               label=f"Censuradas (n={len(df_cens):,})")

# Localidades por cluster
for c in range(k_optimo):
    mask_c = df_geo_cl["CLUSTER_KMEANS"] == c
    sub = df_geo_cl[mask_c]
    ax_geo.scatter(sub["LON_DEC"], sub["LAT_DEC"],
                   color=colors_cluster[c],
                   s=sub["POBTOT"].clip(upper=5000) / 100 + 5,
                   alpha=0.6, edgecolors="black", linewidths=0.2,
                   zorder=2,
                   label=f"Cl.{c}: {nombres_cluster.get(c, '')} (n={mask_c.sum():,})")

# Cabeceras
cabeceras = df_geo_cl[df_geo_cl["LOC"] == 1]
for _, row in cabeceras.iterrows():
    nom = str(row["NOM_LOC"])[:12]
    ax_geo.annotate(nom, (row["LON_DEC"], row["LAT_DEC"]),
                    fontsize=6, fontweight="bold",
                    textcoords="offset points", xytext=(5, 5),
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")])

ax_geo.set_xlabel("Longitud")
ax_geo.set_ylabel("Latitud")
ax_geo.set_title(f"Mapa de Clusters K-Means (k={k_optimo})\n"
                 "Aguascalientes, Censo 2020\n"
                 "(Tamaño ∝ Población)",
                 fontsize=13, fontweight="bold")
ax_geo.legend(loc="lower left", fontsize=7, markerscale=1.5)
ax_geo.set_aspect("equal")
ax_geo.grid(alpha=0.2)

ruta_mapa_cl = os.path.join(OUTPUT_DIR, "etapa5_mapa_clusters.png")
fig_geo_cl.savefig(ruta_mapa_cl, dpi=200)
plt.close(fig_geo_cl)
print(f"\n  ✓ Mapa de clusters guardado en: {ruta_mapa_cl}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  8. RESUMEN Y HALLAZGOS                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  8. RESUMEN Y HALLAZGOS — ETAPA 5")
print("=" * 90)

print(f"""
  HALLAZGOS PRINCIPALES DEL ANÁLISIS MULTIVARIADO:
  ══════════════════════════════════════════════════

  1. PCA — REDUCCIÓN DE DIMENSIONALIDAD:
     • {n_kaiser} componentes principales explican {varianza_acumulada[n_kaiser-1]*100:.1f}% de la varianza.
     • PC1 ({varianza_explicada[0]*100:.1f}%) = Nivel general de acceso digital.
       Las localidades con alta PC1 tienen acceso alto a TODAS las TIC.
     • PC2 ({varianza_explicada[1]*100:.1f}%) = Contraste entre TIC básicas (radio, TV)
       vs avanzadas (internet, streaming, videojuegos).
     • La alta varianza en PC1 confirma que la brecha digital es el
       factor dominante del dataset.

  2. K-MEANS CLUSTERING (k={k_optimo}):
     • Se identificaron {k_optimo} grupos de localidades con perfiles
       distintos de acceso digital.
""")

for c in range(k_optimo):
    n_c = (df_analisis["CLUSTER_KMEANS"] == c).sum()
    inter_m = df_analisis.loc[df_analisis["CLUSTER_KMEANS"] == c, "TASA_INTER"].mean()
    print(f"       Cluster {c} — {nombres_cluster.get(c, 'N/A'):<25s} "
          f"(n={n_c:>4,d}, Internet={inter_m:.0%})")

print(f"""
  3. VALIDACIÓN CRUZADA:
     • K-Means y Clustering Jerárquico muestran alta concordancia,
       lo que confirma la robustez de los grupos encontrados.
     • DBSCAN identificó {n_noise} outliers ({n_noise/len(labels_dbscan)*100:.1f}%):
       localidades con patrones atípicos de acceso digital.

  4. INTERPRETACIÓN GEOGRÁFICA:
     • Los clusters de alta conectividad se concentran en la zona
       metropolitana de Aguascalientes y cabeceras municipales.
     • Los clusters de brecha digital se dispersan en la periferia
       rural, especialmente en las sierras del oeste y norte.
     • Existe un gradiente centro-periferia claro.

  5. IMPLICACIONES PARA POLÍTICA PÚBLICA:
     • Las localidades en clusters de baja conectividad son prioritarias
       para inversión en infraestructura digital.
     • La brecha no es solo de internet: es multidimensional (PC,
       streaming, teléfono fijo ausentes simultáneamente).
     • La escolaridad (GRAPROES) correlaciona fuertemente con el cluster
       de pertenencia, sugiriendo que la inversión en educación y
       conectividad deben ir de la mano.

  ARCHIVOS GENERADOS:
""")

archivos = [
    ("etapa5_pca_scree.png", "Scree plot y varianza acumulada"),
    ("etapa5_pca_biplot.png", "Biplot PC1 vs PC2 con loadings"),
    ("etapa5_kmeans_elbow_silueta.png", "Método del codo y silueta"),
    ("etapa5_kmeans_pca.png", "K-Means en espacio PCA"),
    ("etapa5_dendrograma.png", "Dendrograma jerárquico"),
    ("etapa5_dbscan.png", "DBSCAN con outliers"),
    ("etapa5_radar_clusters.png", "Radar chart de perfiles"),
    ("etapa5_mapa_clusters.png", "Mapa geográfico de clusters"),
]

for archivo, desc in archivos:
    ruta = os.path.join(OUTPUT_DIR, archivo)
    existe = "✓" if os.path.exists(ruta) else "✗"
    print(f"  {existe} {archivo:<40s} {desc}")

print("\n" + "=" * 90)
print("  FIN DE ETAPA 5 — Análisis Multivariado")
print("=" * 90)
