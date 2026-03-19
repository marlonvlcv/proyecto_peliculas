# Importar librerias
import json
from pathlib import Path
from datetime import datetime

# Importar confirguacion y textos 
from config_cineseven import (USUARIOS_PATH, FAVORITOS_PATH)
from Textos_Cineseven import TEXTOS_LOGIN


class Usuario:
    def __init__(self, idioma="es"):
        self.id = None
        self.nombre = None
        self.apellido = None
        self.nombre_app = None
        self.email = None
        self.password = None
        self.favoritos = []
        self.idioma = idioma

        # Utilidades para leer o escribir en archivos json
    def _load_json(self, path):
        # Si el archivo no existe, devuelve una lista vacia
        if not Path(path).exists():
            return []
        # Abre el archivo y carga su contenido, si hay error devuelve lista vacia
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []

    def _save_json(self, path, data):
        # Guarda datos en formato json en la ruta indicada
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Registrar usuario nuevo
    def registrar(self, nombre, email, password, apellido="", nombre_app="CineSeven"):
        usuarios = self._load_json(USUARIOS_PATH)
        # Verifica si el correo ya esta registrado
        if any(u["email"] == email for u in usuarios):
            return False, "⚠️ El correo ya está registrado."

        # Genera un nuevo ID automático
        nuevo_id = max((u["id"] for u in usuarios), default=0) + 1
        nuevo = {
            "id": nuevo_id,
            "nombre": nombre,
            "apellido": apellido,
            "nombre_app": nombre_app,
            "email": email,
            "password": password
        }
        usuarios.append(nuevo)
        # Guarda el nuevo usuario en el archivo JSON
        self._save_json(USUARIOS_PATH, usuarios)
        return True, TEXTOS_LOGIN[self.idioma]["registro_ok"]

    # Iniciar sesión con correo y contraseña
    def login(self, email, password):
        usuarios = self._load_json(USUARIOS_PATH)
        # Busca si el usuario existe con esos datos
        user = next((u for u in usuarios if u["email"] == email and u["password"] == password), None)
        if not user:
            return False, "⚠️ Usuario o contraseña incorrectos."

        # Si existe, guarda los datos en el objeto actual
        self.id = user["id"]
        self.nombre = user["nombre"]
        self.apellido = user["apellido"]
        self.nombre_app = user["nombre_app"]
        self.email = user["email"]
        self.password = user["password"]

        # Carga los favoritos del usuario
        self.cargar()
        return True, ""

    # Cargar la lista de favoritos del usuario
    def cargar(self):
        todos = self._load_json(FAVORITOS_PATH)

        # Limpia registros vacíos o incorrectos
        limpios = []
        for f in todos:
            if isinstance(f, dict) and "user_id" in f and f["user_id"] is not None:
                limpios.append(f)
        if len(limpios) != len(todos):
            # Si había errores, guarda solo los válidos
            self._save_json(FAVORITOS_PATH, limpios)

        # Carga solo los favoritos del usuario actual
        self.favoritos = [f for f in limpios if str(f.get("user_id")) == str(self.id)]

    # Guarda la lista actualizada de favoritos del usuario
    def guardar(self):
        todos = self._load_json(FAVORITOS_PATH)
        # Elimina los favoritos anteriores del usuario
        todos = [f for f in todos if f.get("user_id") != self.id]
        # Agrega los nuevos favoritos
        todos.extend(self.favoritos)
        self._save_json(FAVORITOS_PATH, todos)

    # Agregar una película a favoritos
    def agregar(self, pelicula):
        todos = self._load_json(FAVORITOS_PATH)
        # Verifica si ya existe esa película en favoritos
        if any(f.get("user_id") == self.id and f.get("title") == pelicula.title for f in todos):
            return False  # ya está agregada

        # Genera un ID único para el nuevo favorito
        nuevo_id = 1
        if todos:
            ids = [f.get("id", 0) for f in todos if isinstance(f, dict)]
            nuevo_id = max(ids, default=0) + 1

        # Convierte la película en diccionario y agrega información adicional
        entry = pelicula.to_dict()
        entry.update({
            "id": nuevo_id,
            "user_id": self.id,
            "added_at": datetime.now().isoformat()
        })
        todos.append(entry)

        # Guarda la lista actualizada
        self._save_json(FAVORITOS_PATH, todos)
        self.cargar()
        return True

    # Eliminar una película de favoritos
    def eliminar(self, titulo):
        todos = self._load_json(FAVORITOS_PATH)
        antes = len(todos)
        # Filtra las películas y elimina la que coincida con el título
        todos = [f for f in todos if not (f["user_id"] == self.id and f["title"] == titulo)]
        if len(todos) < antes:
            # Si se eliminó, guarda y recarga los favoritos
            self._save_json(FAVORITOS_PATH, todos)
            self.cargar()
            return True
        return False
