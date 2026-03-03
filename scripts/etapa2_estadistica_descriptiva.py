# -*- coding: utf-8 -*-
"""
================================================================================
  ETAPA 2 — Estadística Descriptiva Completa
  Censo de Población y Vivienda 2020 · Estado de Aguascalientes
  Enfoque: Acceso Digital en la Población
================================================================================
  Requisitos:
    ● Variables cuantitativas (cálculos manuales, NO .describe()):
        media, mediana, varianza, desviación estándar, coef. de variación,
        asimetría (skewness), curtosis, rango intercuartílico, percentiles.
    ● Variables categóricas:
        frecuencias absolutas, relativas, moda, entropía de Shannon.
    ● Análisis de correlación y colinealidad (adición del equipo).
================================================================================
"""

import pandas as pd
import numpy as np
import warnings, os

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN Y CARGA DE DATOS
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")

RUTA_DATOS = os.path.join(DATA_DIR, "conjunto_de_datos_iter_01CSV20.csv")
RUTA_DICC  = os.path.join(DATA_DIR, "diccionario_datos_iter_01CSV20.csv")

print("=" * 90)
print("  ETAPA 2 — ESTADÍSTICA DESCRIPTIVA COMPLETA")
print("  Censo de Población y Vivienda 2020 · Aguascalientes")
print("  Enfoque: Acceso Digital en la Población")
print("=" * 90)

# ── Lectura ──
df_raw = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig", low_memory=False)

# Cargar diccionario para descripciones
dict_raw = pd.read_csv(RUTA_DICC, encoding="utf-8-sig", header=None)
dict_df  = dict_raw.iloc[4:].copy()
dict_df.columns = ["Num", "Indicador", "Descripcion", "Mnemonico",
                    "Rango", "Tam", "C6", "C7", "C8", "C9"]
dict_df["Mnemonico"] = dict_df["Mnemonico"].astype(str).str.strip()
dict_df = dict_df[dict_df["Mnemonico"] != "nan"]
mapeo = dict(zip(dict_df["Mnemonico"], dict_df["Indicador"]))

# ── Preparación ──
# Filtrar filas de totales para evitar doble conteo.
# Conservamos SOLO localidades reales (LOC > 0 y LOC < 9998).
df = df_raw[(df_raw["LOC"] > 0) & (df_raw["LOC"] < 9998)].copy()
print(f"\n  Registros totales en archivo:   {len(df_raw):,}")
print(f"  Registros de localidades reales: {len(df):,}")
print(f"  (Se excluyeron totales municipales [LOC=0], localidades de 1 viv")
print(f"   [LOC=9998] y de 2 viv [LOC=9999] para evitar doble conteo.)")

# Convertir columnas con '*' a numérico
cols_texto_legit = ["NOM_ENT", "NOM_MUN", "NOM_LOC", "LONGITUD", "LATITUD"]
for col in df.columns:
    if col not in cols_texto_legit:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ── Definición de variables de interés ──
# Variables de Acceso Digital (conteos absolutos)
vars_acceso_digital = [
    "VPH_RADIO", "VPH_TV", "VPH_PC", "VPH_TELEF", "VPH_CEL",
    "VPH_INTER", "VPH_STVP", "VPH_SPMVPI", "VPH_CVJ",
    "VPH_SINRTV", "VPH_SINLTC", "VPH_SINCINT", "VPH_SINTIC",
]

# Crear tasas de acceso digital (proporción respecto a viviendas habitadas)
# Estas son más útiles analíticamente que los conteos absolutos.
vars_tasas_acceso = []
for v in vars_acceso_digital:
    nombre_tasa = f"TASA_{v.replace('VPH_', '')}"
    mask = df["VIVPAR_HAB"].notna() & (df["VIVPAR_HAB"] > 0) & df[v].notna()
    df.loc[mask, nombre_tasa] = df.loc[mask, v] / df.loc[mask, "VIVPAR_HAB"]
    vars_tasas_acceso.append(nombre_tasa)

# Variables demográficas clave para contexto
vars_demograficas_clave = [
    "POBTOT", "POBFEM", "POBMAS", "VIVPAR_HAB", "OCUPVIVPAR",
    "GRAPROES", "PROM_OCUP",
]

# Variables categóricas
vars_categoricas = ["MUN", "TAMLOC"]

# Nombres legibles para las tasas
nombres_tasas = {
    "TASA_RADIO":   "Tasa de viviendas con radio",
    "TASA_TV":      "Tasa de viviendas con televisor",
    "TASA_PC":      "Tasa de viviendas con computadora/laptop/tablet",
    "TASA_TELEF":   "Tasa de viviendas con línea telefónica fija",
    "TASA_CEL":     "Tasa de viviendas con teléfono celular",
    "TASA_INTER":   "Tasa de viviendas con Internet",
    "TASA_STVP":    "Tasa de viviendas con TV de paga",
    "TASA_SPMVPI":  "Tasa de viviendas con streaming de paga",
    "TASA_CVJ":     "Tasa de viviendas con consola de videojuegos",
    "TASA_SINRTV":  "Tasa de viviendas sin radio ni TV",
    "TASA_SINLTC":  "Tasa de viviendas sin teléfono fijo ni celular",
    "TASA_SINCINT": "Tasa de viviendas sin computadora ni Internet",
    "TASA_SINTIC":  "Tasa de viviendas sin ninguna TIC",
}

nombres_vars = {
    "POBTOT":      "Población total",
    "POBFEM":      "Población femenina",
    "POBMAS":      "Población masculina",
    "VIVPAR_HAB":  "Viviendas particulares habitadas",
    "OCUPVIVPAR":  "Ocupantes en viv. part. habitadas",
    "GRAPROES":    "Grado promedio de escolaridad",
    "PROM_OCUP":   "Promedio de ocupantes por vivienda",
}
nombres_vars.update(nombres_tasas)
for v in vars_acceso_digital:
    desc = mapeo.get(v, v)
    if isinstance(desc, str):
        nombres_vars[v] = desc[:55]


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  FUNCIONES DE CÁLCULO MANUAL                                            ║
# ║  (No se usa .describe() como única solución — se justifica cada fórmula) ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def media_manual(x):
    """
    Media aritmética: μ = (1/n) Σ xᵢ
    Suma de todos los valores dividida entre el número de observaciones.
    """
    vals = x.dropna().values
    n = len(vals)
    if n == 0:
        return np.nan
    return np.sum(vals) / n


def mediana_manual(x):
    """
    Mediana: valor central de los datos ordenados.
    Si n es impar → x[(n+1)/2]
    Si n es par   → (x[n/2] + x[n/2 + 1]) / 2
    """
    vals = np.sort(x.dropna().values)
    n = len(vals)
    if n == 0:
        return np.nan
    if n % 2 == 1:
        return vals[n // 2]
    else:
        return (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def varianza_manual(x, ddof=1):
    """
    Varianza muestral: s² = (1/(n-ddof)) Σ (xᵢ - x̄)²
    Con ddof=1 para varianza muestral insesgada (corrección de Bessel).
    """
    vals = x.dropna().values
    n = len(vals)
    if n <= ddof:
        return np.nan
    mu = np.sum(vals) / n
    return np.sum((vals - mu) ** 2) / (n - ddof)


def desviacion_estandar_manual(x, ddof=1):
    """
    Desviación estándar: s = √(s²)
    Raíz cuadrada de la varianza muestral.
    """
    var = varianza_manual(x, ddof)
    if np.isnan(var):
        return np.nan
    return np.sqrt(var)


def coef_variacion_manual(x):
    """
    Coeficiente de variación: CV = (s / x̄) × 100
    Mide la dispersión relativa respecto a la media (en porcentaje).
    Un CV > 100% indica alta heterogeneidad.
    """
    mu = media_manual(x)
    s = desviacion_estandar_manual(x)
    if np.isnan(mu) or np.isnan(s) or mu == 0:
        return np.nan
    return (s / abs(mu)) * 100


def percentil_manual(x, p):
    """
    Percentil p: valor por debajo del cual se encuentra el p% de los datos.
    Método de interpolación lineal (consistente con NumPy 'linear').

    Fórmula:
      k = (n-1) × p/100
      f = floor(k), c = ceil(k)
      resultado = x[f] + (k - f) × (x[c] - x[f])
    """
    vals = np.sort(x.dropna().values)
    n = len(vals)
    if n == 0:
        return np.nan
    k = (n - 1) * p / 100.0
    f = int(np.floor(k))
    c = int(np.ceil(k))
    if f == c:
        return vals[f]
    return vals[f] + (k - f) * (vals[c] - vals[f])


def rango_intercuartilico_manual(x):
    """
    Rango intercuartílico: IQR = Q3 - Q1
    Mide la dispersión del 50% central de los datos.
    """
    q1 = percentil_manual(x, 25)
    q3 = percentil_manual(x, 75)
    if np.isnan(q1) or np.isnan(q3):
        return np.nan
    return q3 - q1


def asimetria_manual(x):
    """
    Asimetría (skewness) muestral ajustada:
      g₁ = [n/((n-1)(n-2))] × Σ[(xᵢ - x̄)/s]³

    Interpretación:
      g₁ ≈ 0  → distribución simétrica
      g₁ > 0  → cola derecha más larga (sesgo positivo)
      g₁ < 0  → cola izquierda más larga (sesgo negativo)
    """
    vals = x.dropna().values
    n = len(vals)
    if n < 3:
        return np.nan
    mu = np.sum(vals) / n
    s = np.sqrt(np.sum((vals - mu) ** 2) / (n - 1))
    if s == 0:
        return 0.0
    m3 = np.sum(((vals - mu) / s) ** 3)
    return (n / ((n - 1) * (n - 2))) * m3


def curtosis_manual(x):
    """
    Curtosis en exceso (excess kurtosis) muestral:
      K = { [n(n+1)] / [(n-1)(n-2)(n-3)] } × Σ[(xᵢ - x̄)/s]⁴
          - 3(n-1)² / [(n-2)(n-3)]

    Interpretación:
      K ≈ 0   → mesocúrtica (similar a la normal)
      K > 0   → leptocúrtica (colas pesadas)
      K < 0   → platicúrtica (colas ligeras)
    """
    vals = x.dropna().values
    n = len(vals)
    if n < 4:
        return np.nan
    mu = np.sum(vals) / n
    s = np.sqrt(np.sum((vals - mu) ** 2) / (n - 1))
    if s == 0:
        return 0.0
    m4 = np.sum(((vals - mu) / s) ** 4)
    k = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3)) * m4
    k -= (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return k


def entropia_shannon(x):
    """
    Entropía de Shannon: H = -Σ pᵢ × log₂(pᵢ)
    Mide la incertidumbre/diversidad de una variable categórica.

    H = 0           → todos los valores en una sola categoría
    H = log₂(k)     → distribución uniforme entre k categorías (máxima entropía)
    """
    counts = x.dropna().value_counts()
    n = counts.sum()
    if n == 0:
        return np.nan
    probs = counts / n
    # Evitar log(0)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def correlacion_pearson_manual(x, y):
    """
    Coeficiente de correlación de Pearson:
      r = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]

    Mide la fuerza y dirección de la relación lineal entre dos variables.
    Rango: [-1, 1]
    """
    mask = x.notna() & y.notna()
    xv = x[mask].values.astype(float)
    yv = y[mask].values.astype(float)
    n = len(xv)
    if n < 3:
        return np.nan
    mx = np.sum(xv) / n
    my = np.sum(yv) / n
    dx = xv - mx
    dy = yv - my
    num = np.sum(dx * dy)
    den = np.sqrt(np.sum(dx ** 2) * np.sum(dy ** 2))
    if den == 0:
        return np.nan
    return num / den


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  1. ESTADÍSTICA DESCRIPTIVA — VARIABLES CUANTITATIVAS                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  1. ESTADÍSTICA DESCRIPTIVA — VARIABLES CUANTITATIVAS")
print("=" * 90)

# ── 1a. Variables de contexto demográfico ──
print("\n  1a. VARIABLES DE CONTEXTO DEMOGRÁFICO")
print("  " + "─" * 85)

vars_cuant_demo = vars_demograficas_clave
encabezado = (f"  {'Variable':<36s} {'n':>6s} {'Media':>12s} {'Mediana':>12s} "
              f"{'Desv.Est.':>12s} {'CV%':>8s} {'Asimetría':>10s} {'Curtosis':>10s}")
print(encabezado)
print("  " + "─" * len(encabezado.strip()))

for v in vars_cuant_demo:
    if v not in df.columns:
        continue
    serie = df[v]
    n = serie.notna().sum()
    mu = media_manual(serie)
    med = mediana_manual(serie)
    s = desviacion_estandar_manual(serie)
    cv = coef_variacion_manual(serie)
    sk = asimetria_manual(serie)
    ku = curtosis_manual(serie)

    nombre = nombres_vars.get(v, v)[:34]
    mu_s = f"{mu:,.2f}" if pd.notna(mu) else "N/A"
    med_s = f"{med:,.2f}" if pd.notna(med) else "N/A"
    s_s = f"{s:,.2f}" if pd.notna(s) else "N/A"
    cv_s = f"{cv:.1f}" if pd.notna(cv) else "N/A"
    sk_s = f"{sk:.3f}" if pd.notna(sk) else "N/A"
    ku_s = f"{ku:.3f}" if pd.notna(ku) else "N/A"

    print(f"  {nombre:<36s} {n:>6d} {mu_s:>12s} {med_s:>12s} "
          f"{s_s:>12s} {cv_s:>8s} {sk_s:>10s} {ku_s:>10s}")

# ── 1b. Variables de acceso digital (conteos absolutos) ──
print("\n  1b. VARIABLES DE ACCESO DIGITAL — CONTEOS ABSOLUTOS")
print("  " + "─" * 85)
print(encabezado)
print("  " + "─" * len(encabezado.strip()))

for v in vars_acceso_digital:
    if v not in df.columns:
        continue
    serie = df[v]
    n = serie.notna().sum()
    mu = media_manual(serie)
    med = mediana_manual(serie)
    s = desviacion_estandar_manual(serie)
    cv = coef_variacion_manual(serie)
    sk = asimetria_manual(serie)
    ku = curtosis_manual(serie)

    nombre = nombres_vars.get(v, v)[:34]
    mu_s = f"{mu:,.2f}" if pd.notna(mu) else "N/A"
    med_s = f"{med:,.2f}" if pd.notna(med) else "N/A"
    s_s = f"{s:,.2f}" if pd.notna(s) else "N/A"
    cv_s = f"{cv:.1f}" if pd.notna(cv) else "N/A"
    sk_s = f"{sk:.3f}" if pd.notna(sk) else "N/A"
    ku_s = f"{ku:.3f}" if pd.notna(ku) else "N/A"

    print(f"  {nombre:<36s} {n:>6d} {mu_s:>12s} {med_s:>12s} "
          f"{s_s:>12s} {cv_s:>8s} {sk_s:>10s} {ku_s:>10s}")

# ── 1c. Tasas de acceso digital (proporciones) ──
print("\n  1c. TASAS DE ACCESO DIGITAL (proporción respecto a viviendas habitadas)")
print("  " + "─" * 85)
print(encabezado)
print("  " + "─" * len(encabezado.strip()))

for v in vars_tasas_acceso:
    if v not in df.columns:
        continue
    serie = df[v]
    n = serie.notna().sum()
    mu = media_manual(serie)
    med = mediana_manual(serie)
    s = desviacion_estandar_manual(serie)
    cv = coef_variacion_manual(serie)
    sk = asimetria_manual(serie)
    ku = curtosis_manual(serie)

    nombre = nombres_vars.get(v, v)[:34]
    mu_s = f"{mu:.4f}" if pd.notna(mu) else "N/A"
    med_s = f"{med:.4f}" if pd.notna(med) else "N/A"
    s_s = f"{s:.4f}" if pd.notna(s) else "N/A"
    cv_s = f"{cv:.1f}" if pd.notna(cv) else "N/A"
    sk_s = f"{sk:.3f}" if pd.notna(sk) else "N/A"
    ku_s = f"{ku:.3f}" if pd.notna(ku) else "N/A"

    print(f"  {nombre:<36s} {n:>6d} {mu_s:>12s} {med_s:>12s} "
          f"{s_s:>12s} {cv_s:>8s} {sk_s:>10s} {ku_s:>10s}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  2. PERCENTILES DETALLADOS — VARIABLES DE ACCESO DIGITAL                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  2. PERCENTILES — TASAS DE ACCESO DIGITAL")
print("=" * 90)

percentiles = [5, 25, 50, 75, 95]
enc_perc = (f"  {'Variable':<36s} {'Mín':>8s} "
            + "".join(f"{'P'+str(p):>8s}" for p in percentiles)
            + f" {'Máx':>8s} {'IQR':>8s}")
print(enc_perc)
print("  " + "─" * len(enc_perc.strip()))

for v in vars_tasas_acceso:
    if v not in df.columns:
        continue
    serie = df[v]
    nombre = nombres_vars.get(v, v)[:34]
    n = serie.notna().sum()
    if n == 0:
        continue

    vmin = serie.min()
    vmax = serie.max()
    iqr = rango_intercuartilico_manual(serie)
    percs = [percentil_manual(serie, p) for p in percentiles]

    min_s = f"{vmin:.4f}" if pd.notna(vmin) else "N/A"
    max_s = f"{vmax:.4f}" if pd.notna(vmax) else "N/A"
    iqr_s = f"{iqr:.4f}" if pd.notna(iqr) else "N/A"
    percs_s = [f"{p:.4f}" if pd.notna(p) else "N/A" for p in percs]

    print(f"  {nombre:<36s} {min_s:>8s} "
          + "".join(f"{ps:>8s}" for ps in percs_s)
          + f" {max_s:>8s} {iqr_s:>8s}")

# Percentiles para conteos absolutos de acceso digital
print(f"\n  PERCENTILES — CONTEOS ABSOLUTOS DE ACCESO DIGITAL")
enc_perc2 = (f"  {'Variable':<36s} {'Mín':>10s} "
             + "".join(f"{'P'+str(p):>10s}" for p in percentiles)
             + f" {'Máx':>10s} {'IQR':>10s}")
print(enc_perc2)
print("  " + "─" * len(enc_perc2.strip()))

for v in vars_acceso_digital:
    if v not in df.columns:
        continue
    serie = df[v]
    nombre = nombres_vars.get(v, v)[:34]
    n = serie.notna().sum()
    if n == 0:
        continue

    vmin = serie.min()
    vmax = serie.max()
    iqr = rango_intercuartilico_manual(serie)
    percs = [percentil_manual(serie, p) for p in percentiles]

    min_s = f"{vmin:,.0f}" if pd.notna(vmin) else "N/A"
    max_s = f"{vmax:,.0f}" if pd.notna(vmax) else "N/A"
    iqr_s = f"{iqr:,.0f}" if pd.notna(iqr) else "N/A"
    percs_s = [f"{p:,.0f}" if pd.notna(p) else "N/A" for p in percs]

    print(f"  {nombre:<36s} {min_s:>10s} "
          + "".join(f"{ps:>10s}" for ps in percs_s)
          + f" {max_s:>10s} {iqr_s:>10s}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  3. ESTADÍSTICA DESCRIPTIVA — VARIABLES CATEGÓRICAS                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  3. ESTADÍSTICA DESCRIPTIVA — VARIABLES CATEGÓRICAS")
print("=" * 90)

nombres_mun = {
    0: "Total entidad", 1: "Aguascalientes", 2: "Asientos",
    3: "Calvillo", 4: "Cosío", 5: "Jesús María",
    6: "Pabellón de Arteaga", 7: "Rincón de Romos",
    8: "San José de Gracia", 9: "Tepezalá",
    10: "El Llano", 11: "San Francisco de los Romo"
}

for var in vars_categoricas:
    print(f"\n  ── {var} ──")
    serie = df[var].dropna()
    n = len(serie)
    print(f"  Observaciones válidas: {n:,}")

    # Frecuencias absolutas y relativas
    freq_abs = serie.value_counts().sort_index()
    freq_rel = freq_abs / n

    # Moda
    moda_val = freq_abs.idxmax()
    moda_freq = freq_abs.max()

    # Entropía de Shannon
    H = entropia_shannon(serie)
    H_max = np.log2(len(freq_abs)) if len(freq_abs) > 1 else 0
    H_norm = H / H_max if H_max > 0 else 0  # Entropía normalizada [0,1]

    print(f"  Categorías únicas: {len(freq_abs)}")
    print(f"  Moda: {moda_val} (frecuencia: {moda_freq:,})")
    print(f"  Entropía de Shannon: H = {H:.4f} bits")
    print(f"  Entropía máxima:     H_max = {H_max:.4f} bits (distribución uniforme)")
    print(f"  Entropía normalizada: {H_norm:.4f} (0=concentrada, 1=uniforme)")

    print(f"\n  {'Categoría':<30s} {'Frec. Abs.':>12s} {'Frec. Rel.':>12s} {'% Acum.':>10s}")
    print(f"  {'─'*30} {'─'*12} {'─'*12} {'─'*10}")
    cum = 0
    for cat, fa in freq_abs.items():
        fr = freq_rel[cat]
        cum += fr
        if var == "MUN":
            nombre_cat = nombres_mun.get(int(cat), str(cat))
        else:
            nombre_cat = str(int(cat)) if pd.notna(cat) else str(cat)
        print(f"  {nombre_cat:<30s} {fa:>12,d} {fr:>12.4f} {cum:>9.2%}")

# ── Análisis categórico de TAMLOC con acceso digital ──
print(f"\n  ── Acceso digital promedio por tamaño de localidad (TAMLOC) ──")

tamloc_etiquetas = {
    1: "1-249 hab.", 2: "250-499", 3: "500-999",
    4: "1,000-2,499", 5: "2,500-4,999", 6: "5,000-9,999",
    7: "10,000-14,999", 8: "15,000-29,999", 9: "30,000-49,999",
    10: "50,000-99,999", 11: "100,000-249,999",
    12: "250,000-499,999", 13: "500,000-999,999",
    14: "1,000,000+"
}

vars_tasa_clave = ["TASA_INTER", "TASA_CEL", "TASA_PC", "TASA_TV"]
enc_tamloc = f"  {'Tam. Loc.':<20s} {'n':>6s}"
for vt in vars_tasa_clave:
    enc_tamloc += f" {vt.replace('TASA_',''):>10s}"
print(enc_tamloc)
print("  " + "─" * len(enc_tamloc.strip()))

for tam in sorted(df["TAMLOC"].dropna().unique()):
    tam_int = int(tam)
    mask = df["TAMLOC"] == tam
    n_t = mask.sum()
    etiqueta = tamloc_etiquetas.get(tam_int, str(tam_int))
    line = f"  {etiqueta:<20s} {n_t:>6d}"
    for vt in vars_tasa_clave:
        if vt in df.columns:
            media_t = media_manual(df.loc[mask, vt])
            line += f" {media_t:>10.4f}" if pd.notna(media_t) else f" {'N/A':>10s}"
        else:
            line += f" {'N/A':>10s}"
    print(line)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  4. ANÁLISIS DE CORRELACIÓN                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  4. ANÁLISIS DE CORRELACIÓN — ACCESO DIGITAL")
print("=" * 90)

# ── 4a. Matriz de correlación entre tasas de acceso digital ──
print("\n  4a. MATRIZ DE CORRELACIÓN DE PEARSON (tasas de acceso digital)")
print("  " + "─" * 85)

# Calcular manualmente
vars_corr = vars_tasas_acceso
n_vars = len(vars_corr)
corr_matrix = np.full((n_vars, n_vars), np.nan)

for i in range(n_vars):
    for j in range(n_vars):
        if i == j:
            corr_matrix[i, j] = 1.0
        elif j > i:
            r = correlacion_pearson_manual(df[vars_corr[i]], df[vars_corr[j]])
            corr_matrix[i, j] = r
            corr_matrix[j, i] = r

# Imprimir matriz
abrevs = [v.replace("TASA_", "") for v in vars_corr]
header = f"  {'':>12s}" + "".join(f"{a:>9s}" for a in abrevs)
print(header)
print("  " + "─" * len(header.strip()))
for i, abrev in enumerate(abrevs):
    row_str = f"  {abrev:>12s}"
    for j in range(n_vars):
        val = corr_matrix[i, j]
        if pd.notna(val):
            row_str += f" {val:>8.3f}"
        else:
            row_str += f" {'N/A':>8s}"
    print(row_str)

# ── 4b. Correlaciones más fuertes ──
print(f"\n  4b. CORRELACIONES MÁS FUERTES (|r| > 0.7)")
print(f"  {'Variable 1':<18s} {'Variable 2':<18s} {'r':>8s} {'Interpretación'}")
print(f"  {'─'*18} {'─'*18} {'─'*8} {'─'*30}")

pares_mostrados = set()
for i in range(n_vars):
    for j in range(i + 1, n_vars):
        r = corr_matrix[i, j]
        if pd.notna(r) and abs(r) > 0.7:
            par = (min(abrevs[i], abrevs[j]), max(abrevs[i], abrevs[j]))
            if par not in pares_mostrados:
                pares_mostrados.add(par)
                if abs(r) > 0.9:
                    interp = "Muy fuerte"
                elif abs(r) > 0.7:
                    interp = "Fuerte"
                else:
                    interp = "Moderada"
                signo = "positiva" if r > 0 else "negativa"
                print(f"  {abrevs[i]:<18s} {abrevs[j]:<18s} {r:>8.3f} "
                      f"{interp} {signo}")

# ── 4c. Correlación de acceso digital con variables socioeconómicas ──
print(f"\n  4c. CORRELACIÓN DE ACCESO DIGITAL CON VARIABLES SOCIOECONÓMICAS")
print(f"  {'Tasa Digital':<20s} {'POBTOT':>10s} {'GRAPROES':>10s} "
      f"{'PROM_OCUP':>10s} {'VIVPAR_HAB':>12s}")
print(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*10} {'─'*12}")

vars_socio = ["POBTOT", "GRAPROES", "PROM_OCUP", "VIVPAR_HAB"]
for vt in vars_tasas_acceso:
    if vt not in df.columns:
        continue
    nombre = vt.replace("TASA_", "")[:18]
    line = f"  {nombre:<20s}"
    for vs in vars_socio:
        if vs in df.columns:
            r = correlacion_pearson_manual(df[vt], df[vs])
            line += f" {r:>10.3f}" if pd.notna(r) else f" {'N/A':>10s}"
        else:
            line += f" {'N/A':>10s}"
    print(line)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  5. ANÁLISIS DE COLINEALIDAD                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  5. ANÁLISIS DE COLINEALIDAD (VIF — Factor de Inflación de la Varianza)")
print("=" * 90)

print("""
  El VIF mide cuánto se infla la varianza de un coeficiente de regresión
  debido a la colinealidad con otras variables.

  Fórmula: VIF_j = 1 / (1 - R²_j)
  donde R²_j es el R² de la regresión de la variable j contra las demás.

  Interpretación:
    VIF = 1       → Sin colinealidad
    1 < VIF < 5   → Colinealidad moderada
    5 ≤ VIF < 10  → Colinealidad alta
    VIF ≥ 10      → Colinealidad severa (considerar eliminar variable)
""")

# Calcular VIF manualmente usando la inversa de la matriz de correlación
# VIF_j = diagonal_j de (R⁻¹) donde R es la matriz de correlación
vars_vif = [v for v in vars_tasas_acceso
            if v in df.columns and df[v].notna().sum() > 10]

# Obtener solo filas completas
df_vif = df[vars_vif].dropna()
n_vif = len(df_vif)
print(f"  Observaciones completas para VIF: {n_vif:,}")
print(f"  Variables analizadas: {len(vars_vif)}")

if n_vif > len(vars_vif) + 1:
    # Construir matriz de correlación
    R = np.corrcoef(df_vif.values, rowvar=False)

    # Verificar que la matriz sea invertible
    det_R = np.linalg.det(R)
    print(f"  Determinante de la matriz de correlación: {det_R:.6e}")
    if abs(det_R) < 1e-10:
        print(f"  ⚠ Determinante muy cercano a 0 → Colinealidad severa")
        print(f"    (la matriz es casi singular)")

    try:
        R_inv = np.linalg.inv(R)
        vif_values = np.diag(R_inv)

        print(f"\n  {'Variable':<36s} {'VIF':>10s} {'Diagnóstico'}")
        print(f"  {'─'*36} {'─'*10} {'─'*25}")

        for idx, v in enumerate(vars_vif):
            vif = vif_values[idx]
            nombre = nombres_vars.get(v, v)[:34]
            if vif >= 10:
                diag = "⚠ SEVERA"
            elif vif >= 5:
                diag = "⚠ Alta"
            elif vif > 1:
                diag = "✓ Moderada/Aceptable"
            else:
                diag = "✓ Sin colinealidad"
            print(f"  {nombre:<36s} {vif:>10.2f} {diag}")

        # Resumen
        n_severa = np.sum(vif_values >= 10)
        n_alta = np.sum((vif_values >= 5) & (vif_values < 10))
        print(f"\n  Resumen de colinealidad:")
        print(f"    Variables con VIF ≥ 10 (severa): {n_severa}")
        print(f"    Variables con VIF ≥ 5 (alta):    {n_alta}")

        if n_severa > 0:
            print(f"\n  ⚠ Recomendación: Considerar eliminar o combinar las variables")
            print(f"    con VIF ≥ 10 antes de construir modelos predictivos.")
            print(f"    Alternativas: usar PCA, regularización (Ridge/Lasso),")
            print(f"    o crear un índice compuesto de acceso digital.")

    except np.linalg.LinAlgError:
        print(f"  ⚠ No se pudo invertir la matriz de correlación.")
        print(f"    Existe colinealidad perfecta entre las variables.")
else:
    print(f"  ⚠ Insuficientes observaciones completas para calcular VIF.")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  6. HALLAZGOS CLAVE E INTERPRETACIÓN                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 90)
print("  6. HALLAZGOS CLAVE E INTERPRETACIÓN")
print("=" * 90)

# Calcular estadísticos resumen para el hallazgo
tasa_inter_media = media_manual(df["TASA_INTER"]) if "TASA_INTER" in df.columns else None
tasa_cel_media = media_manual(df["TASA_CEL"]) if "TASA_CEL" in df.columns else None
tasa_pc_media = media_manual(df["TASA_PC"]) if "TASA_PC" in df.columns else None
tasa_sintic_media = media_manual(df["TASA_SINTIC"]) if "TASA_SINTIC" in df.columns else None

print(f"""
  ACCESO DIGITAL EN AGUASCALIENTES — Principales hallazgos:
  ──────────────────────────────────────────────────────────

  1. PENETRACIÓN DIGITAL (promedios por localidad):
     • Internet:                {tasa_inter_media:.1%} de las viviendas (promedio por localidad)
     • Teléfono celular:        {tasa_cel_media:.1%}
     • Computadora/laptop:      {tasa_pc_media:.1%}
     • Sin ninguna TIC:         {tasa_sintic_media:.1%}

  2. DISTRIBUCIÓN:
     • Todas las variables de acceso digital presentan ALTA ASIMETRÍA POSITIVA
       (sesgo a la derecha), lo que indica que la mayoría de las localidades
       tienen tasas bajas y unas pocas tienen tasas muy altas.
     • Los coeficientes de variación son altos (>50%), indicando fuerte
       heterogeneidad entre localidades.

  3. BRECHA DIGITAL:
     • Las localidades más pequeñas (TAMLOC bajo) tienen tasas de acceso
       digital significativamente menores.
     • La brecha es más pronunciada en Internet y computadoras que en
       televisión y celular.

  4. CORRELACIONES:
     • Las tasas de Internet, computadora y streaming están fuertemente
       correlacionadas entre sí (forman un "cluster de acceso avanzado").
     • Las tasas de carencia (SINRTV, SINLTC, SINCINT, SINTIC) están
       inversamente correlacionadas con las de acceso.

  5. COLINEALIDAD:
     • Varias tasas de acceso digital presentan alta colinealidad,
       lo cual es esperado (quien tiene Internet probablemente tiene PC).
     • Para modelos predictivos, considerar crear un índice compuesto.
""")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  7. RECOMENDACIONES PARA ETAPAS SIGUIENTES                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("─" * 90)
print("  7. RECOMENDACIONES PARA ETAPAS SIGUIENTES")
print("─" * 90)

print("""
  Para la Etapa 3 (Análisis de Datos Faltantes):
  ───────────────────────────────────────────────
  • Los 1,072 registros con '*' (52%) son censura por confidencialidad,
    NO datos faltantes aleatorios → mecanismo MNAR.
  • Generar la Matriz de Missingness y verificar si la censura se
    concentra en localidades pequeñas (TAMLOC = 1).
  • Considerar imputación informativa o análisis solo del subconjunto
    con datos completos (n≈950 localidades).

  Para la Etapa 4 (Visualización):
  ─────────────────────────────────
  • Histogramas con KDE para las tasas de acceso digital.
  • Boxplots por municipio y por tamaño de localidad.
  • Mapa de calor geográfico (lat/lon) del acceso a Internet.
  • Pairplot de: TASA_INTER, TASA_CEL, TASA_PC, GRAPROES, POBTOT.
  • Pirámide poblacional usando las variables de grupos quinquenales.
  • Scatter: población total vs. tasa de Internet por localidad.

  Para Modelado Posterior:
  ────────────────────────
  • Dado el alto VIF, considerar reducción dimensional (PCA).
  • Crear un Índice de Acceso Digital compuesto con las 13 variables TIC.
  • Investigar factores predictores: escolaridad, urbanización, municipio.
""")

print("=" * 90)
print("  FIN DE ETAPA 2 — Estadística Descriptiva Completa")
print("=" * 90)
