# scraper.py

import csv
import time
import argparse
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    print("Configurando el navegador...")
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    # El navegador debe ser visible para la intervención manual del usuario.
    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.maximize_window()
    
    print("Navegador configurado.")
    votaciones = []
    
    try:
        # Se dirige directamente a la vista de lista, que es más estable y fácil de parsear.
        url_lista = f"https://www.filmaffinity.com/es/userratings.php?user_id={user_id}&chv=list"
        print(f"Abriendo página: {url_lista}")
        driver.get(url_lista)

        # --- PAUSA PARA ACCIÓN MANUAL DEL USUARIO ---
        print("\n" + "="*70)
        print(">>> ACCIÓN REQUERIDA <<<")
        print("1. Revisa la ventana de Chrome que se ha abierto.")
        print("2. Si ves un banner de cookies o un CAPTCHA, resuélvelo manualmente.")
        print("3. Espera hasta que veas tu lista de películas cargada en la página.")
        print("4. Una vez la lista sea visible, vuelve a esta terminal y pulsa Enter.")
        print("="*70)
        input("Pulsa Enter para que el script comience a descargar los datos...")
        
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