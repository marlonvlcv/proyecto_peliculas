# CineSeven / Proyecto

# importar librerias
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# importar configuraciones
from config_cineseven import (CSV_PATH)

# importar textos
from Textos_Cineseven import TEXTOS_LOGIN, ETIQUETAS_REGISTRO

# importar funciones utiles
from utils_cineseven import (validar_email, validar_password)

# importar clases 
from catalogo import CatalogoPeliculas
from usuario import Usuario
from app_peliculas_gui import AppPeliculasGUI


# Funcion para inicializar la interfaz en el idioma preferido del usuario.
def seleccionar_idioma_inicial():
    win = tk.Tk()
    win.title("🎥 CineSeven APP")
    win.geometry("600x400")
    win.configure(bg="#3b236b")
    win.resizable(False, False)

    # Centrar la ventana en pantalla
    win.update_idletasks()
    w, h = 600, 500
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 3
    win.geometry(f"{w}x{h}+{x}+{y}")

    # Título principal
    tk.Label(
        win,
        text="Bienevenido a / Welcome to\n🎥 CineSeven 🎞️\n🎬",
        bg="#3b236b",
        fg="white",
        font=("Segoe UI", 24, "bold")
    ).pack(pady=(50, 20))

    # Subtítulo
    tk.Label(
        win,
        text="Selecciona tu idioma / Select your language:",
        bg="#3b236b",
        fg="#d0c5ff",
        font=("Segoe UI", 14)
    ).pack(pady=(0, 40))

    idioma_var = tk.StringVar(value="es")

    # Botones de idioma
    frm = tk.Frame(win, bg="#3b236b")
    frm.pack(pady=10)

    def elegir(lang):
        idioma_var.set(lang)
        win.destroy()

    btn_es = tk.Button(
        frm,
        text="🇪🇸 Español",
        font=("Segoe UI", 14, "bold"),
        bg="#6148a6",
        fg="white",
        activebackground="#7b59c6",
        activeforeground="white",
        width=12,
        height=2,
        relief="flat",
        command=lambda: elegir("es")
    )
    btn_es.pack(side="left", padx=30)

    btn_en = tk.Button(
        frm,
        text="🇺🇸 English",
        font=("Segoe UI", 14, "bold"),
        bg="#6148a6",
        fg="white",
        activebackground="#7b59c6",
        activeforeground="white",
        width=12,
        height=2,
        relief="flat",
        command=lambda: elegir("en")
    )
    btn_en.pack(side="right", padx=30)

    # Pie de pagina
    tk.Label(
        win,
        text="© 2025 CineSeven",
        bg="#3b236b",
        fg="#b0a0d0",
        font=("Segoe UI", 10)
    ).pack(side="bottom", pady=20)

    win.mainloop()
    return idioma_var.get()



# Funcion para la ventana de autenticación (Login o Registro)
def ventana_login_o_registro(idioma_inicial):

    # Crear ventana principal de login/registro
    win = tk.Tk()
    win.title("CineSeven - Acceso" if idioma_inicial == "es" else "CineSeven - Access")
    win.configure(bg="#3b236b")
    win.resizable(False, False)

    # Centrar la ventana en la pantalla
    w, h = 500, 550
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 3
    win.geometry(f"{w}x{h}+{x}+{y}")

    # Crear instancia del usuario actual y cargar textos del idioma
    usuario_activo = Usuario()
    textos = TEXTOS_LOGIN[idioma_inicial]

    # Encabezado de la ventana (título y texto principal)
    tk.Label(
        win,
        text=textos["titulo"],
        bg="#3b236b",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(30, 20))

    tk.Label(
        win,
        text=textos["pregunta"],
        bg="#3b236b",
        fg="#d0c5ff",
        font=("Segoe UI", 14)
    ).pack(pady=(0, 30))

    # Marcos contenedores para botones y formularios
    frame_botones = tk.Frame(win, bg="#3b236b")
    frame_botones.pack(pady=10)

    frame_form = tk.Frame(win, bg="#3b236b")
    frame_form.pack(pady=15)

    # Variables asociadas a los campos de entrada
    nombre_var = tk.StringVar()
    apellido_var = tk.StringVar()
    nombreapp_var = tk.StringVar()
    email_var = tk.StringVar()
    pass_var = tk.StringVar()

    # Función auxiliar para limpiar el formulario actual
    def limpiar_formulario():
        for widget in frame_form.winfo_children():
            widget.destroy()

    # SECCIÓN: LOGIN (Iniciar sesión)
    def mostrar_login():
        limpiar_formulario()

        # Campos de correo y contraseña
        tk.Label(frame_form, text=textos["email"], bg="#3b236b", fg="white").pack(pady=5)
        tk.Entry(frame_form, textvariable=email_var, width=40).pack()
        tk.Label(frame_form, text=textos["password"], bg="#3b236b", fg="white").pack(pady=5)

        # Campo de contraseña con opción para mostrar/ocultar
        pw_entry = tk.Entry(frame_form, textvariable=pass_var, width=40, show="*")
        pw_entry.pack()

        # Función para alternar visibilidad de contraseña
        def toggle_pw():
            if pw_entry.cget("show") == "":
                pw_entry.config(show="*")
                btn_pw.config(text=textos["pw_mostrar"])
            else:
                pw_entry.config(show="")
                btn_pw.config(text=textos["pw_ocultar"])

        # Botón para mostrar/ocultar contraseña
        btn_pw = tk.Button(frame_form, text=textos["pw_mostrar"], bg="#6148a6", fg="white", command=toggle_pw)
        btn_pw.pack(pady=4)

        # Función para iniciar sesión
        def iniciar():
            email = email_var.get().strip()
            password = pass_var.get().strip()

            # Validaciones básicas
            if not (email and password):
                messagebox.showwarning("Login", textos["aviso_login"])
                return
            if not validar_email(email):
                messagebox.showerror("❌", textos["email_invalido"])
                return

            # Verificar credenciales
            ok, _ = usuario_activo.login(email, password)
            if ok:
                nombre_display = usuario_activo.nombre_app or usuario_activo.nombre or usuario_activo.email or ""
                saludo = textos["saludo"].format(nombre=nombre_display)
                messagebox.showinfo("✅", saludo)
                win.destroy()  # cerrar la ventana tras iniciar sesión
            else:
                messagebox.showerror("❌", textos["login_incorrecto"])

        # Botón principal de login
        tk.Button(
            frame_form,
            text=textos["btn_login"],
            bg="#6148a6",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=20,
            command=iniciar
        ).pack(pady=15)

    # SECCIÓN: REGISTRO (Crear nueva cuenta)
    def mostrar_registro():
        limpiar_formulario()

        # Cargar etiquetas según idioma
        e = ETIQUETAS_REGISTRO[idioma_inicial]

        # Crear campos de texto dinámicamente
        for label_text, var in [
            (e["nombre"], nombre_var),
            (e["apellido"], apellido_var),
            (e["nombre_app"], nombreapp_var),
            (e["email"], email_var),
            (e["password"], pass_var)
        ]:
            tk.Label(frame_form, text=label_text, bg="#3b236b", fg="white").pack(pady=5)
            show = "*" if "Password" in label_text or "Contraseña" in label_text else None
            tk.Entry(frame_form, textvariable=var, width=40, show=show).pack()

        # Función para registrar un nuevo usuario
        def registrar():
            nombre = nombre_var.get().strip()
            apellido = apellido_var.get().strip()
            nombre_app = nombreapp_var.get().strip()
            email = email_var.get().strip()
            password = pass_var.get().strip()

            # Validaciones
            if not (nombre and email and password):
                messagebox.showwarning("Registro", textos["aviso_reg"])
                return
            if not validar_email(email):
                messagebox.showerror("❌", textos["email_invalido"])
                return
            if not validar_password(password):
                messagebox.showerror("❌", textos["password_invalida"])
                return

            # Intentar registrar al usuario
            ok, msg = usuario_activo.registrar(
                nombre=nombre,
                email=email,
                password=password,
                apellido=apellido,
                nombre_app=nombre_app
            )
            if ok:
                # Mostrar mensaje y loguear automáticamente
                messagebox.showinfo("✅", msg)
                ok2, _ = usuario_activo.login(email, password)
                if ok2:
                    nombre_display = usuario_activo.nombre_app or usuario_activo.nombre or usuario_activo.email or ""
                    saludo = textos["saludo"].format(nombre=nombre_display)
                    messagebox.showinfo("✅", saludo)
                win.destroy()
            else:
                messagebox.showerror("❌", msg)

        # Boton principal de registro
        tk.Button(
            frame_form,
            text=textos["btn_registro"],
            bg="#6148a6",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=20,
            command=registrar
        ).pack(pady=15)

    # Botones principales (para alternar entre Login / Registro)
    tk.Button(
        frame_botones,
        text=textos["btn_login"],
        bg="#6148a6",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        width=14,
        command=mostrar_login
    ).pack(side="left", padx=15)

    tk.Button(
        frame_botones,
        text=textos["btn_registro"],
        bg="#6148a6",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        width=14,
        command=mostrar_registro
    ).pack(side="right", padx=15)

    # Pie de pagina
    tk.Label(
        win,
        text="© 2025 CineSeven",
        bg="#3b236b",
        fg="#b0a0d0",
        font=("Segoe UI", 10)
    ).pack(side="bottom", pady=20)

    # Mantener ventana activa hasta que el usuario decida
    win.mainloop()
    return usuario_activo


# Bloque principal de ejecucion
if __name__ == "__main__":
    if not Path(CSV_PATH).exists():
        tk.messagebox.showerror("Error", f"No se encontró el archivo {CSV_PATH}")
    else:
        idioma_inicial = seleccionar_idioma_inicial()
        usuario_activo = ventana_login_o_registro(idioma_inicial)

        if usuario_activo and usuario_activo.id:
            root = tk.Tk()
            app = AppPeliculasGUI(root, CatalogoPeliculas(CSV_PATH, idioma_inicial), idioma_inicial)
            app.usuario = usuario_activo
            root.mainloop()
        else:
            print("⚠️ No se pudo iniciar sesión o no hay usuario activo.")
