# Importar librerias
import difflib
import pandas as pd

# Importar Funciones utiles
from utils_cineseven import normalizar_texto

# Importar la clase Pelicula
from pelicula import Pelicula

class CatalogoPeliculas:
    def __init__(self, csv_path, idioma="es"):
        # Carga el idioma 
        self.idioma = idioma
        df = pd.read_csv(csv_path).fillna("")
        self.df = df
        self.peliculas = [self._crear_pelicula(row) for _, row in df.iterrows()]

    def _crear_pelicula(self, row):
        data = row.to_dict()

        # El csv contiene columnas en ambos idiomas
        if self.idioma == "es":
            data["title"] = data.get("title_es", data.get("title", ""))
            data["overview"] = data.get("overview_es", data.get("overview", ""))
        else:
            data["title"] = data.get("title", "")
            data["overview"] = data.get("overview", "")

        return Pelicula(data)

    def set_idioma(self, idioma):
        self.idioma = idioma
        self.peliculas = [self._crear_pelicula(row) for _, row in self.df.iterrows()]

    # Filtros
    def filter_and_sort(self, search_text="", ordenar="Más populares", filtros=None):
        filtros = filtros or {}
        resultados = self.peliculas

        st = normalizar_texto(search_text or "")
        if st:
            matches = []

            # campos a considerar para búsqueda "general"
            for p in resultados:
                title_norm    = normalizar_texto(p.title)
                orig_norm     = normalizar_texto(p.original_title)
                overview_norm = normalizar_texto(p.overview)
                genres_norm   = normalizar_texto(p.genres)
                director_norm = normalizar_texto(p.director)
                cast_norm     = normalizar_texto(p.cast)
                keywords_norm = normalizar_texto(p.keywords)

                # coincidencia parcial simple en varios campos
                if (st in title_norm
                    or st in orig_norm
                    or st in overview_norm
                    or st in genres_norm
                    or st in director_norm
                    or st in cast_norm
                    or st in keywords_norm):
                    matches.append(p)

            # Si no hay matches directos, intentamos coincidencia difusa por título/original
            if not matches:
                UM_BRAL = 0.72  # umbral de similitud 
                for p in resultados:
                    title_norm = normalizar_texto(p.title)
                    orig_norm  = normalizar_texto(p.original_title)
                    r1 = difflib.SequenceMatcher(None, st, title_norm).ratio() if title_norm else 0
                    r2 = difflib.SequenceMatcher(None, st, orig_norm).ratio() if orig_norm else 0
                    if max(r1, r2) >= UM_BRAL:
                        matches.append(p)

            resultados = matches
        # Si no hay texto de búsqueda, se mantienen todas las películas filtradas

        # FILTROS AVANZADOS
        if filtros.get("genre"):
            g = normalizar_texto(filtros["genre"])
            resultados = [p for p in resultados if g in normalizar_texto(p.genres)]

        if filtros.get("director"):
            d = normalizar_texto(filtros["director"])
            resultados = [p for p in resultados if d in normalizar_texto(p.director)]

        if filtros.get("actor"):
            a = normalizar_texto(filtros["actor"])
            resultados = [p for p in resultados if a in normalizar_texto(p.cast)]

        # Filtro por año
        year_mode = filtros.get("year_mode", "ninguno")
        if year_mode == "exacto" and filtros.get("exact_year"):
            try:
                y = int(filtros["exact_year"])
                resultados = [p for p in resultados if p.release_year_int() == y]
            except Exception:
                pass
        elif year_mode == "rango" and filtros.get("year_range"):
            y1, y2 = filtros["year_range"]
            try:
                y1, y2 = int(y1), int(y2)
                resultados = [p for p in resultados if y1 <= p.release_year_int() <= y2]
            except Exception:
                pass

        # Filtro por calificación mínima
        if filtros.get("min_rating") is not None and filtros.get("min_rating") > 0:
            resultados = [p for p in resultados if p.vote_average >= filtros["min_rating"]]

        # Filtro por popularidad mínima
        if filtros.get("min_popularity"):
            niveles = ["Baja", "Media", "Alta", "Muy Alta"]
            nivel_sel = filtros["min_popularity"]
            if nivel_sel in niveles:
                idx_sel = niveles.index(nivel_sel)
                resultados = [
                    p for p in resultados if p.popularidad_nivel in niveles and niveles.index(p.popularidad_nivel) >= idx_sel
                ]

        # ORDENAR POR
        ordenar_norm = normalizar_texto(ordenar)

        if ordenar_norm in ["más populares", "mas populares", "most popular"]:
            resultados = sorted(resultados, key=lambda p: p.popularity, reverse=True)
        elif ordenar_norm in ["menos populares", "least popular"]:
            resultados = sorted(resultados, key=lambda p: p.popularity)
        elif ordenar_norm in ["mayor calificación", "mayor calificacion", "highest rating"]:
            resultados = sorted(resultados, key=lambda p: float(p.vote_average or 0), reverse=True)
        elif ordenar_norm in ["menor calificación", "menor calificacion", "lowest rating"]:
            resultados = sorted(resultados, key=lambda p: float(p.vote_average or 0))
        elif ordenar_norm in ["más nuevas", "mas nuevas", "newest"]:
            resultados = sorted(resultados, key=lambda p: p.release_year_int(), reverse=True)
        elif ordenar_norm in ["más antiguas", "mas antiguas", "oldest"]:
            resultados = sorted(resultados, key=lambda p: p.release_year_int())

        return resultados
