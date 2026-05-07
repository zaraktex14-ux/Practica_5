import tkinter as tk
from tkinter import messagebox, filedialog
from math import cos, sin, radians
import xml.etree.ElementTree as ET


# =====================================
# CLASE ESTADO
# =====================================

class Estado:

    def __init__(self, nombre, inicial=False, final=False):
        self.nombre = nombre
        self.inicial = inicial
        self.final = final


# =====================================
# CLASE AFD
# =====================================

class AFD:

    def __init__(self):
        self.estados = []
        self.transiciones = {}

    def agregar_estado(self, estado):
        self.estados.append(estado)

    def buscar_estado(self, nombre):

        for estado in self.estados:
            if estado.nombre == nombre:
                return estado

        return None

    def agregar_transicion(self, origen, simbolo, destino):
        self.transiciones[(origen, simbolo)] = destino

    def obtener_estado_inicial(self):

        for estado in self.estados:
            if estado.inicial:
                return estado

        return None

    def validar_cadena(self, cadena):

        actual = self.obtener_estado_inicial()

        if actual is None:
            return False, []

        camino = [actual.nombre]

        for simbolo in cadena:

            clave = (actual.nombre, simbolo)

            if clave not in self.transiciones:
                return False, camino

            actual = self.transiciones[clave]

            camino.append(actual.nombre)

        return actual.final, camino


# =====================================
# AUTOMATA
# =====================================

mi_afd = AFD()


# =====================================
# VENTANA
# =====================================

root = tk.Tk()

root.title("Visualizador Interactivo de Autómatas")

root.geometry("1200x700")

root.configure(bg="#F4F6F7")


# =====================================
# FRAME IZQUIERDO
# =====================================

frame_izq = tk.Frame(
    root,
    bg="#D6EAF8",
    width=320
)

frame_izq.pack(
    side="left",
    fill="y"
)


# =====================================
# CANVAS
# =====================================

canvas = tk.Canvas(
    root,
    width=850,
    height=700,
    bg="white"
)

canvas.pack(
    side="right",
    fill="both",
    expand=True
)


# =====================================
# TITULO
# =====================================

lbl_titulo = tk.Label(
    frame_izq,
    text="AUTÓMATAS",
    font=("Arial", 20, "bold"),
    bg="#D6EAF8"
)

lbl_titulo.pack(pady=15)


# =====================================
# AGREGAR ESTADOS
# =====================================

lbl_estado = tk.Label(
    frame_izq,
    text="Nombre del estado",
    font=("Arial", 9),
    bg="#D6EAF8"
)

lbl_estado.pack()

entry_estado = tk.Entry(
    frame_izq,
    font=("Arial", 12)
)

entry_estado.pack(pady=5)


# =====================================
# CHECKS
# =====================================

var_inicial = tk.BooleanVar()

check_inicial = tk.Checkbutton(
    frame_izq,
    text="Estado inicial",
    variable=var_inicial,
    bg="#D6EAF8"
)

check_inicial.pack()


var_final = tk.BooleanVar()

check_final = tk.Checkbutton(
    frame_izq,
    text="Estado final",
    variable=var_final,
    bg="#D6EAF8"
)

check_final.pack()


# =====================================
# POSICIONES
# =====================================

posiciones = {}


# =====================================
# DIBUJAR AUTOMATA
# =====================================

def dibujar_automata():

    canvas.delete("all")

    estados = mi_afd.estados

    if len(estados) == 0:
        return

    centro_x = 420
    centro_y = 320

    radio = 220

    total = len(estados)

    posiciones.clear()

    # =================================
    # POSICIONES CIRCULARES
    # =================================

    for i, estado in enumerate(estados):

        angulo = (360 / total) * i

        x = centro_x + radio * cos(radians(angulo))
        y = centro_y + radio * sin(radians(angulo))

        posiciones[estado.nombre] = (x, y)

    # =================================
    # TRANSICIONES
    # =================================

    for (origen, simbolo), destino in mi_afd.transiciones.items():

        x1, y1 = posiciones[origen]

        x2, y2 = posiciones[destino.nombre]

        canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            arrow=tk.LAST,
            width=2
        )

        texto_x = (x1 + x2) / 2
        texto_y = (y1 + y2) / 2

        canvas.create_text(
            texto_x,
            texto_y - 15,
            text=simbolo,
            fill="blue",
            font=("Arial", 12, "bold")
        )

    # =================================
    # ESTADOS
    # =================================

    for estado in estados:

        x, y = posiciones[estado.nombre]

        # CIRCULO PRINCIPAL
        canvas.create_oval(
            x - 35,
            y - 35,
            x + 35,
            y + 35,
            fill="#AED6F1",
            width=3
        )

        # ESTADO FINAL
        if estado.final:

            canvas.create_oval(
                x - 28,
                y - 28,
                x + 28,
                y + 28,
                width=2
            )

        # ESTADO INICIAL
        if estado.inicial:

            canvas.create_line(
                x - 80,
                y,
                x - 35,
                y,
                arrow=tk.LAST,
                width=3,
                fill="green"
            )

        # TEXTO
        canvas.create_text(
            x,
            y,
            text=estado.nombre,
            font=("Arial", 14, "bold")
        )


# =====================================
# AGREGAR ESTADO
# =====================================

def agregar_estado():

    nombre = entry_estado.get()

    if nombre == "":
        messagebox.showerror(
            "Error",
            "Escribe un nombre"
        )
        return

    # NO REPETIDOS
    if mi_afd.buscar_estado(nombre):

        messagebox.showerror(
            "Error",
            "El estado ya existe"
        )
        return

    inicial = var_inicial.get()

    final = var_final.get()

    # SOLO UN INICIAL
    if inicial:

        for estado in mi_afd.estados:
            estado.inicial = False

    nuevo = Estado(
        nombre,
        inicial,
        final
    )

    mi_afd.agregar_estado(nuevo)

    entry_estado.delete(0, tk.END)

    dibujar_automata()


btn_agregar_estado = tk.Button(
    frame_izq,
    text="Agregar Estado",
    command=agregar_estado,
    bg="#3498DB",
    fg="white",
    font=("Arial", 9, "bold")
)

btn_agregar_estado.pack(pady=9)


# =====================================
# SEPARADOR
# =====================================

sep = tk.Frame(
    frame_izq,
    height=3,
    bg="#5D6D7E"
)

sep.pack(
    fill="x",
    pady=15
)


# =====================================
# TRANSICIONES
# =====================================

lbl_trans = tk.Label(
    frame_izq,
    text="Agregar Transición",
    font=("Arial", 9, "bold"),
    bg="#D6EAF8"
)

lbl_trans.pack(pady=5)


entry_origen = tk.Entry(
    frame_izq,
    font=("Arial", 9)
)

entry_origen.pack(pady=5)
entry_origen.insert(0, "Estado origen")


entry_simbolo = tk.Entry(
    frame_izq,
    font=("Arial", 9)
)

entry_simbolo.pack(pady=5)
entry_simbolo.insert(0, "Símbolo")


entry_destino = tk.Entry(
    frame_izq,
    font=("Arial", 9)
)

entry_destino.pack(pady=9)
entry_destino.insert(0, "Estado destino")


# =====================================
# AGREGAR TRANSICION
# =====================================

def agregar_transicion():

    origen = entry_origen.get()

    simbolo = entry_simbolo.get()

    destino = entry_destino.get()

    estado_origen = mi_afd.buscar_estado(origen)

    estado_destino = mi_afd.buscar_estado(destino)

    if estado_origen is None:

        messagebox.showerror(
            "Error",
            "Estado origen no existe"
        )
        return

    if estado_destino is None:

        messagebox.showerror(
            "Error",
            "Estado destino no existe"
        )
        return

    # =================================
    # EVITAR TRANSICIONES REPETIDAS
    # =================================

    clave = (origen, simbolo)

    if clave in mi_afd.transiciones:

        messagebox.showerror(
            "Error",
            f"Ya existe transición para {origen} con '{simbolo}'"
        )
        return

    mi_afd.agregar_transicion(
        origen,
        simbolo,
        estado_destino
    )

    dibujar_automata()


btn_transicion = tk.Button(
    frame_izq,
    text="Agregar Transición",
    command=agregar_transicion,
    bg="#27AE60",
    fg="white",
    font=("Arial", 9, "bold")
)

btn_transicion.pack(pady=9)


# =====================================
# SEPARADOR
# =====================================

sep2 = tk.Frame(
    frame_izq,
    height=3,
    bg="#5D6D7E"
)

sep2.pack(
    fill="x",
    pady=9
)


# =====================================
# PROBAR CADENA
# =====================================

lbl_prueba = tk.Label(
    frame_izq,
    text="Probar Cadena",
    font=("Arial", 9, "bold"),
    bg="#D6EAF8"
)

lbl_prueba.pack(pady=5)


entry_cadena = tk.Entry(
    frame_izq,
    font=("Arial", 9)
)

entry_cadena.pack(pady=5)


resultado = tk.Label(
    frame_izq,
    text="",
    font=("Arial", 9, "bold"),
    bg="#D6EAF8"
)

resultado.pack(pady=10)


# =====================================
# ANIMAR RECORRIDO
# =====================================

def animar(camino):

    canvas.delete("resaltado")

    for nombre in camino:

        if nombre in posiciones:

            x, y = posiciones[nombre]

            canvas.create_oval(
                x - 42,
                y - 42,
                x + 42,
                y + 42,
                outline="red",
                width=4,
                tags="resaltado"
            )


# =====================================
# VALIDAR CADENA
# =====================================

def probar_cadena():

    cadena = entry_cadena.get()

    valido, camino = mi_afd.validar_cadena(cadena)

    if valido:

        resultado.config(
            text=f"ACEPTADA\n{' → '.join(camino)}",
            fg="green"
        )

    else:

        resultado.config(
            text=f"RECHAZADA\n{' → '.join(camino)}",
            fg="red"
        )

    animar(camino)


btn_probar = tk.Button(
    frame_izq,
    text="Probar",
    command=probar_cadena,
    bg="#E67E22",
    fg="white",
    font=("Arial", 11, "bold")
)

btn_probar.pack(pady=9)


# =====================================
# GUARDAR JFLAP
# =====================================

def guardar_jflap():

    archivo = filedialog.asksaveasfilename(
        defaultextension=".jff",
        filetypes=[("JFLAP", "*.jff")]
    )

    if not archivo:
        return

    structure = ET.Element("structure")

    tipo = ET.SubElement(
        structure,
        "type"
    )

    tipo.text = "fa"

    automaton = ET.SubElement(
        structure,
        "automaton"
    )

    ids = {}

# =====================================
# ABRIR JFLAP
# =====================================

def abrir_jflap():

    archivo = filedialog.askopenfilename(
        filetypes=[("JFLAP", "*.jff")]
    )

    if not archivo:
        return

    try:

        tree = ET.parse(archivo)

        root_xml = tree.getroot()

        automaton = root_xml.find("automaton")

        # LIMPIAR AUTOMATA ACTUAL
        mi_afd.estados.clear()
        mi_afd.transiciones.clear()

        ids_estados = {}

        # =================================
        # CARGAR ESTADOS
        # =================================

        for state in automaton.findall("state"):

            nombre = state.get("name")

            estado_id = state.get("id")

            inicial = state.find("initial") is not None

            final = state.find("final") is not None

            nuevo_estado = Estado(
                nombre,
                inicial,
                final
            )

            mi_afd.agregar_estado(nuevo_estado)

            ids_estados[estado_id] = nuevo_estado

        # =================================
        # CARGAR TRANSICIONES
        # =================================

        for transition in automaton.findall("transition"):

            origen_id = transition.find("from").text

            destino_id = transition.find("to").text

            simbolo_tag = transition.find("read")

            simbolo = ""

            if simbolo_tag is not None and simbolo_tag.text:
                simbolo = simbolo_tag.text

            origen_estado = ids_estados[origen_id]

            destino_estado = ids_estados[destino_id]

            mi_afd.agregar_transicion(
                origen_estado.nombre,
                simbolo,
                destino_estado
            )

        dibujar_automata()

        messagebox.showinfo(
            "Archivo cargado",
            "Automata cargado correctamente"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No se pudo abrir el archivo\n{e}"
        )
    # =================================
    # ESTADOS
    # =================================

    for i, estado in enumerate(mi_afd.estados):

        ids[estado.nombre] = str(i)

        state = ET.SubElement(
            automaton,
            "state",
            id=str(i),
            name=estado.nombre
        )

        x = ET.SubElement(state, "x")
        x.text = str(100 + (i * 100))

        y = ET.SubElement(state, "y")
        y.text = "100"

        if estado.inicial:
            ET.SubElement(state, "initial")

        if estado.final:
            ET.SubElement(state, "final")

    # =================================
    # TRANSICIONES
    # =================================

    for (origen, simbolo), destino in mi_afd.transiciones.items():

        transition = ET.SubElement(
            automaton,
            "transition"
        )

        from_tag = ET.SubElement(
            transition,
            "from"
        )

        from_tag.text = ids[origen]

        to_tag = ET.SubElement(
            transition,
            "to"
        )

        to_tag.text = ids[destino.nombre]

        read = ET.SubElement(
            transition,
            "read"
        )

        read.text = simbolo

    tree = ET.ElementTree(structure)

    tree.write(
        archivo,
        encoding="utf-8",
        xml_declaration=True
    )

    messagebox.showinfo(
        "Guardado",
        "Archivo JFLAP guardado correctamente"
    )


btn_guardar = tk.Button(
    frame_izq,
    text="Guardar JFLAP",
    command=guardar_jflap,
    bg="#8E44AD",
    fg="white",
    font=("Arial", 9, "bold")
)

btn_guardar.pack(pady=9)

btn_abrir = tk.Button(
    frame_izq,
    text="Abrir JFLAP",
    command=abrir_jflap,
    bg="#16A085",
    fg="white",
    font=("Arial", 9, "bold")
)

btn_abrir.pack(pady=9)


# =====================================
# EJECUTAR
# =====================================

root.mainloop()
