import json, os, random
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(CARPETA, "preguntas.json")
FUENTE = ("Times New Roman", 14)
COLOR = "#0a0a0a"
MIN_PREG = 5
VIDAS_INICIALES = 3


def cargar():
    if not os.path.exists(ARCHIVO):
        return []
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos if isinstance(datos, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def guardar(preguntas):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, ensure_ascii=False, indent=4)


class VentanaAgregar(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Agregar pregunta")
        self.entradas = {}
        for i, campo in enumerate(("Pregunta", "Respuesta", "Dificultad")):
            tk.Label(self, text=campo + ":").grid(row=i, column=0, padx=8, pady=6, sticky="e")
            e = tk.Entry(self, width=45)
            e.grid(row=i, column=1, padx=8, pady=6)
            self.entradas[campo] = e
        tk.Button(self, text="Guardar", command=self._guardar).grid(row=3, column=0, columnspan=2, pady=10)
        self.protocol("WM_DELETE_WINDOW", self._guardar)

    def _guardar(self):
        pregunta = self.entradas["Pregunta"].get().strip()
        respuesta = self.entradas["Respuesta"].get().strip()
        dificultad = self.entradas["Dificultad"].get().strip() or "facil"
        if pregunta and respuesta:
            datos = cargar()
            datos.append({"pregunta": pregunta, "respuesta": respuesta, "dificultad": dificultad})
            guardar(datos)
        self.destroy()


class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz de Tecnologia")
        self.geometry("560x420")
        menu = tk.Menu(self)
        archivo = tk.Menu(menu, tearoff=0)
        archivo.add_command(label="Jugar", command=self.jugar)
        archivo.add_command(label="Agregar", command=lambda: VentanaAgregar(self))
        archivo.add_command(label="Salir", command=self.destroy)
        menu.add_cascade(label="File", menu=archivo)
        menu.add_cascade(label="Help", menu=tk.Menu(menu, tearoff=0))
        self.config(menu=menu)
        self.inicio()

    def inicio(self):
        if hasattr(self, "vista"):
            self.vista.pack_forget()
        self.vista = tk.Frame(self)
        self.vista.pack(expand=True, fill="both")
        tk.Label(self.vista, text="Quiz de Tecnologia",
                 font=("Times New Roman", 18, "bold"), fg=COLOR).pack(pady=30)
        tk.Button(self.vista, text="Jugar", width=20, command=self.jugar).pack(pady=10)
        tk.Button(self.vista, text="Agregar pregunta", width=20, command=lambda: VentanaAgregar(self)).pack(pady=5)
        tk.Button(self.vista, text="Salir", width=20, command=self.destroy).pack(pady=5)

    def jugar(self):
        if not os.path.exists(ARCHIVO):
            messagebox.showerror("Archivo no encontrado", f"No existe el archivo {ARCHIVO}.")
            return
        todas = cargar()
        if len(todas) < MIN_PREG:
            messagebox.showerror("Error", f"al menos se necesitan {MIN_PREG} preguntas (hay {len(todas)}).")
            return
        self.preguntas = random.sample(todas, MIN_PREG)
        self.idx = 0
        self.puntaje = 0
        self.vidas = VIDAS_INICIALES
        self.vista.pack_forget()
        self._vista_juego()
        self._mostrar()

    def _vista_juego(self):
        self.vista = tk.Frame(self, padx=10, pady=10)
        self.vista.pack(expand=True, fill="both")
        self.lbl_estado = tk.Label(self.vista, text="", font=("Arial", 11, "bold"))
        self.lbl_estado.pack(anchor="e")
        self.texto = ScrolledText(self.vista, height=8, wrap="word", font=FUENTE, fg=COLOR)
        self.texto.pack(fill="both", expand=True, pady=10)
        self.entry = tk.Entry(self.vista, width=40)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda e: self._responder())
        tk.Button(self.vista, text="Responder", command=self._responder).pack()

    def _mostrar(self):
        try:
            self.lbl_estado.config(text=f"Puntaje: {self.puntaje}    Vidas: {self.vidas}")
            p = self.preguntas[self.idx]
            texto_pregunta = p["pregunta"]
            self.texto.config(state="normal")
            self.texto.delete("1.0", tk.END)
            self.texto.insert(tk.END, f"Pregunta {self.idx + 1} de {MIN_PREG}:\n\n{texto_pregunta}")
            self.texto.config(state="disabled")
            self.entry.delete(0, tk.END)
            self.entry.focus_set()
        except (KeyError, IndexError) as error:
            messagebox.showerror("Error al mostrar la pregunta", f"Revisa preguntas.json: {error}")

    def _responder(self):
        correcta = str(self.preguntas[self.idx]["respuesta"]).strip().lower()
        if self.entry.get().strip().lower() == correcta:
            self.puntaje += 1
            messagebox.showinfo("Correcto", "\u00a1Respuesta correcta!")
        else:
            self.vidas -= 1
            messagebox.showinfo("Incorrecto", f"La respuesta era: {correcta}\nVidas restantes: {self.vidas}")
        self.idx += 1
        if self.vidas <= 0:
            self._resultados("Te quedaste sin vidas :(")
        elif self.idx < MIN_PREG:
            self._mostrar()
        else:
            self._resultados("Respondiste todas las preguntas")

    def _resultados(self, motivo):
        self.vista.pack_forget()
        self.vista = tk.Frame(self)
        self.vista.pack(expand=True, fill="both")
        tk.Label(self.vista, text="\u00a1Juego terminado!", font=("Times New Roman", 18, "bold"), fg=COLOR).pack(pady=20)
        tk.Label(self.vista, text=motivo, font=("Arial", 11)).pack()
        tk.Label(self.vista, text=f"Puntaje final: {self.puntaje}    Vidas restantes: {self.vidas}", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.vista, text="Volver al inicio", command=self.inicio).pack(pady=20)


if __name__ == "__main__":
    QuizApp().mainloop()