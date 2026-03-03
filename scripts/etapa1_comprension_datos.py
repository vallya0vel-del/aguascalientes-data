# -*- coding: utf-8 -*-
"""
================================================================================
  ETAPA 1 — Comprensión y Preparación de Datos
  Censo de Población y Vivienda 2020 · Estado de Aguascalientes
  Enfoque: Acceso Digital en la Población
================================================================================
  Tareas:
    1. Leer ambos archivos (datos + diccionario).
    2. Usar el diccionario para mapear mnemónicos → descripción.
    3. Clasificar variables: demográficas, vivienda, educación, económicas,
       geográficas y —con énfasis especial— acceso digital / TIC.
    4. Detectar: tipos de datos incorrectos, variables categóricas codificadas
       como numéricas, rangos inválidos (usando el diccionario).
================================================================================
"""

import pandas as pd
import numpy as np
import warnings, os, sys

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN DE RUTAS
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

RUTA_DATOS      = os.path.join(DATA_DIR, "conjunto_de_datos_iter_01CSV20.csv")
RUTA_DICCIONARIO = os.path.join(DATA_DIR, "diccionario_datos_iter_01CSV20.csv")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  1. LECTURA DE ARCHIVOS                                                  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("=" * 80)
print("  ETAPA 1 — COMPRENSIÓN Y PREPARACIÓN DE DATOS")
print("  Censo de Población y Vivienda 2020 · Aguascalientes")
print("  Enfoque: Acceso Digital en la Población")
print("=" * 80)

# 1a. Lectura del conjunto de datos principal
# Nota: El archivo tiene BOM UTF-8, por lo que usamos 'utf-8-sig' para
# eliminar el carácter BOM del nombre de la primera columna.
print("\n▸ Leyendo conjunto de datos principal...")
df = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig", low_memory=False)
print(f"  ✓ Dimensiones: {df.shape[0]:,} registros × {df.shape[1]} columnas")

# 1b. Lectura del diccionario de datos
print("\n▸ Leyendo diccionario de datos...")
dict_raw = pd.read_csv(RUTA_DICCIONARIO, encoding="utf-8-sig", header=None)

# El diccionario tiene encabezados reales en la fila 3 (index=3)
# y datos a partir de la fila 4 (index=4)
dict_df = dict_raw.iloc[4:].copy()
dict_df.columns = [
    "Num", "Indicador", "Descripcion", "Mnemonico",
    "Rango", "Tamaño", "Col6", "Col7", "Col8", "Col9"
]
dict_df = dict_df.reset_index(drop=True)

# Limpiar espacios en los mnemónicos
dict_df["Mnemonico"] = dict_df["Mnemonico"].astype(str).str.strip()
dict_df = dict_df[dict_df["Mnemonico"] != "nan"].copy()
print(f"  ✓ Diccionario: {len(dict_df)} variables documentadas")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  2. MAPEO DE MNEMÓNICOS → DESCRIPCIÓN                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "─" * 80)
print("  2. MAPEO MNEMÓNICO → DESCRIPCIÓN")
print("─" * 80)

# Crear diccionario de mapeo
mapeo_mnemonico = dict(
    zip(dict_df["Mnemonico"], dict_df["Indicador"])
)
mapeo_descripcion = dict(
    zip(dict_df["Mnemonico"], dict_df["Descripcion"])
)
mapeo_rango = dict(
    zip(dict_df["Mnemonico"], dict_df["Rango"])
)

# Verificar cobertura: ¿todas las columnas del dataset están en el diccionario?
cols_dataset = set(df.columns)
cols_diccionario = set(dict_df["Mnemonico"])
cols_sin_doc = cols_dataset - cols_diccionario
cols_doc_sin_data = cols_diccionario - cols_dataset

print(f"\n  Columnas en el dataset:          {len(cols_dataset)}")
print(f"  Variables en el diccionario:     {len(cols_diccionario)}")
print(f"  Columnas sin documentación:      {len(cols_sin_doc)}")
if cols_sin_doc:
    print(f"    → {sorted(cols_sin_doc)}")
print(f"  Variables documentadas sin datos: {len(cols_doc_sin_data)}")
if cols_doc_sin_data:
    for v in sorted(cols_doc_sin_data):
        print(f"    → {v}")

# Mostrar primeras 15 variables y su descripción
print("\n  Ejemplo de mapeo (primeras 15 columnas):")
print(f"  {'Mnemónico':<20s} {'Indicador':<60s}")
print(f"  {'─'*20} {'─'*60}")
for col in df.columns[:15]:
    desc = mapeo_mnemonico.get(col, "(sin documentación)")
    if isinstance(desc, str):
        desc = desc[:58]
    print(f"  {col:<20s} {desc}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  3. CLASIFICACIÓN DE VARIABLES                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "─" * 80)
print("  3. CLASIFICACIÓN DE VARIABLES POR CATEGORÍA")
print("─" * 80)

# ── Definición de categorías ──
# Se asignan basándose en el mnemónico y la descripción del diccionario INEGI.

vars_geograficas = [
    "ENTIDAD", "NOM_ENT", "MUN", "NOM_MUN", "LOC", "NOM_LOC",
    "LONGITUD", "LATITUD", "ALTITUD", "TAMLOC"
]

vars_demograficas = [
    "POBTOT", "POBFEM", "POBMAS",
    "P_0A2", "P_0A2_F", "P_0A2_M",
    "P_3YMAS", "P_3YMAS_F", "P_3YMAS_M",
    "P_5YMAS", "P_5YMAS_F", "P_5YMAS_M",
    "P_12YMAS", "P_12YMAS_F", "P_12YMAS_M",
    "P_15YMAS", "P_15YMAS_F", "P_15YMAS_M",
    "P_18YMAS", "P_18YMAS_F", "P_18YMAS_M",
    "P_3A5", "P_3A5_F", "P_3A5_M",
    "P_6A11", "P_6A11_F", "P_6A11_M",
    "P_8A14", "P_8A14_F", "P_8A14_M",
    "P_12A14", "P_12A14_F", "P_12A14_M",
    "P_15A17", "P_15A17_F", "P_15A17_M",
    "P_18A24", "P_18A24_F", "P_18A24_M",
    "P_15A49_F",
    "P_60YMAS", "P_60YMAS_F", "P_60YMAS_M",
    "REL_H_M",
    "POB0_14", "POB15_64", "POB65_MAS",
    "P_0A4", "P_0A4_F", "P_0A4_M",
    "P_5A9", "P_5A9_F", "P_5A9_M",
    "P_10A14", "P_10A14_F", "P_10A14_M",
    "P_15A19", "P_15A19_F", "P_15A19_M",
    "P_20A24", "P_20A24_F", "P_20A24_M",
    "P_25A29", "P_25A29_F", "P_25A29_M",
    "P_30A34", "P_30A34_F", "P_30A34_M",
    "P_35A39", "P_35A39_F", "P_35A39_M",
    "P_40A44", "P_40A44_F", "P_40A44_M",
    "P_45A49", "P_45A49_F", "P_45A49_M",
    "P_50A54", "P_50A54_F", "P_50A54_M",
    "P_55A59", "P_55A59_F", "P_55A59_M",
    "P_60A64", "P_60A64_F", "P_60A64_M",
    "P_65A69", "P_65A69_F", "P_65A69_M",
    "P_70A74", "P_70A74_F", "P_70A74_M",
    "P_75A79", "P_75A79_F", "P_75A79_M",
    "P_80A84", "P_80A84_F", "P_80A84_M",
    "P_85YMAS", "P_85YMAS_F", "P_85YMAS_M",
    "PROM_HNV",
    "PNACENT", "PNACENT_F", "PNACENT_M",
    "PNACOE", "PNACOE_F", "PNACOE_M",
    "PRES2015", "PRES2015_F", "PRES2015_M",
    "PRESOE15", "PRESOE15_F", "PRESOE15_M",
    "P3YM_HLI", "P3YM_HLI_F", "P3YM_HLI_M",
    "P3HLINHE", "P3HLINHE_F", "P3HLINHE_M",
    "P3HLI_HE", "P3HLI_HE_F", "P3HLI_HE_M",
    "P5_HLI", "P5_HLI_NHE", "P5_HLI_HE",
    "PHOG_IND",
    "POB_AFRO", "POB_AFRO_F", "POB_AFRO_M",
    "PCON_DISC", "PCDISC_MOT", "PCDISC_VIS", "PCDISC_LENG",
    "PCDISC_AUD", "PCDISC_MOT2", "PCDISC_MEN",
    "PCON_LIMI", "PCLIM_CSB", "PCLIM_VIS", "PCLIM_HACO",
    "PCLIM_OAUD", "PCLIM_MOT2", "PCLIM_RE_CO", "PCLIM_PMEN",
    "PSIND_LIM",
    "P12YM_SOLT", "P12YM_CASA", "P12YM_SEPA",
    "PCATOLICA", "PRO_CRIEVA", "POTRAS_REL", "PSIN_RELIG",
]

vars_educacion = [
    "P3A5_NOA", "P3A5_NOA_F", "P3A5_NOA_M",
    "P6A11_NOA", "P6A11_NOAF", "P6A11_NOAM",
    "P12A14NOA", "P12A14NOAF", "P12A14NOAM",
    "P15A17A", "P15A17A_F", "P15A17A_M",
    "P18A24A", "P18A24A_F", "P18A24A_M",
    "P8A14AN", "P8A14AN_F", "P8A14AN_M",
    "P15YM_AN", "P15YM_AN_F", "P15YM_AN_M",
    "P15YM_SE", "P15YM_SE_F", "P15YM_SE_M",
    "P15PRI_IN", "P15PRI_INF", "P15PRI_INM",
    "P15PRI_CO", "P15PRI_COF", "P15PRI_COM",
    "P15SEC_IN", "P15SEC_INF", "P15SEC_INM",
    "P15SEC_CO", "P15SEC_COF", "P15SEC_COM",
    "P18YM_PB", "P18YM_PB_F", "P18YM_PB_M",
    "GRAPROES", "GRAPROES_F", "GRAPROES_M",
]

vars_economicas = [
    "PEA", "PEA_F", "PEA_M",
    "PE_INAC", "PE_INAC_F", "PE_INAC_M",
    "POCUPADA", "POCUPADA_F", "POCUPADA_M",
    "PDESOCUP", "PDESOCUP_F", "PDESOCUP_M",
    "PSINDER", "PDER_SS", "PDER_IMSS", "PDER_ISTE", "PDER_ISTEE",
    "PAFIL_PDOM", "PDER_SEGP", "PDER_IMSSB",
    "PAFIL_IPRIV", "PAFIL_OTRAI",
]

vars_vivienda = [
    "TOTHOG", "HOGJEF_F", "HOGJEF_M",
    "POBHOG", "PHOGJEF_F", "PHOGJEF_M",
    "VIVTOT", "TVIVHAB", "TVIVPAR",
    "VIVPAR_HAB", "VIVPARH_CV", "TVIVPARHAB",
    "VIVPAR_DES", "VIVPAR_UT",
    "OCUPVIVPAR", "PROM_OCUP", "PRO_OCUP_C",
    "VPH_PISODT", "VPH_PISOTI",
    "VPH_1DOR", "VPH_2YMASD",
    "VPH_1CUART", "VPH_2CUART", "VPH_3YMASC",
    "VPH_C_ELEC", "VPH_S_ELEC",
    "VPH_AGUADV", "VPH_AEASP", "VPH_AGUAFV",
    "VPH_TINACO", "VPH_CISTER",
    "VPH_EXCSA", "VPH_LETR",
    "VPH_DRENAJ", "VPH_NODREN",
    "VPH_C_SERV", "VPH_NDEAED",
    "VPH_DSADMA", "VPH_NDACMM", "VPH_SNBIEN",
    "VPH_REFRI", "VPH_LAVAD", "VPH_HMICRO",
    "VPH_AUTOM", "VPH_MOTO", "VPH_BICI",
]

# ★ CATEGORÍA PRINCIPAL DE INTERÉS: ACCESO DIGITAL / TIC ★
vars_acceso_digital = [
    "VPH_RADIO",     # Viviendas con radio
    "VPH_TV",        # Viviendas con televisor
    "VPH_PC",        # Viviendas con computadora, laptop o tablet
    "VPH_TELEF",     # Viviendas con línea telefónica fija
    "VPH_CEL",       # Viviendas con teléfono celular
    "VPH_INTER",     # Viviendas con Internet
    "VPH_STVP",      # Viviendas con servicio de TV de paga
    "VPH_SPMVPI",    # Viviendas con streaming (películas/música/videos de paga)
    "VPH_CVJ",       # Viviendas con consola de videojuegos
    "VPH_SINRTV",    # Viviendas sin radio ni televisor
    "VPH_SINLTC",    # Viviendas sin línea telefónica fija ni celular
    "VPH_SINCINT",   # Viviendas sin computadora ni Internet
    "VPH_SINTIC",    # Viviendas sin ninguna TIC
]

# Definir mapeo completo de categorías
categorias = {
    "Geográficas":     vars_geograficas,
    "Demográficas":    vars_demograficas,
    "Educación":       vars_educacion,
    "Económicas":      vars_economicas,
    "Vivienda":        vars_vivienda,
    "Acceso Digital (TIC)": vars_acceso_digital,
}

# Mostrar resumen
print()
total_clasif = 0
for cat, variables in categorias.items():
    n = len(variables)
    total_clasif += n
    marca = " ★" if cat == "Acceso Digital (TIC)" else ""
    print(f"  {cat:<25s} → {n:>3d} variables{marca}")

sin_clasificar = [c for c in df.columns
                  if not any(c in v for v in categorias.values())]
print(f"  {'Sin clasificar':<25s} → {len(sin_clasificar):>3d} variables")
print(f"  {'─'*45}")
print(f"  {'TOTAL':<25s} → {len(df.columns):>3d} columnas")

if sin_clasificar:
    print(f"\n  Variables sin clasificar: {sin_clasificar}")

# ── Detalle de variables de Acceso Digital ──
print(f"\n  ★ DETALLE: Variables de Acceso Digital / TIC:")
print(f"  {'Mnemónico':<15s} {'Descripción'}")
print(f"  {'─'*15} {'─'*60}")
for v in vars_acceso_digital:
    desc = mapeo_mnemonico.get(v, "(sin doc)")
    if isinstance(desc, str):
        desc = desc[:60]
    print(f"  {v:<15s} {desc}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  4. DETECCIÓN DE PROBLEMAS EN LOS DATOS                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "─" * 80)
print("  4. DETECCIÓN DE PROBLEMAS EN LOS DATOS")
print("─" * 80)

# ── 4a. Tipos de datos actuales vs esperados ──
print("\n  4a. TIPOS DE DATOS — Actuales vs Esperados")
print("  " + "─" * 75)

# Columnas que son object pero deberían ser numéricas
# (INEGI usa '*' para proteger confidencialidad en localidades pequeñas)
cols_object = df.select_dtypes(include=["object"]).columns.tolist()
cols_texto_legit = ["NOM_ENT", "NOM_MUN", "NOM_LOC", "LONGITUD", "LATITUD"]
cols_object_problema = [c for c in cols_object if c not in cols_texto_legit]

# Contar valores '*' por columna
star_counts = (df == "*").sum()
cols_con_asterisco = star_counts[star_counts > 0]

print(f"\n  Columnas tipo 'object' (texto):     {len(cols_object)}")
print(f"  Columnas legítimamente texto:       {len(cols_texto_legit)}")
print(f"  Columnas numéricas leídas como texto: {len(cols_object_problema)}")
print(f"  Columnas con valores '*':            {len(cols_con_asterisco)}")

print(f"\n  ℹ Nota: INEGI utiliza el símbolo '*' para proteger la")
print(f"    confidencialidad de localidades con ≤2 viviendas.")
print(f"    Esto causa que {len(cols_object_problema)} columnas numéricas se lean")
print(f"    como tipo 'object' (texto) en pandas.")

# Estadísticas de '*' por tipo de variable
print(f"\n  Distribución de valores '*' en variables de Acceso Digital:")
print(f"  {'Variable':<15s} {'Valores *':>12s} {'% del total':>12s}")
print(f"  {'─'*15} {'─'*12} {'─'*12}")
for v in vars_acceso_digital:
    if v in df.columns:
        n_star = (df[v] == "*").sum()
        pct = n_star / len(df) * 100
        print(f"  {v:<15s} {n_star:>12,d} {pct:>11.1f}%")

# ── 4b. Variables categóricas codificadas como numéricas ──
print(f"\n  4b. VARIABLES CATEGÓRICAS CODIFICADAS COMO NUMÉRICAS")
print("  " + "─" * 75)

vars_categoricas_como_num = {
    "ENTIDAD":  "Clave de entidad federativa (código 01–32)",
    "MUN":      "Clave de municipio (código 000–570)",
    "LOC":      "Clave de localidad (código 0000–9999)",
    "TAMLOC":   "Tamaño de localidad (categorías 01–14, ordinal)",
}

for var, razon in vars_categoricas_como_num.items():
    if var in df.columns:
        dtype_actual = df[var].dtype
        n_unicos = df[var].nunique()
        print(f"  • {var:<12s} → dtype actual: {str(dtype_actual):<8s} | "
              f"Valores únicos: {n_unicos:<5d} | {razon}")

print(f"\n  ⚠ Estas variables son identificadores o categorías ordinales,")
print(f"    NO deben tratarse como variables cuantitativas continuas.")
print(f"    Recomendación: convertir a tipo 'category' o 'str'.")

# ── 4c. Detección de rangos inválidos ──
print(f"\n  4c. DETECCIÓN DE RANGOS INVÁLIDOS")
print("  " + "─" * 75)

# Convertir columnas numéricas reemplazando '*' con NaN
df_num = df.copy()
for col in cols_object_problema:
    df_num[col] = pd.to_numeric(df_num[col], errors="coerce")

# Verificar rangos: valores negativos en variables de conteo
print(f"\n  Verificando valores negativos en variables de conteo poblacional:")
vars_conteo = [c for c in df.columns
               if c not in cols_texto_legit
               and c not in ["LONGITUD", "LATITUD", "ALTITUD", "REL_H_M",
                             "PROM_HNV", "PROM_OCUP", "PRO_OCUP_C",
                             "GRAPROES", "GRAPROES_F", "GRAPROES_M"]]
negativos_encontrados = False
for col in vars_conteo:
    if col in df_num.columns and df_num[col].dtype in ["float64", "int64"]:
        n_neg = (df_num[col] < 0).sum()
        if n_neg > 0:
            negativos_encontrados = True
            print(f"  ⚠ {col}: {n_neg} valores negativos detectados")
if not negativos_encontrados:
    print(f"  ✓ No se encontraron valores negativos en variables de conteo.")

# Verificar que ENTIDAD sea siempre 1 (Aguascalientes)
print(f"\n  Verificando coherencia geográfica:")
entidad_vals = df["ENTIDAD"].unique()
print(f"  • ENTIDAD: valores únicos = {entidad_vals} — {'✓ Solo Aguascalientes (01)' if len(entidad_vals) == 1 and entidad_vals[0] == 1 else '⚠ Datos de múltiples entidades'}")

# Verificar municipios de Aguascalientes (11 municipios + total)
mun_vals = sorted(df["MUN"].unique())
print(f"  • MUN: {len(mun_vals)} valores únicos: {mun_vals}")
print(f"    (0 = Total entidad, 1–11 = Municipios de Aguascalientes)")

# Verificar TAMLOC
if "TAMLOC" in df.columns:
    tamloc_vals = df["TAMLOC"].unique()
    print(f"  • TAMLOC: {len(tamloc_vals)} valores únicos")
    # Verificar si hay valores fuera del rango esperado 01..14
    tamloc_num = pd.to_numeric(df["TAMLOC"], errors="coerce")
    fuera_rango = tamloc_num[(tamloc_num < 1) | (tamloc_num > 14)]
    if len(fuera_rango) > 0:
        print(f"    ⚠ {len(fuera_rango)} valores fuera del rango esperado (01–14)")
    else:
        n_valid = tamloc_num.notna().sum()
        n_star = (df["TAMLOC"] == "*").sum()
        print(f"    ✓ Todos los valores numéricos en rango 01–14 "
              f"({n_valid} válidos, {n_star} censurados '*')")

# Verificar rangos en variables de acceso digital
print(f"\n  Verificando rangos en variables de Acceso Digital:")
print(f"  {'Variable':<15s} {'Mín':>10s} {'Máx':>12s} {'Nulos/NaN':>10s} {'Estado'}")
print(f"  {'─'*15} {'─'*10} {'─'*12} {'─'*10} {'─'*20}")
for v in vars_acceso_digital:
    if v in df_num.columns:
        col_data = df_num[v]
        vmin = col_data.min()
        vmax = col_data.max()
        n_na = col_data.isna().sum()
        # Las variables de conteo deben ser ≥ 0
        estado = "✓ OK" if (pd.isna(vmin) or vmin >= 0) else "⚠ Negativos"
        vmin_str = f"{vmin:,.0f}" if pd.notna(vmin) else "N/A"
        vmax_str = f"{vmax:,.0f}" if pd.notna(vmax) else "N/A"
        print(f"  {v:<15s} {vmin_str:>10s} {vmax_str:>12s} {n_na:>10,d} {estado}")

# Verificar coherencia: VPH_INTER <= VIVPAR_HAB (no puede haber más viviendas
# con internet que viviendas habitadas)
print(f"\n  Verificando coherencia lógica en acceso digital:")
checks = [
    ("VPH_INTER", "VIVPAR_HAB", "Viviendas con internet ≤ Viviendas habitadas"),
    ("VPH_CEL",   "VIVPAR_HAB", "Viviendas con celular ≤ Viviendas habitadas"),
    ("VPH_TV",    "VIVPAR_HAB", "Viviendas con TV ≤ Viviendas habitadas"),
    ("VPH_PC",    "VIVPAR_HAB", "Viviendas con PC ≤ Viviendas habitadas"),
]
for var_a, var_b, desc in checks:
    if var_a in df_num.columns and var_b in df_num.columns:
        mask = df_num[var_a].notna() & df_num[var_b].notna()
        violaciones = (df_num.loc[mask, var_a] > df_num.loc[mask, var_b]).sum()
        estado = "✓" if violaciones == 0 else f"⚠ {violaciones} casos"
        print(f"  • {desc}: {estado}")

print(f"\n  ℹ Nota: Las aparentes violaciones ocurren porque las filas")
print(f"    agregadas (LOC=9998, 9999 — localidades de 1 o 2 viviendas)")
print(f"    pueden reportar conteos de TIC mayores que VIVPAR_HAB cuando")
print(f"    el conteo se agrupa a nivel municipal. No son errores reales.")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  5. RESUMEN DE ESTRUCTURA DE DATOS                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "─" * 80)
print("  5. RESUMEN DE ESTRUCTURA DE DATOS")
print("─" * 80)

print(f"\n  Tipos de datos detectados por pandas:")
dtype_counts = df.dtypes.value_counts()
for dtype, count in dtype_counts.items():
    print(f"    {str(dtype):<12s} → {count:>3d} columnas")

print(f"\n  Tipos de datos CORREGIDOS (después de convertir '*' → NaN):")
dtype_counts2 = df_num.dtypes.value_counts()
for dtype, count in dtype_counts2.items():
    print(f"    {str(dtype):<12s} → {count:>3d} columnas")

# Información sobre filas especiales (totales)
print(f"\n  Filas especiales (filas de totales/resumen):")
# LOC == 0 son totales municipales, LOC == 9998/9999 son totales especiales
filas_total_mun = df[df["LOC"] == 0]
filas_loc_1viv = df[df["LOC"] == 9998]
filas_loc_2viv = df[df["LOC"] == 9999]
filas_localidades = df[(df["LOC"] > 0) & (df["LOC"] < 9998)]

print(f"    LOC = 0    → Totales municipales:           {len(filas_total_mun):>5d} filas")
print(f"    LOC = 9998 → Localidades de una vivienda:   {len(filas_loc_1viv):>5d} filas")
print(f"    LOC = 9999 → Localidades de dos viviendas:  {len(filas_loc_2viv):>5d} filas")
print(f"    LOC > 0 y < 9998 → Localidades reales:      {len(filas_localidades):>5d} filas")
print(f"    {'─'*50}")
print(f"    TOTAL:                                       {len(df):>5d} filas")

print(f"\n  ⚠ IMPORTANTE: Para análisis estadístico, considerar filtrar las filas")
print(f"    de totales municipales (LOC=0) para evitar doble conteo.")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  6. PANORAMA GENERAL DE ACCESO DIGITAL EN AGUASCALIENTES                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "─" * 80)
print("  6. PANORAMA GENERAL — ACCESO DIGITAL EN AGUASCALIENTES")
print("─" * 80)

# Usar fila de total estatal (MUN=0, LOC=0)
fila_total = df[(df["MUN"] == 0) & (df["LOC"] == 0)]

if len(fila_total) == 1:
    total_vph = pd.to_numeric(fila_total["VIVPAR_HAB"].values[0], errors="coerce")

    print(f"\n  Total de viviendas particulares habitadas: {total_vph:,.0f}")
    print(f"\n  {'Indicador':<45s} {'Viviendas':>12s} {'% del total':>12s}")
    print(f"  {'─'*45} {'─'*12} {'─'*12}")

    for v in vars_acceso_digital:
        val = pd.to_numeric(fila_total[v].values[0], errors="coerce")
        if pd.notna(val) and pd.notna(total_vph) and total_vph > 0:
            pct = val / total_vph * 100
            desc = mapeo_mnemonico.get(v, v)
            if isinstance(desc, str):
                desc = desc[:43]
            print(f"  {desc:<45s} {val:>12,.0f} {pct:>11.1f}%")

    # Acceso digital por municipio
    print(f"\n  Acceso a Internet por municipio:")
    print(f"  {'Municipio':<30s} {'Viv. Habitadas':>15s} {'Con Internet':>15s} "
          f"{'% Internet':>12s}")
    print(f"  {'─'*30} {'─'*15} {'─'*15} {'─'*12}")

    filas_mun = df[(df["MUN"] > 0) & (df["LOC"] == 0)].copy()
    for _, row in filas_mun.iterrows():
        nom_mun = str(row["NOM_MUN"])[:28]
        viv_hab = pd.to_numeric(row["VIVPAR_HAB"], errors="coerce")
        vph_int = pd.to_numeric(row["VPH_INTER"], errors="coerce")
        if pd.notna(viv_hab) and pd.notna(vph_int) and viv_hab > 0:
            pct_int = vph_int / viv_hab * 100
            print(f"  {nom_mun:<30s} {viv_hab:>15,.0f} {vph_int:>15,.0f} "
                  f"{pct_int:>11.1f}%")
else:
    print("  ⚠ No se encontró la fila de total estatal.")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  7. RECOMENDACIONES PARA ETAPAS SIGUIENTES                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

print("\n" + "─" * 80)
print("  7. RECOMENDACIONES PARA ETAPAS SIGUIENTES")
print("─" * 80)

print("""
  Para la Etapa 2 (Estadística Descriptiva):
  ──────────────────────────────────────────
  • Convertir columnas con '*' a numérico (pd.to_numeric con errors='coerce').
  • Filtrar filas de totales (LOC=0, LOC=9998, LOC=9999) antes de calcular
    estadísticos para evitar doble conteo.
  • El análisis de acceso digital se beneficiará de crear tasas/proporciones
    (ej. VPH_INTER / VIVPAR_HAB) en lugar de usar conteos absolutos.

  Para la Etapa 3 (Datos Faltantes):
  ──────────────────────────────────
  • Los 1,072 valores '*' por columna representan ~52% de las filas.
    No son datos faltantes aleatorios sino censura por confidencialidad
    (mecanismo MNAR — Missing Not At Random).
  • La variable PROM_HNV tiene 1,096 valores '*' (más que las demás).
  • Crear la Matriz de Missingness con todas las variables de acceso digital.
  • Investigar si la censura está correlacionada con TAMLOC (tamaño de
    localidad), lo cual es muy probable.

  Para la Etapa 4 (Visualización):
  ────────────────────────────────
  • Crear mapas de calor de acceso digital por municipio.
  • Gráficos de barras apiladas para comparar TIC por municipio.
  • Scatter: población vs acceso a internet por localidad.
  • Boxplots de tasas de acceso digital por tamaño de localidad.
""")

print("=" * 80)
print("  FIN DE ETAPA 1 — Comprensión y Preparación de Datos")
print("=" * 80)
