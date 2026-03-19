# Importar librerias 
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Importar Confifuraciones
from config_cineseven import (
    CSV_PATH, IMAGES_BASE_PATH, USUARIOS_PATH, FAVORITOS_PATH, IMAGE_PANEL,
    GRID_COLUMNS, GRID_ROWS, PAGE_SIZE, THUMB_W, THUMB_H,
    BG_COLOR, PANEL_COLOR, BANNER_COLOR, BTN_COLOR
)

# Importa textos
from Textos_Cineseven import (TEXTOS, TEXTOS_GENEROS)

# Importar funciones utiles
from utils_cineseven import (normalizar_texto, cargar_thumbnail)

# Importar clases
from pelicula import Pelicula
from usuario import Usuario


class AppPeliculasGUI:
    def __init__(self,root, catalogo, idioma="es"):
        # configuración inicial
        self.catalogo = catalogo    
        self.idioma = idioma
        self.usuario = None
        self.root = root
        self.root.title("🎥 CineSeven")
        self.root.geometry("1280x900")
        self.root.configure(bg=BG_COLOR)

        # estilos ttk 
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=BG_COLOR, foreground="white")
        style.configure("TButton", background=BTN_COLOR, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#7b59c6")])
        style.configure("TFrame", background=BG_COLOR)

        # variables principales de la app
        self.idioma_actual = idioma  
        self.usuario = Usuario()
        self.search_var = tk.StringVar()
        self.ordenar_var = tk.StringVar(value=self.t("mas_populares"))
        self._thumb_cache = {}
        self.filtros_avanzados = {}
        self.offset = 0  # para paginación 

        # construir interfaz y mostrar catálogo inicial
        self._build_ui()
        self.mostrar_catalogo(reset_offset=True)
    # traducir una clave según el idioma actual
    def t(self, clave):
        return TEXTOS.get(self.idioma_actual, TEXTOS["es"]).get(clave, clave)
    
    # construir toda la interfaz gráfica
    def _build_ui(self):
        banner = tk.Frame(self.root, bg=BANNER_COLOR, height=90)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        self.logo_lbl = tk.Label(banner, bg=BANNER_COLOR)
        self.logo_lbl.pack(side="left", padx=16, pady=8)
        tk.Label(
            banner, text=self.t("catalogo_nombre"),
            bg=BANNER_COLOR, fg="white",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=12)

        # contenedor principal
        main = tk.Frame(self.root, bg=BG_COLOR)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # PANEL IZQUIERDO
        panel_left = tk.Frame(main, bg=PANEL_COLOR, width=340)
        panel_left.pack(side="left", fill="y", padx=(0,10))
        panel_left.pack_propagate(False)

        # campo de búsqueda
        pad = dict(padx=10, pady=8)
        self.lbl_search = tk.Label(
            panel_left, text=self.t("buscar_pelicula"),
            bg=PANEL_COLOR, fg="white", anchor="w"
        )
        self.lbl_search.pack(fill="x", **pad)

        entry = ttk.Entry(panel_left, textvariable=self.search_var)
        entry.pack(fill="x", padx=10)
        entry.bind("<Return>", lambda e: self._on_search_enter())

        # botón para abrir búsqueda avanzada
        self.btn_advanced = ttk.Button(
            panel_left, text=self.t("busqueda_avanzada"),
            command=self.abrir_busqueda_avanzada
        )
        self.btn_advanced.pack(fill="x", padx=10, pady=(12,6))

        # sección de ordenamiento
        self.lbl_order = tk.Label(
            panel_left, text=self.t("ordenar_por"),
            bg=PANEL_COLOR, fg="white", anchor="w"
        )
        self.lbl_order.pack(fill="x", **pad)

        
        # claves internas del orden
        self.opciones_orden = [
            "mas_populares",
            "menos_populares",
            "mayor_calificacion",
            "menor_calificacion",
            "mas_nuevas",
            "mas_antiguas",
        ]

        # Combobox mostrando traducciones
        self.cmb_order = ttk.Combobox(
            panel_left,
            textvariable=self.ordenar_var,
            values=[self.t(op) for op in self.opciones_orden],
            state="readonly"
        )
        self.cmb_order.pack(fill="x", padx=10)
        self.cmb_order.bind("<<ComboboxSelected>>", lambda e: self._on_order_change())

        # botones para buscar y ver favoritos
        self.btn_search = ttk.Button(
            panel_left, text=self.t("buscar_pelicula"),
            command=lambda: self.mostrar_catalogo(reset_offset=True)
        )
        self.btn_search.pack(fill="x", padx=10, pady=(10,6))

        self.btn_favs = ttk.Button(
            panel_left, text=self.t("ver_favoritos"),
            command=self.abrir_ventana_favoritos
        )
        self.btn_favs.pack(fill="x", padx=10, pady=(0,6))

        self.lbl_info = tk.Label(
            panel_left, text="", bg=PANEL_COLOR,
            fg="white", justify="left"
        )
        self.lbl_info.pack(fill="x", padx=10, pady=(4,2))

        # zona principal derecha (catálogo de películas)
        right_container = tk.Frame(main, bg=BG_COLOR)
        right_container.pack(side="right", fill="both", expand=True)

        header = tk.Frame(right_container, bg=BG_COLOR)
        header.pack(fill="x")
        self.lbl_results = tk.Label(
            header, text="", bg=BG_COLOR,
            fg="white", font=("Segoe UI", 11)
        )
        self.lbl_results.pack(side="left", padx=8, pady=6)

        # canvas + scroll vertical y horizontal 
        canvas = tk.Canvas(right_container, bg=BG_COLOR, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(right_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(right_container, orient="horizontal", command=canvas.xview)

        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # frame interno donde se muestran las películas
        self.grid_frame = tk.Frame(canvas, bg=BG_COLOR)
        canvas.create_window((0,0), window=self.grid_frame, anchor="nw")

        # ajustar el área del scroll dinámicamente
        self.grid_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # navegación entre páginas de resultados
        tk.Label(
            panel_left, text=self.t("nav_label"),
            bg=PANEL_COLOR, fg="white", anchor="w"
        ).pack(fill="x", padx=10, pady=(0, 0))

        nav_frame = tk.Frame(panel_left, bg=PANEL_COLOR)
        nav_frame.pack(fill="x", padx=10, pady=(0, 0))

        self.btn_prev = ttk.Button(
            nav_frame, text=self.t("mostrar_menos"),
            command=self.mostrar_anterior_peliculas
        )
        self.btn_prev.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_next = ttk.Button(
            nav_frame, text=self.t("mostrar_mas"),
            command=self.mostrar_mas
        )
        self.btn_next.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Imagen lateral
        try:
            img_path = IMAGE_PANEL
            img = Image.open(img_path)
            img = img.resize((315, 510))
            self.panel_image = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(panel_left, image=self.panel_image, bg=PANEL_COLOR)
            lbl_img.pack(pady=(6, 0))
        except Exception as e:
            print(f"⚠️ No se pudo cargar la imagen: {e}")

    # ventana emergente con filtros de búsqueda avanzada
    def abrir_busqueda_avanzada(self):
        # configuración general del toplevel
        top = tk.Toplevel(self.root)
        top.title(self.t("busqueda_avanzada_titulo"))
        top.geometry("420x420")
        top.configure(bg=PANEL_COLOR)

        # definición de filtros y opciones
        filtros = {}
        genres_map = TEXTOS_GENEROS[self.idioma_actual]

        # Lista de géneros mostrados según idioma actual
        genres_display = sorted(genres_map.values())

        def aplicar():
            # Traduce el género seleccionado al inglés antes de filtrar
            selected_genre = genre_var.get().strip()
            genre_en = ""
            for k, v in TEXTOS_GENEROS[self.idioma_actual].items():
                if selected_genre == v:
                    genre_en = k
                    break

            year_value = year_exact_var.get()
            if year_value > 0:
                filtros["exact_year"] = int(year_value)
            else:
                filtros["exact_year"] = None

            filtros["genre"] = genre_en
            filtros["director"] = director_var.get().strip()
            filtros["actor"] = actor_var.get().strip()
            filtros["year_mode"] = year_mode_var.get()
            filtros["year_range"] = (year_min_var.get(), year_max_var.get())
            filtros["min_rating"] = rating_var.get()
            filtros["min_popularity"] = pop_var.get()
            self.filtros_avanzados = filtros
            top.destroy()
            self.mostrar_catalogo(reset_offset=True)

        pad = dict(padx=10, pady=8)

        # Género 
        tk.Label(top, text=self.t("genero"), bg=PANEL_COLOR, fg="white").pack(anchor="w", **pad)
        genre_var = tk.StringVar()
        cmb_genres = ttk.Combobox(top, textvariable=genre_var, values=genres_display, state="readonly")
        cmb_genres.pack(fill="x", padx=10)

        # Director
        tk.Label(top, text=self.t("director"), bg=PANEL_COLOR, fg="white").pack(anchor="w", **pad)
        director_var = tk.StringVar()
        ttk.Entry(top, textvariable=director_var).pack(fill="x", padx=10)

        # Actor
        tk.Label(top, text=self.t("actor"), bg=PANEL_COLOR, fg="white").pack(anchor="w", **pad)
        actor_var = tk.StringVar()
        ttk.Entry(top, textvariable=actor_var).pack(fill="x", padx=10)

        # Filtro de año
        tk.Label(top, text=self.t("filtro_anio"), bg=PANEL_COLOR, fg="white").pack(anchor="w", **pad)
        year_mode_var = tk.StringVar(value="ninguno")

        frm_year = tk.Frame(top, bg=PANEL_COLOR)
        frm_year.pack(fill="x", padx=10)
        ttk.Radiobutton(frm_year, text=self.t("ninguno"), variable=year_mode_var, value="ninguno").pack(side="left")
        ttk.Radiobutton(frm_year, text=self.t("exacto"), variable=year_mode_var, value="exacto").pack(side="left")
        ttk.Radiobutton(frm_year, text=self.t("rango"), variable=year_mode_var, value="rango").pack(side="left")

        year_exact_var = tk.IntVar(value=0)
        year_exact_entry = ttk.Entry(top, textvariable=year_exact_var)
        year_exact_entry.pack(fill="x", padx=10, pady=(6,0))

        year_range_frame = tk.Frame(top, bg=PANEL_COLOR)
        year_min_var = tk.IntVar(value=1900)
        year_max_var = tk.IntVar(value=datetime.now().year)
        tk.Label(year_range_frame, text=self.t("desde"), bg=PANEL_COLOR, fg="white").pack(side="left", padx=(0,6))
        ttk.Entry(year_range_frame, textvariable=year_min_var, width=6).pack(side="left")
        tk.Label(year_range_frame, text=self.t("hasta"), bg=PANEL_COLOR, fg="white").pack(side="left", padx=(10,6))
        ttk.Entry(year_range_frame, textvariable=year_max_var, width=6).pack(side="left")
        year_range_frame.pack(fill="x", padx=10, pady=(6,0))

        def actualizar_year_widgets(*_):
            mode = year_mode_var.get()
            if mode == "ninguno":
                year_exact_entry.pack_forget()
                year_range_frame.pack_forget()
            elif mode == "exacto":
                year_range_frame.pack_forget()
                year_exact_entry.pack(fill="x", padx=10, pady=(6,0))
            else:
                year_exact_entry.pack_forget()
                year_range_frame.pack(fill="x", padx=10, pady=(6,0))

        year_mode_var.trace_add("write", actualizar_year_widgets)
        actualizar_year_widgets()

        # Calificación mínima
        tk.Label(top, text=self.t("calificacion_minima"), bg=PANEL_COLOR, fg="white").pack(anchor="w", padx=10, pady=(8,0))
        rating_var = tk.DoubleVar(value=0.0)
        ttk.Entry(top, textvariable=rating_var).pack(fill="x", padx=10, pady=(0,6))

        # Popularidad mínima
        tk.Label(top, text=self.t("nivel_popularidad_label"), bg=PANEL_COLOR, fg="white").pack(anchor="w", padx=10, pady=(6,0))

        # Valores para mostrar al usuario según idioma
        niveles_pop_mostrar = [
            self.t("pop_baja"),
            self.t("pop_media"),
            self.t("pop_alta"),
            self.t("pop_muy_alta")
        ]

        pop_var = tk.StringVar(value="")  
        combo_pop = ttk.Combobox(top, textvariable=pop_var, values=niveles_pop_mostrar, state="readonly")
        combo_pop.set("")  # deja el campo en blanco al abrir la ventana
        combo_pop.pack(fill="x", padx=10, pady=(0,6))
        ttk.Button(top, text=self.t("aplicar_filtros"), command=aplicar).pack(pady=12)

    # Buscar / ordenar / paginar
    def _on_search_enter(self):
        self.offset = 0
        self.mostrar_catalogo(reset_offset=True)

    def _on_order_change(self):
        self.offset = 0
        self.mostrar_catalogo(reset_offset=True)

    def mostrar_catalogo(self, reset_offset=False):
        if reset_offset:
            self.offset = 0

        # limpiar grid
        for c in self.grid_frame.winfo_children():
            c.destroy()

        resultados = self.catalogo.filter_and_sort(
            search_text=self.search_var.get(),
            ordenar=self.ordenar_var.get(),
            filtros=self.filtros_avanzados
        )

        total = len(resultados)
        start = self.offset
        end = min(start + PAGE_SIZE, total)
        mostrar = resultados[start:end]

        # crear grid 
        for idx, peli in enumerate(mostrar):
            fila, col = divmod(idx, GRID_COLUMNS)
            frame = tk.Frame(self.grid_frame, bg=BG_COLOR, padx=6, pady=6)
            frame.grid(row=fila, column=col, padx=8, pady=8)

            ruta = peli.poster_path
            if ruta not in self._thumb_cache:
                self._thumb_cache[ruta] = cargar_thumbnail(ruta)
            imgtk = self._thumb_cache[ruta]

            lbl_img = tk.Label(frame, image=imgtk, cursor="hand2")
            lbl_img.image = imgtk
            lbl_img.pack()
            lbl_img.bind("<Button-1>", lambda e, p=peli: self.abrir_detalle(p))

            lbl_title = tk.Label(frame, text=f"{peli.title}\n({peli.release_year})", bg=BG_COLOR, fg="white", wraplength=THUMB_W, justify="center")
            lbl_title.pack(pady=(6,0))

        # actualizar texto de resultados
        self.lbl_results.config(text=self.t("mostrando").format(start=start+1, end=end, total=total))
        self.usuario.cargar()

    # Funciones de paginación
    def mostrar_mas(self):
        resultados = self.catalogo.filter_and_sort(
            search_text=self.search_var.get(),
            ordenar=self.ordenar_var.get(),
            filtros=self.filtros_avanzados
        )
        total = len(resultados)
        if self.offset + PAGE_SIZE < total:
            self.offset += PAGE_SIZE
            self.mostrar_catalogo(reset_offset=False)
        else:
            messagebox.showinfo(self.t("mostrar_mas"), self.t("no_mas"))


    def mostrar_anterior_peliculas(self):
        if self.offset - PAGE_SIZE >= 0:
            self.offset -= PAGE_SIZE
            self.mostrar_catalogo(reset_offset=False)
        else:
            messagebox.showinfo(self.t("mostrar_menos"), self.t("no_menos"))

    # Ventana detalle
    def abrir_detalle(self, pelicula: Pelicula):
        top = tk.Toplevel(self.root)
        top.title(pelicula.title)
        top.geometry("800x520")
        top.configure(bg=BG_COLOR)

        left = tk.Frame(top, bg=BG_COLOR)
        left.pack(side="left", fill="y", padx=12, pady=12)

        right = tk.Frame(top, bg=BG_COLOR)
        right.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        try:
            ruta_str = str(pelicula.poster_path).replace("\\", "/").strip()

            if ruta_str.lower().startswith("posters/"):
                ruta_str = ruta_str[len("posters/"):]

            ruta_abs = IMAGES_BASE_PATH / ruta_str

            if ruta_abs.exists():
                img = Image.open(ruta_abs).convert("RGB")
            else:
                img = Image.new("RGB", (350, 520), (200, 200, 200))

            img.thumbnail((350, 520), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

        except Exception as e:
            img = Image.new("RGB", (350, 520), (200, 200, 200))
            photo = ImageTk.PhotoImage(img)

        lbl_img = tk.Label(left, image=photo, bg=BG_COLOR)
        lbl_img.image = photo  
        lbl_img.pack(padx=20, pady=20)


        tk.Label(right, text=f"{pelicula.title} ({pelicula.release_year})", bg=BG_COLOR, fg="white", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(right, text=f"{self.t('director_label')} {pelicula.director}", bg=BG_COLOR, fg="white").pack(anchor="w", pady=(6,0))
        tk.Label(right, text=f"{self.t('reparto_label')} {pelicula.cast}", bg=BG_COLOR, fg="white", wraplength=380, justify="left").pack(anchor="w", pady=(6,0))
        tk.Label(right, text=f"{self.t('generos_label')} {pelicula.genres}", bg=BG_COLOR, fg="white").pack(anchor="w", pady=(6,0))

        # Traducir nivel de popularidad
        niveles_es = ["Baja", "Media", "Alta", "Muy Alta"]
        niveles_en = ["Low", "Medium", "High", "Very High"]

        if self.idioma_actual == "en":
            try:
                idx = niveles_es.index(pelicula.popularidad_nivel)
                pop_nivel = niveles_en[idx]
            except:
                pop_nivel = pelicula.popularidad_nivel
        else:
            pop_nivel = pelicula.popularidad_nivel

        # Mostrar calificación + popularidad traducida
        tk.Label(
            right,
            text=f"⭐ {pelicula.vote_average} 🔥 {pop_nivel} ({pelicula.popularity:.1f})",
            bg=BG_COLOR,
            fg="white"
        ).pack(anchor="w", pady=(6,0))


        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=8)

        # Cuadro de sinopsis con scroll
        txt_frame = tk.Frame(right, bg=BG_COLOR)
        txt_frame.pack(fill="both", expand=True)

        scroll_txt = ttk.Scrollbar(txt_frame, orient="vertical")
        txt = tk.Text(txt_frame, wrap="word", height=16, yscrollcommand=scroll_txt.set)
        scroll_txt.config(command=txt.yview)

        txt.insert("1.0", pelicula.overview or self.t("sinopsis_no_disp"))
        txt.config(state="disabled")

        txt.pack(side="left", fill="both", expand=True)
        scroll_txt.pack(side="right", fill="y")


        btn_frame = tk.Frame(right, bg=BG_COLOR)
        btn_frame.pack(fill="x", pady=8)
        ttk.Button(btn_frame, text= self.t("agregar_fav"), command=lambda: self._agregar_fav_from_detail(pelicula)).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=self.t("cerrar"), command=top.destroy).pack(side="right", padx=6)

    # agregar película a favoritos desde la ventana de detalle
    def _agregar_fav_from_detail(self, pelicula):
        if self.usuario.agregar(pelicula):
            self.usuario.cargar()
            self.usuario.guardar()
            messagebox.showinfo(self.t("favoritos_titulo"), self.t("agregado_fav"))
            self.mostrar_catalogo(reset_offset=False)
        else:
            messagebox.showwarning(self.t("favoritos_titulo"), self.t("ya_en_fav"))

    # ventana para mostrar y administrar los favoritos del usuario
    def abrir_ventana_favoritos(self):
        favs = self.usuario.favoritos
        if not favs:
            messagebox.showinfo(self.t("favoritos_titulo"), self.t("sin_favoritos"))
            return

        # configuración de la ventana principal de favoritos
        top = tk.Toplevel(self.root)
        top.title(self.t("favoritos_titulo"))
        top.geometry("1100x750")
        top.configure(bg=BG_COLOR)

        # variables de búsqueda, orden y paginación
        search_var = tk.StringVar()
        ordenar_var = tk.StringVar(value=self.t("fecha_agregado"))
        offset = 0
        GRID_COLUMNS = 8
        PAGE_SIZE = GRID_COLUMNS * 2  # 16 por página

        # encabezado con buscador y opciones de orden
        header = tk.Frame(top, bg=BG_COLOR)
        header.pack(fill="x", pady=(10, 4))

        tk.Label(header, text=self.t("buscar_en_favoritos"), bg=BG_COLOR, fg="white").pack(side="left", padx=(10, 4))
        entry_search = ttk.Entry(header, textvariable=search_var, width=30)
        entry_search.pack(side="left", padx=(0, 10))

        tk.Label(header, text=self.t("ordenar_favoritos"), bg=BG_COLOR, fg="white").pack(side="left", padx=(10, 4))
        opciones_orden = [
            self.t("titulo_az"),
            self.t("anio"),
            self.t("popularidad"),
            self.t("genero"),
            self.t("fecha_agregado"),
        ]
        combo_orden = ttk.Combobox(header, textvariable=ordenar_var, values=opciones_orden, state="readonly", width=18)
        combo_orden.pack(side="left", padx=(0, 10))

        ttk.Button(header, text=self.t("buscar_pelicula"), command=lambda: refrescar(True)).pack(side="left", padx=(5, 0))

        # contenedor principal con canvas y scroll horizontal
        contenedor = tk.Frame(top, bg=BG_COLOR)
        contenedor.pack(fill="both", expand=True, padx=12, pady=12)

        canvas = tk.Canvas(contenedor, bg=BG_COLOR, highlightthickness=0)
        canvas.pack(side="top", fill="both", expand=True)

        scroll_x = tk.Scrollbar(contenedor, orient="horizontal", command=canvas.xview)
        scroll_x.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=scroll_x.set)

        frame = tk.Frame(canvas, bg=BG_COLOR)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame.bind("<Configure>", actualizar_scroll)

        nav_frame = tk.Frame(top, bg=BG_COLOR)
        nav_frame.pack(fill="x", pady=(10, 6))
        thumb_cache = {}

        # aplica búsqueda y orden sobre los favoritos
        def aplicar_filtros_y_orden():
            resultados = [Pelicula(item) for item in favs]
            texto = search_var.get().strip().lower()
            if texto:
                resultados = [
                    p for p in resultados
                    if texto in p.title.lower() or texto in p.director.lower() or texto in p.genres.lower()
                ]

            orden_sel = ordenar_var.get()
            if orden_sel == self.t("titulo_az"):
                resultados.sort(key=lambda p: p.title)
            elif orden_sel == self.t("anio"):
                resultados.sort(key=lambda p: p.release_year_int(), reverse=True)
            elif orden_sel == self.t("popularidad"):
                resultados.sort(key=lambda p: p.popularity, reverse=True)
            elif orden_sel == self.t("genero"):
                resultados.sort(key=lambda p: p.genres)
            elif orden_sel == self.t("fecha_agregado"):
                resultados.sort(key=lambda p: p.to_dict().get("added_at", ""), reverse=True)

            return resultados

        # refresca la cuadrícula de favoritos mostrados
        def refrescar(reset_offset=False):
            nonlocal offset
            if reset_offset:
                offset = 0
            for c in frame.winfo_children():
                c.destroy()

            resultados = aplicar_filtros_y_orden()
            total = len(resultados)
            start = offset
            end = min(start + PAGE_SIZE, total)
            mostrar = resultados[start:end]

            for idx, peli in enumerate(mostrar):
                fila, col = divmod(idx, GRID_COLUMNS)
                tarjeta = tk.Frame(frame, bg=BG_COLOR, padx=6, pady=6)
                tarjeta.grid(row=fila, column=col, padx=8, pady=8)

                if peli.poster_path not in thumb_cache:
                    thumb_cache[peli.poster_path] = cargar_thumbnail(peli.poster_path)
                imgtk = thumb_cache[peli.poster_path]

                lbl_img = tk.Label(tarjeta, image=imgtk, bg=BG_COLOR, cursor="hand2")
                lbl_img.image = imgtk
                lbl_img.pack()
                lbl_img.bind("<Button-1>", lambda e, p=peli: self.abrir_detalle(p))

                tk.Label(
                    tarjeta,
                    text=f"{peli.title}\n({peli.release_year})",
                    bg=BG_COLOR,
                    fg="white",
                    wraplength=THUMB_W,
                    justify="center"
                ).pack(pady=4)

                ttk.Button(
                    tarjeta,
                    text=self.t("eliminar"),
                    command=lambda p=peli: eliminar_fav(p)
                ).pack(pady=(2, 6))

            # botones de navegación inferior
            for widget in nav_frame.winfo_children():
                widget.destroy()

            ttk.Button(nav_frame, text=self.t("mostrar_menos"), command=lambda: anterior()).pack(side="left", padx=10)
            lbl_estado = tk.Label(
                nav_frame,
                text=self.t("mostrando_favs").format(start=start+1, end=end, total=total),
                bg=BG_COLOR, fg="white"
            )
            lbl_estado.pack(side="left", expand=True)
            ttk.Button(nav_frame, text=self.t("mostrar_mas"), command=lambda: siguiente()).pack(side="right", padx=10)

        # navegación entre páginas
        def siguiente():
            nonlocal offset
            resultados = aplicar_filtros_y_orden()
            if offset + PAGE_SIZE < len(resultados):
                offset += PAGE_SIZE
                refrescar()
            else:
                messagebox.showinfo(self.t("favoritos_titulo"), self.t("no_mas"))

        def anterior():
            nonlocal offset
            if offset - PAGE_SIZE >= 0:
                offset -= PAGE_SIZE
                refrescar()
            else:
                messagebox.showinfo(self.t("favoritos_titulo"), self.t("no_menos"))

        # elimina un favorito y actualiza la vista
        def eliminar_fav(peli: Pelicula):
            if messagebox.askyesno(self.t("favoritos_titulo"),
                                   self.t("confirmar_eliminar_fav").format(titulo=peli.title)):
                if self.usuario.eliminar(peli.title):
                    messagebox.showinfo(self.t("favoritos_titulo"),
                                        self.t("favoritos_eliminado").format(titulo=peli.title))
                    refrescar(True)
                else:
                    messagebox.showwarning(self.t("favoritos_titulo"),
                                            self.t("favoritos_no_puede_eliminar"))

        refrescar(True)
        ttk.Button(top, text=self.t("cerrar"), command=top.destroy).pack(pady=8)

    def cambiar_idioma(self, nuevo_idioma):
        if nuevo_idioma not in ("es", "en"):
            return
        self.catalogo.set_idioma(nuevo_idioma)
        self.idioma_actual = nuevo_idioma

        # filtrar usando normalizar_texto para coherencia
        texto = self.search_var.get().strip()
        if texto:
            st = normalizar_texto(texto)
            todas = self.catalogo.peliculas
            resultados = [
                p for p in todas
                if st in normalizar_texto(p.title) or st in normalizar_texto(p.original_title)
            ]
            # sustituimos la lista de películas por los resultados
            self.catalogo.peliculas = resultados

        self.mostrar_catalogo(reset_offset=True)
        idioma_texto = "Español" if nuevo_idioma == "es" else "Inglés"
        messagebox.showinfo(self.t("idioma_titulo"), self.t("idioma_cambiado"))
        self.refrescar_textos()
        
    def refrescar_textos(self):
        self.root.title(self.t("catalogo_nombre"))

        try:
            self.lbl_search.config(text=self.t("buscar_pelicula"))
            self.btn_advanced.config(text=self.t("busqueda_avanzada"))
            self.lbl_order.config(text=self.t("ordenar_por"))

            # actualizar combobox SOLO con traducciones
            traducciones = [self.t(op) for op in self.opciones_orden]
            self.cmb_order.config(values=traducciones)

            try:
                actual = self.ordenar_var.get()
                if actual not in traducciones:
                    self.ordenar_var.set(traducciones[0])
            except:
                pass

            self.btn_search.config(text=self.t("buscar_pelicula"))
            self.btn_favs.config(text=self.t("ver_favoritos"))
            self.btn_prev.config(text=self.t("mostrar_menos"))
            self.btn_next.config(text=self.t("mostrar_mas"))
        except:
            pass

        # Refrescar labels
        def _rec_update(parent):
            for w in parent.winfo_children():
                try:
                    text = w.cget("text")
                except Exception:
                    text = None
                if text:
                    for clave, val in TEXTOS[self.idioma_actual].items():
                        if text == TEXTOS.get("es", {}).get(clave) or text == TEXTOS.get("en", {}).get(clave):
                            w.config(text=self.t(clave))
                            break
                _rec_update(w)
        _rec_update(self.root)
