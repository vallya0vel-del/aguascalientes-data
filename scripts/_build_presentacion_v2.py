"""
Genera un HTML-resumen v2 para guía de la presentación final.
Embebe las imágenes como base64 para que sea un solo archivo portable.
Archivo de salida: presentacion_guia_v2.html  (no sobreescribe el v1)
"""
import os, base64

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "output")
HTML_PATH = os.path.join(OUTPUT, "presentacion_guia_v2.html")


def img_b64(filename):
    """Lee un PNG de output/ y devuelve la cadena data-URI base64."""
    path = os.path.join(OUTPUT, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"


# ── Secciones ────────────────────────────────────────────────────────────

sections = []

# =====================================================================
# 1. ENTENDIMIENTO DEL PROBLEMA
# =====================================================================
sections.append("""
<section id="s1">
  <h2>1 &mdash; Entendimiento del Problema</h2>
  <div class="card">
    <h3>Hipótesis</h3>
    <p>El acceso a Tecnologías de la Información y Comunicación (TIC) en el estado de
       <strong>Aguascalientes</strong> presenta una <strong>brecha digital significativa</strong>
       entre localidades urbanas y rurales, determinada principalmente por el tamaño de la
       localidad y su ubicación geográfica.</p>
  </div>
  <div class="card">
    <h3>¿Por qué importa?</h3>
    <ul>
      <li>El acceso digital condiciona oportunidades de educación, salud y empleo.</li>
      <li>El 86&percnt; de las localidades de Aguascalientes tienen <strong>&lt;250 habitantes</strong>:
          la "ruralidad profunda" del estado.</li>
      <li>Identificar los patrones de esta brecha permite dirigir mejor la inversión pública en
          conectividad.</li>
    </ul>
  </div>
  <div class="card">
    <h3>Fuente de datos</h3>
    <p><strong>INEGI &mdash; Censo de Población y Vivienda 2020</strong>, Iter estatal de
       Aguascalientes. Contiene indicadores a nivel <em>localidad</em> (2,022 localidades,
       286 variables).</p>
    <p>Variables clave: 13 indicadores TIC (radio, TV, PC, teléfono, celular, internet,
       TV de paga, streaming, videojuegos y 4 indicadores de carencia), más variables
       demográficas y socioeconómicas.</p>
  </div>
</section>
""")

# =====================================================================
# 2. DESCRIPCIÓN DE LOS DATOS
# =====================================================================
sections.append(f"""
<section id="s2">
  <h2>2 &mdash; Descripción de los Datos</h2>
  <div class="card">
    <h3>Panorama general</h3>
    <table class="data-table">
      <tr><th>Dimensión</th><th>Valor</th></tr>
      <tr><td>Registros totales</td><td>2,058</td></tr>
      <tr><td>Localidades reales (filtradas)</td><td>2,022</td></tr>
      <tr><td>Variables</td><td>286</td></tr>
      <tr><td>11 municipios</td><td>Aguascalientes, Asientos, Calvillo, Cosío, Jesús María, etc.</td></tr>
    </table>
  </div>
  <div class="two-col">
    <div class="card">
      <h3>Distribución de localidades por TAMLOC</h3>
      <img src="{img_b64('etapa4_distribucion_localidades_tamloc.png')}" alt="TAMLOC">
      <p class="caption">El 86&percnt; de las localidades tienen &lt;250 habitantes (TAMLOC&nbsp;1).
         Solamente 1 localidad supera los 500,000 hab. (la capital).</p>
    </div>
    <div class="card">
      <h3>Distribución de la población por municipio</h3>
      <img src="{img_b64('etapa4_distribucion_poblacion_municipio.png')}" alt="Pob municipio">
      <p class="caption">El municipio de Aguascalientes concentra ~70&percnt; de la población estatal.</p>
    </div>
  </div>
  <div class="card">
    <h3>Pirámide poblacional</h3>
    <img src="{img_b64('etapa4_piramide_poblacional.png')}" alt="Pirámide" class="wide-img">
    <p class="caption">Base ligeramente más estrecha que el cuerpo &rarr; transición demográfica en curso.
       Distribución simétrica entre hombres y mujeres.</p>
  </div>
</section>
""")

# =====================================================================
# 3. LIMPIEZA
# =====================================================================
sections.append(f"""
<section id="s3">
  <h2>3 &mdash; Limpieza de Datos</h2>
  <div class="card">
    <h3>¿Qué encontramos?</h3>
    <ul>
      <li><strong>53&percnt;</strong> de las localidades tienen datos censurados por el INEGI
          (marcados con <code>*</code>).</li>
      <li>La censura afecta a <strong>273 de 281</strong> variables numéricas (97&percnt;).</li>
      <li>Es <strong>censura en bloque</strong>: si una variable TIC está censurada en una localidad,
          <em>todas</em> las demás también lo están.</li>
    </ul>
  </div>
  <div class="two-col">
    <div class="card">
      <h3>Matriz de datos faltantes</h3>
      <img src="{img_b64('etapa3_matriz_missingness.png')}" alt="Missingness">
      <p class="caption">Cada fila = localidad, cada columna = variable. Amarillo = dato censurado.
         Se observa un bloque compacto: la censura es todo-o-nada.</p>
    </div>
    <div class="card">
      <h3>¿Por qué ocurre?</h3>
      <img src="{img_b64('etapa3_censura_vs_tamloc.png')}" alt="Censura vs TAMLOC">
      <p class="caption">El 61.5&percnt; de las localidades de &lt;250 hab. están censuradas,
         vs. 0&percnt; en localidades grandes. <strong>Es por confidencialidad estadística.</strong></p>
    </div>
  </div>
  <div class="card highlight-box">
    <h3>Mecanismo identificado: <span class="tag-red">MNAR</span></h3>
    <p>Los datos <strong>no</strong> faltan al azar. Faltan porque las localidades son tan pequeñas
       que publicar cifras exactas permitiría identificar a los habitantes.
       Prueba χ² de independencia: <strong>p &lt; 0.001</strong>.</p>
    <p><strong>Decisión:</strong> No es correcto imputar con media/mediana. Trabajamos con
       el <strong>subconjunto completo (n ≈ 950)</strong> y reportamos el sesgo de selección.</p>
  </div>
</section>
""")

# =====================================================================
# 4. IMPUTACIÓN
# =====================================================================
sections.append(f"""
<section id="s4">
  <h2>4 &mdash; Estrategia ante Datos Faltantes</h2>
  <div class="card">
    <h3>¿Por qué NO imputamos?</h3>
    <p>Al ser datos <strong>MNAR</strong> (Missing Not At Random), cualquier método de
       imputación estándar introduciría sesgo:</p>
    <ul>
      <li><strong>Imputar con media/mediana</strong> &rarr; asigna valores de <em>localidades grandes</em>
          a localidades rurales pequeñas.</li>
      <li><strong>Eliminar registros censurados</strong> &rarr; perdemos el 53&percnt; del dataset.</li>
      <li><strong>Imputar con 0</strong> &rarr; incorrecto: "no tener dato" &ne; "no tener TIC".</li>
    </ul>
  </div>
  <div class="card">
    <h3>Estrategia adoptada: Análisis en subconjuntos</h3>
    <table class="data-table">
      <tr><th>Subconjunto</th><th>n</th><th>Uso</th></tr>
      <tr><td><strong>A &mdash; Datos completos</strong></td><td>~950</td>
          <td>Correlaciones, PCA, clustering</td></tr>
      <tr><td><strong>B &mdash; Censurados</strong></td><td>~1,072</td>
          <td>Análisis demográfico (población, municipio)</td></tr>
      <tr><td><strong>Completo + indicador</strong></td><td>2,022</td>
          <td>Brecha urbano-rural con variable binaria CENSURADO</td></tr>
    </table>
  </div>
  <div class="card">
    <h3>Perfil de los subconjuntos</h3>
    <table class="data-table">
      <tr><th>Característica</th><th>Completos</th><th>Censurados</th></tr>
      <tr><td>Población media</td><td>1,494</td><td>6</td></tr>
      <tr><td>Población mediana</td><td>56</td><td>4</td></tr>
    </table>
    <p class="caption">Los censurados son localidades de muy pocos habitantes;
       analizarlos por separado nos da una imagen real de la &ldquo;ruralidad profunda.&rdquo;</p>
  </div>
</section>
""")

# =====================================================================
# 5. ANÁLISIS EXPLORATORIO
# =====================================================================
sections.append(f"""
<section id="s5">
  <h2>5 &mdash; Análisis Exploratorio</h2>

  <div class="card">
    <h3>Distribuciones de acceso digital (Histogramas)</h3>
    <img src="{img_b64('etapa4_histogramas_kde.png')}" alt="Histogramas KDE" class="wide-img">
    <p class="caption">La mayoría de las localidades tienen tasas <strong>bajas</strong> de acceso,
       especialmente en variables avanzadas (streaming, videojuegos, teléfono fijo).
       Celular es la tecnología con mayor penetración (~93&percnt; promedio).</p>
  </div>

  <div class="card">
    <h3>Brecha digital: Urbano vs Rural</h3>
    <img src="{img_b64('etapa4_brecha_digital.png')}" alt="Brecha digital" class="wide-img">
    <p class="caption">Las localidades urbanas (&ge;2,500 hab.) superan a las rurales
       en todos los indicadores: <strong>~5x</strong> en internet, <strong>~10x</strong> en
       PC y streaming. El celular es la única TIC donde la brecha es menor (~2x).</p>
  </div>

  <div class="two-col">
    <div class="card">
      <h3>Boxplots por municipio</h3>
      <img src="{img_b64('etapa4_boxplot_municipio.png')}" alt="Boxplot municipio">
      <p class="caption">Jesús María y Aguascalientes lideran en acceso.
         El Llano, Tepezalá y San José de Gracia tienen las medianas más bajas.</p>
    </div>
    <div class="card">
      <h3>Violin plots: 9 variables TIC</h3>
      <img src="{img_b64('etapa4_violin_todas_tic.png')}" alt="Violin TIC">
      <p class="caption">Internet y celular muestran la mayor densidad alrededor de tasas medias-altas.
         Streaming y videojuegos se concentran cerca del 0.</p>
    </div>
  </div>

  <div class="card">
    <h3>Mapa geográfico: Tasa de Internet</h3>
    <img src="{img_b64('etapa4_mapa_internet.png')}" alt="Mapa Internet" class="wide-img">
    <p class="caption"><strong>Gradiente centro-periferia:</strong> las localidades cercanas a la
       capital muestran mayor acceso a internet, mientras que las periferias rurales hacia el oeste
       y norte tienen acceso mínimo.</p>
  </div>

  <div class="card">
    <h3>Correlaciones: TIC + Variables socioeconómicas</h3>
    <img src="{img_b64('etapa4_heatmap_correlacion_ampliada.png')}" alt="Heatmap correlación" class="wide-img">
    <p class="caption">Internet &harr; PC: <strong>r = 0.96</strong>.
       Internet &harr; Streaming: <strong>r = 0.90</strong>.
       La <strong>escolaridad</strong> (GRAPROES) es un predictor fuerte del acceso digital.</p>
  </div>

  <div class="card">
    <h3>Índice Compuesto de Acceso Digital (ICAD)</h3>
    <img src="{img_b64('etapa3_icad.png')}" alt="ICAD" class="wide-img">
    <p class="caption">El ICAD resume las 9 variables TIC positivas en un solo indicador [0-1].
       <strong>92.8%</strong> de las localidades clasifican como "Muy bajo".
       Solo 2 localidades (incluyendo la capital) alcanzan nivel "Alto".</p>
  </div>
</section>
""")

# =====================================================================
# 6. TÉCNICAS DE CIENCIA DE DATOS
# =====================================================================
sections.append(f"""
<section id="s6">
  <h2>6 &mdash; Técnicas de Ciencia de Datos</h2>

  <div class="card">
    <h3>PCA &mdash; Reducción de dimensionalidad</h3>
    <p>Aplicamos <strong>Análisis de Componentes Principales</strong> para condensar 15 variables
       en componentes interpretables.</p>
    <img src="{img_b64('etapa5_pca_scree.png')}" alt="Scree plot" class="wide-img">
    <p class="caption"><strong>3 componentes explican 67.2&percnt;</strong> de la varianza total.
       PC1 (37.6&percnt;) representa el <em>nivel general de acceso digital</em> &mdash;
       las localidades con PC1 alto tienen acceso alto a <strong>todas</strong> las TIC simultáneamente.</p>
  </div>

  <div class="card">
    <h3>Biplot: localidades en el espacio PCA</h3>
    <img src="{img_b64('etapa5_pca_biplot.png')}" alt="Biplot" class="wide-img">
    <p class="caption">Cada punto es una localidad coloreada por municipio.
       Las flechas muestran la dirección de cada variable original.
       Internet, PC y Streaming apuntan en la misma dirección (alta colinealidad),
       mientras que las variables de carencia apuntan en dirección opuesta.</p>
  </div>

  <div class="card">
    <h3>K-Means &mdash; Clasificación de localidades</h3>
    <div class="two-col">
      <div>
        <img src="{img_b64('etapa5_kmeans_elbow_silueta.png')}" alt="Elbow">
        <p class="caption">El método del codo y la silueta coinciden en <strong>k = 2</strong>
           como el número óptimo de clusters.</p>
      </div>
      <div>
        <img src="{img_b64('etapa5_kmeans_pca.png')}" alt="KMeans PCA">
        <p class="caption">Los 2 clusters son claramente separables en el espacio PCA.</p>
      </div>
    </div>
  </div>

  <div class="card">
    <h3>Perfiles de los clusters</h3>
    <img src="{img_b64('etapa5_radar_clusters.png')}" alt="Radar" class="wide-img">
    <table class="data-table" style="margin-top:1rem;">
      <tr><th>Cluster</th><th>n</th><th>Internet</th><th>Celular</th><th>PC</th><th>Perfil</th></tr>
      <tr><td style="background:#2166AC;color:#fff;">Cluster 0</td>
          <td>885 (93.6&percnt;)</td><td>29&percnt;</td><td>90&percnt;</td><td>17&percnt;</td>
          <td>Solo telecom básica</td></tr>
      <tr><td style="background:#D6604D;color:#fff;">Cluster 1</td>
          <td>61 (6.4&percnt;)</td><td>100&percnt;</td><td>133&percnt;*</td><td>85&percnt;</td>
          <td>Alta conectividad</td></tr>
    </table>
    <p class="caption" style="margin-top:0.5rem;">* Tasas &gt;100&percnt; porque una vivienda puede tener
       múltiples líneas celulares. El radar muestra cómo las TIC avanzadas (streaming,
       videojuegos, PC) son casi exclusivas del Cluster 1.</p>
  </div>
</section>
""")

# =====================================================================
# 7. EVALUACIÓN DE RESULTADOS
# =====================================================================
sections.append(f"""
<section id="s7">
  <h2>7 &mdash; Evaluación de Resultados</h2>

  <div class="card">
    <h3>Mapa geográfico de los clusters</h3>
    <img src="{img_b64('etapa5_mapa_clusters.png')}" alt="Mapa clusters" class="wide-img">
    <p class="caption">Las localidades de <strong>alta conectividad</strong> (rojo-naranja) se concentran
       en la zona metropolitana y cabeceras municipales. La inmensa mayoría del territorio
       pertenece al cluster de <strong>solo telecom básica</strong> (azul).</p>
  </div>

  <div class="card">
    <h3>Validación cruzada de los clusters</h3>
    <ul>
      <li><strong>Silueta promedio:</strong> 0.69 — separación robusta.</li>
      <li><strong>Concordancia K-Means &harr; Jerárquico:</strong> 98.3&percnt; &mdash;
          dos algoritmos distintos llegan prácticamente al mismo resultado.</li>
      <li><strong>DBSCAN:</strong> identificó 4 outliers (localidades con patrones atípicos),
          confirmando la estructura de 2 grupos.</li>
    </ul>
  </div>

  <div class="card highlight-box">
    <h3>Conclusiones principales</h3>
    <ol>
      <li><strong>La brecha digital es real y dramática.</strong> Existe una separación clara entre
          un pequeño grupo de localidades bien conectadas (6.4&percnt;) y la gran mayoría
          con acceso limitado (93.6&percnt;).</li>
      <li><strong>Es multidimensional, no solo "internet".</strong> PC, streaming, videojuegos y
          teléfono fijo están casi ausentes simultáneamente en localidades rurales.</li>
      <li><strong>La escolaridad y el tamaño de la localidad</strong> son los mejores predictores
          del acceso digital.</li>
      <li><strong>Existe un gradiente centro-periferia:</strong> el acceso disminuye conforme la
          localidad se aleja de la capital.</li>
      <li><strong>Hipótesis confirmada:</strong> el tamaño de la localidad y la geografía determinan
          significativamente el acceso a TIC en Aguascalientes.</li>
    </ol>
  </div>

  <div class="card">
    <h3>Implicaciones</h3>
    <ul>
      <li>Las 885 localidades del Cluster 0 son prioritarias para inversión en infraestructura.</li>
      <li>La inversión en <strong>educación y conectividad</strong> deben ir de la mano
          (correlación escolaridad-acceso).</li>
      <li>El celular es la <em>puerta de entrada</em> digital en zonas rurales — programas de
          inclusión digital podrían aprovechar esta penetración existente.</li>
    </ul>
  </div>
</section>
""")

# ── Armado del HTML final ────────────────────────────────────────────────

nav_items = [
    ("s1", "1. Problema"),
    ("s2", "2. Datos"),
    ("s3", "3. Limpieza"),
    ("s4", "4. Imputación"),
    ("s5", "5. Exploratorio"),
    ("s6", "6. Técnicas"),
    ("s7", "7. Resultados"),
]

nav_html = "\n".join(
    f'        <a href="#{sid}">{label}</a>' for sid, label in nav_items
)

body_html = "\n".join(sections)

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guía de Presentación v2 — Brecha Digital en Aguascalientes</title>
<style>
  :root {{
    --bg: #f5f6fa;
    --card: #ffffff;
    --accent: #2c3e7a;
    --accent-light: #e8ecf8;
    --text: #2d3436;
    --muted: #636e72;
    --red: #d63031;
    --green: #00b894;
    --border: #dfe6e9;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}
  /* ── NAV ── */
  nav {{
    position: sticky; top: 0; z-index: 100;
    background: var(--accent);
    padding: .6rem 1.5rem;
    display: flex; flex-wrap: wrap; gap: .5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.15);
  }}
  nav a {{
    color: #ffffffcc; text-decoration: none; font-size: .85rem;
    padding: .3rem .7rem; border-radius: 4px; transition: .2s;
  }}
  nav a:hover {{ background: rgba(255,255,255,.15); color: #fff; }}

  /* ── HEADER ── */
  header {{
    background: linear-gradient(135deg, var(--accent), #1a2557);
    color: #fff; text-align: center; padding: 3rem 1.5rem 2.5rem;
  }}
  header h1 {{ font-size: 1.9rem; font-weight: 700; margin-bottom: .4rem; }}
  header p {{ opacity: .85; font-size: 1rem; }}

  /* ── SECTIONS ── */
  main {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}
  section {{ margin-bottom: 3rem; }}
  section h2 {{
    color: var(--accent); font-size: 1.5rem; font-weight: 700;
    border-bottom: 3px solid var(--accent); padding-bottom: .4rem;
    margin-bottom: 1.5rem;
  }}

  /* ── CARDS ── */
  .card {{
    background: var(--card);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 6px rgba(0,0,0,.06);
    border: 1px solid var(--border);
  }}
  .card h3 {{
    color: var(--accent); font-size: 1.1rem; margin-bottom: .7rem;
  }}
  .card ul, .card ol {{ padding-left: 1.3rem; }}
  .card li {{ margin-bottom: .3rem; }}

  /* ── IMAGES ── */
  .card img {{
    width: 100%; max-width: 900px;
    display: block; margin: .8rem auto;
    border-radius: 6px;
    border: 1px solid var(--border);
  }}
  .wide-img {{ max-width: 960px; }}
  .caption {{
    font-size: .88rem; color: var(--muted); margin-top: .5rem;
    text-align: center; font-style: italic;
  }}

  /* ── TWO COLUMNS ── */
  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
  }}
  @media (max-width: 780px) {{ .two-col {{ grid-template-columns: 1fr; }} }}

  /* ── DATA TABLE ── */
  .data-table {{
    border-collapse: collapse; width: 100%; font-size: .9rem;
  }}
  .data-table th, .data-table td {{
    padding: .55rem .8rem; text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  .data-table th {{ background: var(--accent-light); font-weight: 600; }}

  /* ── HIGHLIGHT BOX ── */
  .highlight-box {{
    background: #fffbea;
    border-left: 4px solid #f9ca24;
  }}
  .tag-red {{
    background: var(--red); color: #fff;
    padding: .15rem .5rem; border-radius: 4px; font-size: .9rem;
  }}

  code {{
    background: #f1f2f6; padding: .15rem .35rem; border-radius: 3px;
    font-size: .88rem;
  }}

  /* ── FOOTER ── */
  footer {{
    text-align: center; padding: 2rem; color: var(--muted);
    font-size: .82rem; border-top: 1px solid var(--border);
  }}
</style>
</head>
<body>

<header>
  <h1>Brecha Digital en Aguascalientes</h1>
  <p>Análisis del Censo de Población y Vivienda 2020 &mdash; INEGI</p>
  <p style="margin-top:.5rem;opacity:.7;font-size:.88rem;">Guía de presentación final &mdash; v2</p>
</header>

<nav>
{nav_html}
</nav>

<main>
{body_html}
</main>

<footer>
  Generado automáticamente a partir de los outputs del proyecto (v2 &mdash; colores actualizados).<br>
  Datos: INEGI, Censo 2020, Iter estatal Aguascalientes.
</footer>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✓ HTML v2 generado: {HTML_PATH}")
print(f"  Tamaño: {os.path.getsize(HTML_PATH) / (1024*1024):.1f} MB")
