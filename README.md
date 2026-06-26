# Descargador de Votaciones de FilmAffinity

Descarga todas tus votaciones (título, año y nota) de un perfil público de FilmAffinity y las guarda en un archivo `.csv`.

Utiliza un **método híbrido** para superar las protecciones anti-bot: abre un navegador para que el usuario resuelva manualmente el banner de cookies y, una vez confirmado, extrae todos los datos de forma automática recorriendo todas las páginas.

---

## Características

- 🍿 **Supera protecciones anti-bot** usando `undetected-chromedriver`.
- 🔄 **Recorre todas las páginas** de votaciones automáticamente.
- ✍️ **Guarda los datos** en un CSV limpio (`votaciones_TU_USER_ID.csv`).
- 🖥️ **Interfaz web** con barra de progreso, filtros y descarga directa (`app.py`).
- 🔍 **Detecta automáticamente** el navegador instalado (Chrome, Brave, Chromium).

---

## Requisitos

- Python 3.8 o superior.
- **Google Chrome**, **Brave** o **Chromium** instalado.

---

## Instalación

```bash
git clone https://github.com/rubentena/filmaffinity-scraper.git
cd filmaffinity-scraper
pip install -r requirements.txt
```

---

## Uso

### Opción A — Interfaz web (recomendado)

```bash
streamlit run app.py
```

Se abrirá una página web en `http://localhost:8501` donde podrás:
- Introducir tu User ID.
- Ver el progreso en tiempo real.
- Filtrar y ordenar los resultados.
- Descargar el CSV con un botón.

### Opción B — Línea de comandos

```bash
python scraper_filmaffinity.py TU_USER_ID
```

**¿Dónde encuentro mi User ID?**  
Ve a *Mis votaciones* en FilmAffinity. La URL tendrá la forma:  
`https://www.filmaffinity.com/es/userratings.php?user_id=`**123456**

---

## Salida

Archivo **`votaciones_TU_USER_ID.csv`** con tres columnas: `titulo`, `año` y `mi_votacion`.

---

## Nota

La efectividad depende de la estructura HTML de FilmAffinity. Si la web cambia, puede que los selectores necesiten ajustes. *Versión funcional a junio de 2026.*

---

## Autor

**Rubén Tena Martínez** — [LinkedIn](https://www.linkedin.com/in/rubén-t-17b238a2)

---

## Licencia

MIT
