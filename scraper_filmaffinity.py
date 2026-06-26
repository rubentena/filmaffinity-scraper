# scraper.py

import csv
import re
import subprocess
import time
import argparse
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

RUTAS_NAVEGADOR = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

def detectar_navegador():
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

def descargar_votaciones_filmaffinity(user_id):
    """
    Descarga todas las votaciones de un usuario de FilmAffinity.

    Este script utiliza un método híbrido:
    1. Usa 'undetected-chromedriver' para evitar las protecciones anti-bot.
    2. Abre un navegador visible y se detiene, pidiendo al usuario que resuelva
       manualmente el banner de cookies o cualquier CAPTCHA.
    3. Una vez el usuario confirma, el script reanuda la extracción de forma
       totalmente automática, navegando por todas las páginas de votaciones.
    """
    print("Detectando navegador...")
    nav_path, nav_version = detectar_navegador()
    if not nav_path:
        print("ERROR: No se encontró Google Chrome, Brave ni Chromium instalado.")
        return

    print(f"Usando: {nav_path} (versión {nav_version})")
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    options.binary_location = nav_path
    # El navegador debe ser visible para la intervención manual del usuario.
    driver = uc.Chrome(options=options, use_subprocess=True, browser_executable_path=nav_path, version_main=nav_version)
    driver.maximize_window()
    
    print("Navegador configurado.")
    votaciones = []
    
    try:
        # Se dirige directamente a la vista de lista, que es más estable y fácil de parsear.
        url_lista = f"https://www.filmaffinity.com/es/userratings.php?user_id={user_id}&chv=list"
        print(f"Abriendo página: {url_lista}")
        driver.get(url_lista)

        # --- PAUSA PARA ACCIÓN MANUAL DEL USUARIO ---
        espera = 60
        print("\n" + "="*70)
        print(">>> ACCIÓN REQUERIDA <<<")
        print("1. Revisa la ventana de Brave que se ha abierto.")
        print("2. Si ves un banner de cookies o un CAPTCHA, resuélvelo manualmente.")
        print("3. El script continuará automáticamente en cuanto aceptes las cookies.")
        print("="*70)
        for i in range(espera, 0, -1):
            print(f"  Continuando en {i} segundos... (acepta las cookies en el navegador)", end="\r")
            time.sleep(1)
        print("\nReanudando automatización...")
        
        print("\nReanudando automatización... ¡Comienza la extracción!")

        # --- BUCLE DE EXTRACCIÓN AUTOMÁTICA ---
        page_num = 1
        while True:
            if page_num > 1:
                url = f"https://www.filmaffinity.com/es/userratings.php?user_id={user_id}&p={page_num}&chv=list"
                print(f"Procesando página {page_num}...")
                driver.get(url)
                time.sleep(3) # Pausa para asegurar la carga de la nueva página

            # Espera explícita a que el contenedor de las películas esté cargado
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "movie-card"))
                )
            except Exception:
                print(f"La página {page_num} no cargó contenido nuevo. Finalizando.")
                break

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Selector para cada fila de película en la vista de lista
            lista_peliculas = soup.select("div.card-body > div.row.mb-4")

            if not lista_peliculas:
                print("No se encontraron más películas. Se ha llegado al final.")
                break

            for pelicula in lista_peliculas:
                titulo_elem = pelicula.select_one('div.mc-title a')
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else 'N/A'
                
                year_elem = pelicula.select_one('span.mc-year')
                year = year_elem.get_text(strip=True) if year_elem else 'N/A'
                
                votacion_elem = pelicula.select_one('div.fa-user-rat-box')
                votacion = votacion_elem.get_text(strip=True) if votacion_elem else 'N/A'
                
                votaciones.append({'titulo': titulo, 'año': year, 'mi_votacion': votacion})

            print(f"  > Página {page_num} procesada. {len(votaciones)} películas acumuladas.")
            page_num += 1
            time.sleep(1) # Pausa cortés entre páginas

    finally:
        print("Cerrando navegador...")
        driver.quit()

    if votaciones:
        nombre_archivo = f'votaciones_{user_id}.csv'
        print(f"\nGuardando {len(votaciones)} votaciones en el archivo '{nombre_archivo}'...")
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['titulo', 'año', 'mi_votacion']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(votaciones)
        print(f"¡Proceso completado! 🎉 El archivo '{nombre_archivo}' está listo.")
    else:
        print("No se encontraron votaciones. Asegúrate de que la lista era visible antes de pulsar Enter.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga las votaciones de un usuario de FilmAffinity.")
    parser.add_argument("user_id", help="El ID de usuario de tu perfil de FilmAffinity.")
    args = parser.parse_args()
    
    descargar_votaciones_filmaffinity(args.user_id)