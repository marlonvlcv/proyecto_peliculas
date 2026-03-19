# Importar librerias
from pathlib import Path

# Rutas principales
CSV_PATH = Path(r"C:\Users\marlo\proyecto_peliculas\CineSeven_db.csv")
IMAGES_BASE_PATH = Path(r"C:\Users\marlo\proyecto_peliculas\posters")
USUARIOS_PATH = Path(r"C:\Users\marlo\proyecto_peliculas\usuarios.json")
FAVORITOS_PATH = Path(r"C:\Users\marlo\proyecto_peliculas\favortios.json")  
IMAGE_PANEL = r"C:\Users\marlo\proyecto_peliculas\posters\Foto_image_izquierda.png"

# Configuración de interfaz
GRID_COLUMNS = 6
GRID_ROWS = 4
PAGE_SIZE = GRID_COLUMNS * GRID_ROWS  # 24 miniaturas por página
THUMB_W, THUMB_H = 235, 250          # tamaño de miniaturas


# Colores principales (tema morado)
BG_COLOR = "#2d0f4b"       # fondo general
PANEL_COLOR = "#3b236b"    # panel lateral
BANNER_COLOR = "#472e7a"   # banner superior
BTN_COLOR = "#6148a6"      # botones
