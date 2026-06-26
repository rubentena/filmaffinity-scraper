import re
import subprocess
import streamlit as st
import threading
import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="FilmAffinity Scraper", page_icon="🎬", layout="centered")

RUTAS_NAVEGADOR = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

def detectar_navegador():
    """Devuelve (ruta, version_major) del primer navegador Chromium encontrado."""
    for ruta in RUTAS_NAVEGADOR:
        try:
            resultado = subprocess.run(
                [ruta, "--version"], capture_output=True, text=True, timeout=5
            )
            match = re.search(r"(\d+)\.\d+\.\d+", resultado.stdout)
            if match:
                return ruta, int(match.group(1))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None, None

# cache_resource persiste entre reruns y es accesible desde threads
@st.cache_resource
def get_state():
    return {
        "estado": "idle",   # idle | iniciando | esperando_cookies | scraping | completado | error
        "pagina": 0,
        "total": 0,
        "votaciones": [],
        "error": "",
        "cookies_event": None,
        "user_id": "",
    }

_state = get_state()


def run_scraper(user_id):
    driver = None
    try:
        nav_path, nav_version = detectar_navegador()
        if not nav_path:
            _state["error"] = "No se encontró Google Chrome, Brave ni Chromium instalado."
            _state["estado"] = "error"
            return

        options = uc.ChromeOptions()
        options.add_argument("--log-level=3")
        options.binary_location = nav_path
        driver = uc.Chrome(
            options=options,
            use_subprocess=True,
            browser_executable_path=nav_path,
            version_main=nav_version,
        )
        driver.maximize_window()
        driver.get(f"https://www.filmaffinity.com/es/userratings.php?user_id={user_id}&chv=list")

        _state["estado"] = "esperando_cookies"
        _state["cookies_event"].wait()

        _state["estado"] = "scraping"
        votaciones = []
        page_num = 1

        while True:
            if page_num > 1:
                driver.get(
                    f"https://www.filmaffinity.com/es/userratings.php"
                    f"?user_id={user_id}&p={page_num}&chv=list"
                )
                time.sleep(3)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "movie-card"))
                )
            except Exception:
                break

            soup = BeautifulSoup(driver.page_source, "html.parser")
            peliculas = soup.select("div.card-body > div.row.mb-4")
            if not peliculas:
                break

            for p in peliculas:
                t_el = p.select_one("div.mc-title a")
                y_el = p.select_one("span.mc-year")
                v_el = p.select_one("div.fa-user-rat-box")
                votaciones.append({
                    "titulo":      t_el.get_text(strip=True) if t_el else "N/A",
                    "año":         y_el.get_text(strip=True) if y_el else "N/A",
                    "mi_votacion": v_el.get_text(strip=True) if v_el else "N/A",
                })

            _state["pagina"] = page_num
            _state["total"] = len(votaciones)
            page_num += 1
            time.sleep(1)

        driver.quit()
        _state["votaciones"] = votaciones
        _state["estado"] = "completado"

    except Exception as e:
        _state["error"] = str(e)
        _state["estado"] = "error"
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ── UI ─────────────────────────────────────────────────────────────

st.title("🎬 FilmAffinity Scraper")
st.caption("Descarga todas tus votaciones en un CSV")

estado = _state["estado"]

# ── IDLE ───────────────────────────────────────────────────────────
if estado == "idle":
    st.info(
        "Encuentra tu **User ID** en la URL de tus votaciones:\n\n"
        "`filmaffinity.com/es/userratings.php?user_id=`**XXXXXX**"
    )
    with st.form("inicio"):
        user_id = st.text_input("User ID", placeholder="ej. 860588")
        go = st.form_submit_button("🚀 Iniciar", use_container_width=True, type="primary")

    if go and user_id.strip():
        _state.update({
            "estado": "iniciando",
            "cookies_event": threading.Event(),
            "pagina": 0,
            "total": 0,
            "votaciones": [],
            "error": "",
            "user_id": user_id.strip(),
        })
        threading.Thread(target=run_scraper, args=(user_id.strip(),), daemon=True).start()
        st.rerun()

# ── INICIANDO ──────────────────────────────────────────────────────
elif estado == "iniciando":
    st.info("⏳ Abriendo Brave Browser...")
    time.sleep(0.5)
    st.rerun()

# ── ESPERANDO COOKIES ──────────────────────────────────────────────
elif estado == "esperando_cookies":
    st.markdown("### 🌐 Brave Browser está abierto")
    st.warning(
        "FilmAffinity se está cargando en Brave.  \n"
        "**Acepta el banner de cookies** y vuelve aquí."
    )
    if st.button("✅ He aceptado las cookies — ¡Empezar!", use_container_width=True, type="primary"):
        _state["cookies_event"].set()
        st.rerun()
    time.sleep(1)
    st.rerun()

# ── SCRAPING ───────────────────────────────────────────────────────
elif estado == "scraping":
    pagina = _state["pagina"]
    total  = _state["total"]
    st.markdown("### 🔄 Descargando votaciones...")
    col1, col2 = st.columns(2)
    col1.metric("Página actual", pagina if pagina else "—")
    col2.metric("Películas descargadas", total)
    st.progress(min(pagina / 40, 0.95))
    time.sleep(1)
    st.rerun()

# ── COMPLETADO ─────────────────────────────────────────────────────
elif estado == "completado":
    votaciones = _state["votaciones"]
    st.success(f"✅ ¡Completado! **{len(votaciones)} votaciones** descargadas.")

    df = pd.DataFrame(votaciones)
    df["mi_votacion"] = pd.to_numeric(df["mi_votacion"], errors="coerce")
    df["año"]         = pd.to_numeric(df["año"],         errors="coerce")

    with st.expander("🔍 Filtrar y ordenar", expanded=True):
        busqueda = st.text_input("Buscar título", placeholder="ej. Blade Runner")
        col1, col2 = st.columns(2)
        orden = col1.selectbox(
            "Ordenar por",
            ["Puntuación ↓", "Puntuación ↑", "Año ↓", "Año ↑", "Título A-Z"],
        )
        min_nota, max_nota = col2.slider("Rango de nota", 1, 10, (1, 10))

    df_filtrado = df.copy()
    if busqueda:
        df_filtrado = df_filtrado[df_filtrado["titulo"].str.contains(busqueda, case=False, na=False)]
    df_filtrado = df_filtrado[
        df_filtrado["mi_votacion"].between(min_nota, max_nota, inclusive="both")
    ]
    orden_map = {
        "Puntuación ↓": ("mi_votacion", False),
        "Puntuación ↑": ("mi_votacion", True),
        "Año ↓":        ("año", False),
        "Año ↑":        ("año", True),
        "Título A-Z":   ("titulo", True),
    }
    col_ord, asc = orden_map[orden]
    df_filtrado = df_filtrado.sort_values(col_ord, ascending=asc)

    st.dataframe(df_filtrado, use_container_width=True, height=420)
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} votaciones")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar CSV completo",
        data=csv_data,
        file_name=f"votaciones_{_state['user_id']}.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )

    if st.button("🔄 Nueva descarga", use_container_width=True):
        _state["estado"] = "idle"
        st.rerun()

# ── ERROR ──────────────────────────────────────────────────────────
elif estado == "error":
    st.error(f"❌ Error: {_state['error']}")
    if st.button("🔄 Reintentar", use_container_width=True):
        _state["estado"] = "idle"
        st.rerun()
