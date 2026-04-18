import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import threading
import requests
import keyboard
import pyperclip
import os

from licensing import LicenseController

# Script flotante que lee el portapapeles y consulta Ollama con una hotkey global.
# ==============================
# CONFIGURACIÓN
# ==============================
MODELO = "llama3"
TECLA_LECTURA = "F7"
TECLA_OCULTAR = "F8"
TECLA_MOSTRAR = "F9"
TECLA_SALIR = "F10"
# Endpoint del servidor de licencias (se puede cambiar por variable de entorno).
LICENSE_API_URL = os.getenv("LICENSE_API_URL", "http://127.0.0.1:8008")
# Frecuencia objetivo de chequeo remoto de licencia (en horas).
LICENSE_CHECK_HOURS = int(os.getenv("LICENSE_CHECK_HOURS", "24"))
# Ventana offline permitida si no hay conexion con el servidor de licencias.
LICENSE_GRACE_HOURS = int(os.getenv("LICENSE_GRACE_HOURS", "72"))


def pedir_licencia(root):
    # Dialogo de activacion mostrado solo cuando no hay licencia valida local.
    return simpledialog.askstring(
        "Activacion de licencia",
        "Ingresa tu licencia para activar AsistenteCajaPro:",
        parent=root,
    )


def validar_licencia_inicio():
    # Ventana oculta temporal para usar cuadros de dialogo antes de abrir el overlay.
    gate = tk.Tk()
    gate.withdraw()

    # Controlador central de activacion/revalidacion.
    controller = LicenseController(
        api_base_url=LICENSE_API_URL,
        check_hours=LICENSE_CHECK_HOURS,
        grace_hours=LICENSE_GRACE_HOURS,
    )

    # Intenta validar estado local o activar con clave si no existe licencia valida.
    ok, mensaje = controller.ensure_valid(lambda: pedir_licencia(gate))
    if not ok:
        # Si falla la validacion, se aborta el inicio de la app.
        messagebox.showerror("Licencia", mensaje, parent=gate)
        gate.destroy()
        return None

    # Avisa cuando entra en modo gracia (uso temporal sin conexion).
    if "gracia" in mensaje.lower():
        messagebox.showwarning("Licencia", mensaje, parent=gate)

    gate.destroy()
    return controller

def preguntar_ollama(texto):
    try:
        # Fuerza una respuesta en codigo y evita errores frecuentes de acumulacion en menus.
        prompt = f"""Responde SOLO con código Python. 
        Enunciado: {texto}
        REGLA: Si hay un menú while, asegúrate de que los cálculos de sumas (totales) 
        y contadores se reinicien a 0 dentro de la opción del menú para evitar acumulación errónea."""
        
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": MODELO, "prompt": prompt, "stream": False, 
                  "options": {"temperature": 0.1}}, timeout=60)
        return r.json().get("response", "").strip()
    except: return "Error: Verifica Ollama"

# ==============================
# INTERFAZ
# ==============================
class AsistenteCajaPro:
    def __init__(self, license_controller):
        # Se guarda para revalidaciones periodicas durante la ejecucion.
        self.license_controller = license_controller
        # Ventana sin bordes y siempre visible para usarla como overlay.
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.bg_key = "#ffffff" 
        self.root.config(bg=self.bg_key)
        self.root.attributes("-transparentcolor", self.bg_key)
        self.root.geometry("600x160+250+250")

        self.label = tk.Label(self.root, text=f"[ SISTEMA CORREGIDO | PULSA {TECLA_LECTURA} ]",
                              font=("Consolas", 9), fg="#333333", bg=self.bg_key, 
                              wraplength=530, justify="left")
        self.label.pack(side="left", padx=10, fill="both", expand=True)

        self.btn_copy = tk.Label(self.root, text="📋", font=("Arial", 16), 
                                 fg="#888888", bg=self.bg_key, cursor="hand2")
        self.btn_copy.pack(side="right", padx=15)
        self.btn_copy.bind("<Button-1>", self.copiar_limpio)

        # Atajos globales: una tecla ejecuta lectura; otra oculta; otra muestra; otra cierra.
        keyboard.add_hotkey(TECLA_LECTURA, self.go, suppress=True)
        keyboard.add_hotkey(TECLA_OCULTAR, self.ocultar, suppress=True)
        keyboard.add_hotkey(TECLA_MOSTRAR, self.mostrar, suppress=True)
        keyboard.add_hotkey(TECLA_SALIR, self.salir, suppress=True)
        self.label.bind("<Button-1>", self.atrapa)
        self.label.bind("<B1-Motion>", self.mueve)
        # Programa chequeo periodico de licencia para detectar revocacion remota.
        self.root.after(3600 * 1000, self.revalidar_licencia_periodica)

    def atrapa(self, e): self.x, self.y = e.x, e.y
    def mueve(self, e): self.root.geometry(f"+{e.x_root-self.x}+{e.y_root-self.y}")

    def ocultar(self):
        self.root.withdraw()

    def mostrar(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(50, self.root.focus_force)

    def salir(self):
        os._exit(0)

    def revalidar_licencia_periodica(self):
        # Revalida en segundo plano sin pedir clave nuevamente al usuario.
        ok, mensaje = self.license_controller.revalidate_non_interactive()
        if not ok:
            # Si el servidor invalida la licencia, se cierra para impedir uso no autorizado.
            messagebox.showerror("Licencia", mensaje)
            self.salir()
            return

        # Reagenda el siguiente chequeo periodico.
        self.root.after(3600 * 1000, self.revalidar_licencia_periodica)


    def copiar_limpio(self, event):
        # Solo copia respuestas; evita copiar el texto inicial del sistema.
        txt = self.label.cget("text")
        if "[ SISTEMA" not in txt:
            pyperclip.copy(txt)
            self.btn_copy.config(fg="#28a745")
            self.root.after(600, lambda: self.btn_copy.config(fg="#888888"))

    def go(self): threading.Thread(target=self.work, daemon=True).start()
    def work(self):
        # No bloquea la interfaz: consulta en segundo plano y actualiza al terminar.
        self.root.after(0, lambda: self.label.config(text="Calculando lógica correcta..."))
        res = preguntar_ollama(pyperclip.paste())
        self.root.after(0, lambda: self.label.config(text=res))

if __name__ == "__main__":
    # Bloquea el inicio si no hay licencia valida.
    controller = validar_licencia_inicio()
    if not controller:
        os._exit(1)

    app = AsistenteCajaPro(controller)
    app.root.mainloop()


