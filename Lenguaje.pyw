import tkinter as tk
import threading
import requests
import keyboard
import pyperclip
import os

# Script flotante que lee el portapapeles y consulta Ollama con una hotkey global.
# ==============================
# CONFIGURACIÓN
# ==============================
MODELO = "llama3"
TECLA_LECTURA = "F7"
TECLA_OCULTAR = "F8"
TECLA_MOSTRAR = "F9"
TECLA_SALIR = "F10"

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
    def __init__(self):
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
    app = AsistenteCajaPro()
    app.root.mainloop()


