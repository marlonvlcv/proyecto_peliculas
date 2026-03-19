class Pelicula:
    def __init__(self, data: dict):
        # Campos del CSV todos los 16 campos principales 
        self.title = str(data.get("title", "")).strip()
        self.original_title = str(data.get("original_title", "")).strip()
        self.overview = str(data.get("overview", "")).strip()
        self.genres = str(data.get("genres", "")).strip()
        self.release_year = str(data.get("release_year", "")).strip()
        self.director = str(data.get("director", "")).strip()
        self.cast = str(data.get("main_cast", "")).strip()
        self.keywords = str(data.get("keywords", "")).strip()
        self.poster_path = str(data.get("poster_path", "")).strip()
        self.popularity_scaled = str(data.get("popularity_scaled", "")).strip()
        self.popularidad_nivel = str(data.get("popularidad_nivel", "")).strip()
        self.title_es = str(data.get("title_es", "")).strip()
        self.overview_es = str(data.get("overview_es", "")).strip()

        # Campos numéricos, con validaciones por si hay errores de formato
        try:
            val = str(data.get("vote_average", "0")).replace(",", ".").strip()
            self.vote_average = float(val) if val else 0.0
        except:
            self.vote_average = 0.0

        try:
            self.vote_count = int(data.get("vote_count", 0) or 0)
        except:
            self.vote_count = 0

        try:
            self.popularity = float(data.get("popularity", 0) or 0)
        except:
            self.popularity = 0.0

        # Fecha o momento en que se agrego a favoritos 
        self.added_at = data.get("added_at", None)

    # Convierte el objeto Pelicula en un diccionario, util para guardar en json
    def to_dict(self):
        return {
            "title": self.title,
            "original_title": self.original_title,
            "overview": self.overview,
            "genres": self.genres,
            "release_year": self.release_year,
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "popularity": self.popularity,
            "director": self.director,
            "main_cast": self.cast,
            "keywords": self.keywords,
            "poster_path": self.poster_path,
            "popularity_scaled": self.popularity_scaled,
            "popularidad_nivel": self.popularidad_nivel,
            "title_es": self.title_es,
            "overview_es": self.overview_es,
            "added_at": self.added_at,
        }

    # Devuelve el año de estreno como número entero 
    def release_year_int(self):
        try:
            return int(self.release_year)
        except:
            return 0
