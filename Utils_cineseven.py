# Importar librerias
from pathlib import Path
import unicodedata
import re
from PIL import Image, ImageTk

# Importar configuraciones
from config_cineseven import (IMAGES_BASE_PATH, THUMB_W, THUMB_H)

# limpia y estandariza texto (quita acentos, espacios y mayúsculas)
def normalizar_texto(texto):
    if texto is None:
        return ""
    if not isinstance(texto, str):
        texto = str(texto)
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


# valida que el correo tenga una estructura correcta 
def validar_email(email: str) -> bool:
    patron = r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]{2,}$"
    return re.match(patron, email) is not None


# comprueba que la contraseña cumpla con requisitos de seguridad
def validar_password(pw: str) -> bool:
    if len(pw) < 6:
        return False
    if not re.search(r"[A-Z]", pw):   # al menos una mayúscula
        return False
    if not re.search(r"[a-z]", pw):   # al menos una minúscula
        return False
    if not re.search(r"[0-9]", pw):   # al menos un número
        return False
    return True


# carga miniatura de la película o un cuadro gris si no existe
def cargar_thumbnail(ruta, w=THUMB_W, h=THUMB_H, debug=False):
    try:
        if ruta is None:
            ruta = ""
        ruta_str = str(ruta).strip()

        # limpia caracteres extraños o emojis
        ruta_str = ruta_str.replace("🖼️", "").replace('"', "").replace("'", "").strip()

        # si la ruta esta vacia muestra un cuadro gris
        if ruta_str == "":
            if debug:
                print("cargar_thumbnail: ruta vacía → cuadro gris")
            img = Image.new("RGB", (w, h), (190, 190, 190))
            return ImageTk.PhotoImage(img)

        # normaliza las barras en la ruta
        ruta_str = ruta_str.replace("\\", "/")

        # construye la ruta absoluta correcta
        ruta_abs = Path(ruta_str)
        if not ruta_abs.is_absolute():
            if ruta_str.lower().startswith("posters/"):
                ruta_rel = ruta_str[len("posters/"):]
            else:
                ruta_rel = ruta_str
            ruta_abs = IMAGES_BASE_PATH / ruta_rel

        # si el archivo existe, carga la imagen y genera el thumbnail
        if ruta_abs.exists() and ruta_abs.is_file():
            img = Image.open(ruta_abs).convert("RGB")
            img.thumbnail((w, h), Image.LANCZOS)
            return ImageTk.PhotoImage(img)

        # si no existe muestra un cuadro gris
        img = Image.new("RGB", (w, h), (190, 190, 190))
        return ImageTk.PhotoImage(img)

    except Exception as e:
        # si hay error  muestra un cuadro gris
        img = Image.new("RGB", (w, h), (190, 190, 190))
        return ImageTk.PhotoImage(img)

