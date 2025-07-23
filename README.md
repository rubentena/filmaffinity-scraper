# Descargador de Votaciones de FilmAffinity

Este es un script de Python para descargar todas las votaciones (título, año y nota) de un perfil de usuario público de FilmAffinity y guardarlas en un archivo `.csv`.

El script utiliza un **método híbrido** para superar las protecciones anti-bot más avanzadas: abre un navegador para que el usuario resuelva manualmente cualquier control de seguridad inicial (como un banner de cookies o un CAPTCHA) y, una vez confirmado, procede a extraer todos los datos de forma completamente automática.

---
## Características

-   🍿 **Supera protecciones anti-bot** complejas usando `undetected-chromedriver`.
-   🔄 **Recorre todas las páginas** de votaciones de un usuario.
-   ✍️ **Guarda los datos** en un archivo CSV limpio y fácil de usar (`votaciones_TU_USER_ID.csv`).
-   🤖 **Proceso interactivo** para garantizar el éxito donde la automatización completa falla.

---
## Requisitos

-   Python 3.8 o superior.
-   Tener instalado el navegador **Google Chrome**.

---
## Instalación

1.  **Clona o descarga este repositorio.**
    ```bash
    git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
    cd TU_REPOSITORIO
    ```

2.  **Instala las dependencias** necesarias usando el archivo `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

---
## Uso

1.  **Encuentra tu ID de Usuario de FilmAffinity.**
    -   Ve a tu perfil de FilmAffinity y haz clic en "Mis votaciones".
    -   La URL será algo como: `https://www.filmaffinity.com/es/userratings.php?user_id=860588`
    -   Tu ID de usuario es el número que aparece al final (en este caso, `860588`).

2.  **Ejecuta el script desde tu terminal.**
    -   Pasa tu ID de usuario como argumento después del nombre del script.
    ```bash
    python scraper.py TU_USER_ID
    ```
    -   *Ejemplo:*
    ```bash
    python scraper.py 860588
    ```

3.  **Sigue las instrucciones en la terminal.**
    -   Se abrirá una ventana de Chrome.
    -   El script te pedirá que resuelvas el banner de cookies o cualquier CAPTCHA.
    -   Una vez veas tu lista de películas en la pantalla, vuelve a la terminal y pulsa **Enter**.
    -   El script comenzará a descargar tus votaciones automáticamente.

---
## Salida

El script creará un archivo llamado **`votaciones_TU_USER_ID.csv`** en la misma carpeta, con tres columnas: `titulo`, `año` y `mi_votacion`.

---
## Nota Importante

La efectividad de este script depende de la estructura del código HTML de FilmAffinity. Si la web cambia en el futuro, es posible que el script necesite ajustes en sus selectores. *Versión funcional a julio de 2025.*

---
## Licencia

Este proyecto está bajo la Licencia MIT.