import json
import tkinter as tk
import gramaticas
from tkinter import ttk, messagebox, scrolledtext
from tkinter import filedialog 
from PIL import Image, ImageTk
try:
    import expresiones
    import herramientas 
    import afd, afnd
except ImportError:
    pass
exr =  expresiones.RegexValidator()
mi_afd = afd.AFD()
mi_afnd = afnd.AFN()
def cargar_automata_archivo():
    ruta = filedialog.askopenfilename(
        title="Seleccionar Autómata",
        filetypes=(("Archivos AFD", "*.afd"), ("Archivos JFLAP", "*.jff"), ("Todos", "*.*"))
    )
    
    if not ruta:
        return

    try:
        if ruta.endswith('.afd'):
            with open(ruta, 'r') as f:
                datos = json.load(f)
                global mi_afd
                mi_afd = afd.AFD.from_dict(datos)
        
        elif ruta.endswith('.jff'):

            with open(ruta, 'r') as f:
                contenido = f.read()
                mi_afd = afd.AFD.from_jff_format(contenido)

        actualizar_interfaz_afd()
        messagebox.showinfo("Éxito", "Autómata cargado correctamente")
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar: {str(e)}")
def guardar_automata_archivo():
    if not mi_afd.states:
        messagebox.showwarning("Atención", "No hay un autómata configurado para guardar.")
        return

    ruta = filedialog.asksaveasfilename(
        defaultextension=".afd",
        filetypes=(("Archivos AFD", "*.afd"), ("Todos", "*.*"))
    )
    
    if ruta:
        try:
            datos = mi_afd.to_dict()
            with open(ruta, 'w') as f:
                json.dump(datos, f, indent=4)
            messagebox.showinfo("Éxito", f"Autómata guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

def limpiar_interfaz_y_datos():
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres borrar el autómata actual?"):
        global mi_afd
        mi_afd = afd.AFD() 
        actualizar_interfaz_afd() 
        lbl_res_afd.config(text="")
        entry_probar.delete(0, tk.END) 
        messagebox.showinfo("Limpiar", "Simulador reiniciado correctamente.")

def actualizar_interfaz_afd():
    # 1. Obtener el alfabeto ordenado para las columnas
    alfabeto = sorted(list(mi_afd.alphabet))
    
    # 2. Configurar nuevas columnas: "Estado" + cada símbolo del alfabeto
    columnas = ["Estado"] + alfabeto
    tree_trans["columns"] = columnas
    tree_trans["show"] = "headings"
    
    # 3. Definir encabezados
    tree_trans.heading("Estado", text="Estado")
    tree_trans.column("Estado", width=150, anchor="center")
    
    for simb in alfabeto:
        tree_trans.heading(simb, text=str(simb))
        tree_trans.column(simb, width=100, anchor="center")

    # 4. Limpiar datos viejos
    for item in tree_trans.get_children():
        tree_trans.delete(item)
   
    # 5. Insertar filas (un estado por fila)
    for estado in mi_afd.states:
        # Formatear nombre: q0 (I), q2 (F), etc.
        nombre_mostrar = estado.name
        if estado.is_initial: nombre_mostrar += " (I)"
        if estado.is_final: nombre_mostrar += " (F)"
        
        valores = [nombre_mostrar]
        
        # Buscar destino para cada símbolo del alfabeto
        for simb in alfabeto:
            destino = mi_afd.transitions.get((estado, simb))
            valores.append(destino.name if destino else "-")
        
        tree_trans.insert("", "end", values=valores)

    # Actualizar ComboBoxes
    nombres = [s.name for s in mi_afd.states]
    cb_desde['values'] = nombres
    cb_hacia['values'] = nombres

def agregar_estado_interfaz():
    nombre = entry_estado_nombre.get().strip()
    es_ini = var_es_inicial.get()
    es_fin = var_es_final.get()
    
    if nombre:
        nuevo = mi_afd.add_state(nombre, es_ini, es_fin)
        if nuevo:
            listado = [s.name for s in mi_afd.states]
            cb_desde['values'] = listado
            cb_hacia['values'] = listado
            messagebox.showinfo("Éxito", f"Estado {nombre} agregado")
        else:
            messagebox.showerror("Error", "El estado ya existe")
    
def agregar_transicion_interfaz():
    f = cb_desde.get()
    s = entry_simbolo.get().strip()
    t = cb_hacia.get()
    
    if not f or not s or not t:
        messagebox.showerror("Error", "Debe completar todos los campos de la transición")
        return

    if mi_afd.add_transition(f, s, t):
        # En lugar de solo insertar una fila, refrescamos toda la tabla
        # para que se creen las columnas de los símbolos si es necesario
        actualizar_interfaz_afd()
        entry_simbolo.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "No se pudo agregar la transición")

def probar_cadena():
    cadena = entry_probar.get()
    valido, camino = mi_afd.validate_string(cadena)
    color = "green" if valido else "red"
    lbl_res_afd.config(text=f"Resultado: {'Aceptada' if valido else 'Rechazada'}\nRuta: {camino}", fg=color)


def validate_string(self):
    input_string = self.input_string_var.get()
    
    is_accepted, steps = mi_afd.validate_string(input_string)
    
    self.simulation_steps = steps
    self.current_step = 0

    if is_accepted:
        self.validation_result_var.set("Resultado: Válido")
        self.validation_result_label.configure(foreground="green")
    else:
        self.validation_result_var.set("Resultado: Inválido")
        self.validation_result_label.configure(foreground="red")
 
    self.update_simulation_view()



def ejecutar_minimizacion():
    # 1. Limpiar el texto de simulación
    text_reporte.config(state="normal")
    text_reporte.delete('1.0', tk.END)
    
    if not mi_afd.states:
        messagebox.showwarning("Aviso", "No hay un autómata cargado para minimizar.")
        return

    res_min = mi_afd.minimizar_y_reportar()

    text_reporte.insert(tk.END, res_min)

    cadenas_prueba = ["", "0", "1", "01", "10", "110", "001"] # Ejemplos
    text_reporte.insert(tk.END, "\n=== VERIFICACIÓN DE EQUIVALENCIA ===\n")
    text_reporte.insert(tk.END, f"{'Cadena':<15} | {'Original':<15}\n")
    text_reporte.insert(tk.END, "-"*35 + "\n")
    
    for c in cadenas_prueba:
        valido_orig, _ = mi_afd.validate_string(c)
        res_txt = "Aceptada" if valido_orig else "Rechazada"
        text_reporte.insert(tk.END, f"{c if c != '' else 'λ':<15} | {res_txt:<15}\n")

    text_reporte.config(state="disabled")

def centrar_ventana(ventana, ancho, alto):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def ejecutar_analisis_cadena():
    cadena = entry_cadena.get()
    if not cadena:
        messagebox.showwarning("Atención", "Escribe una cadena primero")

    prefijos, sufijos, subcadenas = herramientas.obtener_analisis_cadena(cadena)
    
    txt_analisis.delete(1.0, tk.END)
    txt_analisis.insert(tk.END, f"Analizando cadena: '{cadena}'\n")
    txt_analisis.insert(tk.END, "-"*40 + "\n")
    txt_analisis.insert(tk.END, f"PREFIJOS: {', '.join([p if p != '' else 'λ' for p in prefijos])}\n\n")
    txt_analisis.insert(tk.END, f"SUFIJOS: {', '.join([s if s != '' else 'λ' for s in sufijos])}\n\n")
    txt_analisis.insert(tk.END, f"SUBCADENAS ({len(subcadenas)}): {', '.join(subcadenas)}")

def ejecutar_calculo_kleene():
    alfabeto = entry_alfabeto.get()
    try:
        limite = int(entry_limite.get())

        star, plus = herramientas.calcular_kleene_logic(alfabeto, limite)
        
        txt_resultados.delete(1.0, tk.END)
        txt_resultados.insert(tk.END, f"Σ* (Kleene): {', '.join(star)}\n\n")
        txt_resultados.insert(tk.END, f"Σ+ (Positiva): {', '.join(plus)}")
    except ValueError:
        messagebox.showerror("Error", "La longitud debe ser un número entero")

root = tk.Tk()
root.title("Practicas de Teoría de la Computación")
centrar_ventana(root, 900, 700)


portada = tk.Frame(root, bg="#0B436E", pady=20)
portada.pack(fill="x")
tk.Label(portada, text="TEORÍA DE LA COMPUTACIÓN", font=("Arial", 18, "bold"), fg="white", bg="#0B436E").pack()
tk.Label(portada, text="Resendiz Garcia Renata", font=("Arial", 10), fg="#d2dae2", bg="#0B436E").pack()
tk.Label(portada, text="Hernandez Hernandez Wendy", font=("Arial", 10), fg="#d2dae2", bg="#0B436E").pack()
tk.Label(portada, text="Perez Griselda", font=("Arial", 10), fg="#d2dae2", bg="#0B436E").pack()

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=20, pady=20)

# --- PESTAÑA 1: KLEENE ---
tab_kleene = tk.Frame(notebook, bg="white")
notebook.add(tab_kleene, text=" Cerraduras (Kleene) ")

frame_k = tk.Frame(tab_kleene, bg="white", pady=10)
frame_k.pack()

tk.Label(frame_k, text="Alfabeto:", bg="white").grid(row=0, column=0)
entry_alfabeto = tk.Entry(frame_k)
entry_alfabeto.grid(row=0, column=1, padx=5)

tk.Label(frame_k, text="Longitud Máx:", bg="white").grid(row=0, column=2)
entry_limite = tk.Entry(frame_k, width=5)
entry_limite.insert(0, "3")
entry_limite.grid(row=0, column=3, padx=5)

btn_k = tk.Button(frame_k, text="Calcular", command=ejecutar_calculo_kleene, bg="#344fe7", fg="white")
btn_k.grid(row=0, column=4, padx=10)

txt_resultados = scrolledtext.ScrolledText(tab_kleene, height=15, width=80)
txt_resultados.pack(pady=10, padx=10)


# --- PESTAÑA 2: SUBCADENAS ---
tab_tools = tk.Frame(notebook, bg="white")
notebook.add(tab_tools, text=" Subcadenas/Sufijos ")

frame_c = tk.Frame(tab_tools, bg="white", pady=15)
frame_c.pack()

tk.Label(frame_c, text="Cadena:", bg="white").grid(row=0, column=0)
entry_cadena = tk.Entry(frame_c, width=30)
entry_cadena.grid(row=0, column=1, padx=10)

btn_c = tk.Button(frame_c, text="Analizar", command=ejecutar_analisis_cadena, bg="#0B436E", fg="white")
btn_c.grid(row=0, column=2, padx=5)

txt_analisis = scrolledtext.ScrolledText(tab_tools, height=15, width=80)
txt_analisis.pack(pady=10, padx=20)

# --- PESTAÑA 3: AFD ---
tab_afd = tk.Frame(notebook, bg="white")
notebook.add(tab_afd, text=" Definir AFD ")
f_acciones = tk.Frame(tab_afd, bg="white")
f_acciones.pack(fill="x", padx=10, pady=5)
btn_cargar = tk.Button(f_acciones, text="Cargar", command=cargar_automata_archivo, 
                       bg="#2ecc71", fg="white", width=12)
btn_cargar.pack(side="left", padx=5)

btn_guardar = tk.Button(f_acciones, text="Guardar", command=guardar_automata_archivo, 
                        bg="#3498db", fg="white", width=12)
btn_guardar.pack(side="left", padx=5)

btn_limpiar = tk.Button(f_acciones, text="Limpiar", command=limpiar_interfaz_y_datos, 
                        bg="#e74c3c", fg="white", width=12)
btn_limpiar.pack(side="left", padx=5)

f_estados = ttk.LabelFrame(tab_afd, text=" 1. Agregar Estados ")
f_estados.pack(fill="x", padx=10, pady=5)

tk.Label(f_estados, text="Nombre:").grid(row=0, column=0, padx=5)
entry_estado_nombre = tk.Entry(f_estados, width=10)
entry_estado_nombre.grid(row=0, column=1, padx=5)

var_es_inicial = tk.BooleanVar()
tk.Checkbutton(f_estados, text="Inicial", variable=var_es_inicial).grid(row=0, column=2)

var_es_final = tk.BooleanVar()
tk.Checkbutton(f_estados, text="Final", variable=var_es_final).grid(row=0, column=3)

tk.Button(f_estados, text="Añadir", command=agregar_estado_interfaz).grid(row=0, column=4, padx=10)


f_trans = ttk.LabelFrame(tab_afd, text=" 2. Definir Transiciones ")
f_trans.pack(fill="x", padx=10, pady=5)

cb_desde = ttk.Combobox(f_trans, width=10, state="readonly")
cb_desde.grid(row=0, column=0, padx=5)
tk.Label(f_trans, text="--").grid(row=0, column=1)
entry_simbolo = tk.Entry(f_trans, width=5)
entry_simbolo.grid(row=0, column=2, padx=5)
tk.Label(f_trans, text="-->").grid(row=0, column=3)
cb_hacia = ttk.Combobox(f_trans, width=10, state="readonly")
cb_hacia.grid(row=0, column=4, padx=5)

tk.Button(f_trans, text="Asignar", command=agregar_transicion_interfaz).grid(row=0, column=5, padx=10)

#tablita
f_tabla = ttk.LabelFrame(tab_afd, text=" Tabla de Transiciones ")
f_tabla.pack(fill="both", expand=True, padx=10, pady=5)

tree_trans = ttk.Treeview(f_tabla, show="headings", height=8)
tree_trans.pack(fill="both", expand=True, padx=5, pady=5)

# Opcional: Agregar scrollbar si hay muchos estados
scrollbar_tabla = ttk.Scrollbar(f_tabla, orient="vertical", command=tree_trans.yview)
tree_trans.configure(yscrollcommand=scrollbar_tabla.set)
scrollbar_tabla.pack(side="right", fill="y") 

f_prueba = ttk.LabelFrame(tab_afd, text=" 3. Probar Cadena ")
f_prueba.pack(fill="x", padx=10, pady=5)

entry_probar = tk.Entry(f_prueba)
entry_probar.pack(side="left", padx=10, pady=5, expand=True, fill="x")
tk.Button(f_prueba, text="Validar", command=probar_cadena).pack(side="right", padx=10)

lbl_res_afd = tk.Label(tab_afd, text="", font=("Arial", 10, "bold"), bg="white")
lbl_res_afd.pack(pady=10)

text_reporte = scrolledtext.ScrolledText(tab_afd, height=15, width=80)
text_reporte.pack(pady=10, padx=10)

btn_cargar = tk.Button(f_acciones, text="Minimizar", command=ejecutar_minimizacion, bg="#cc9a2e", fg="white", width=12)
btn_cargar.pack(side="left", padx=5)

def update_validator_ui(event=None):
    selected = validator_type_var.get()
    # Obtenemos el patrón directamente de la clase lógica para no duplicar strings
    patterns = {
        "Correo electrónico": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "Número telefónico": r'^(\+\d{1,3}\s?)?(\d{2,3}[\s-]?)?\d{3,4}[\s-]?\d{3,4}$',
        "URL": r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$',
        "Fecha": r'^(\d{2}\/\d{2}\/\d{4})|(\d{4}-\d{2}-\d{2})$',
        "Contraseña": r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    }
    regex_pattern_var.set(patterns.get(selected, "Seleccione un tipo"))

def validate_with_regex():
    v_type = validator_type_var.get()
    input_text = validator_input_var.get()
    
    if not v_type or not input_text:
        messagebox.showerror("Error", "Seleccione tipo e ingrese texto")
        return
        
    validadores = {
        "Correo electrónico": exr.validate_email,
        "Número telefónico": exr.validate_phone,
        "URL": exr.validate_url,
        "Fecha": exr.validate_date,
        "Contraseña": exr.validate_password
    }

    is_valid, _ = validadores[v_type](input_text)
    
    res_text = "VÁLIDO" if is_valid else "INVALIDO"
    color = "#27ae60" if is_valid else "#c0392b"
    
    validation_regex_result_var.set(f"El texto ingresado es {res_text}")
    lbl_resultado_regex.config(fg=color)


# --- PESTAÑA 5: VALIDACIÓN REGEX ---
tab_regex = tk.Frame(notebook, bg="white")
notebook.add(tab_regex, text=" Validador Regex ")

validator_frame = ttk.LabelFrame(tab_regex, text=" Configuración de Validación ")
validator_frame.pack(fill="both", expand=True, padx=20, pady=20)

validator_type_var = tk.StringVar()
validator_input_var = tk.StringVar()
regex_pattern_var = tk.StringVar(value="Seleccione un tipo para ver el patrón")
validation_regex_result_var = tk.StringVar(value="Esperando validación...")

ttk.Label(validator_frame, text="Tipo de validación:", font=("Arial", 10, "bold")).pack(pady=10)
validator_types = ["Correo electrónico", "Número telefónico", "URL", "Fecha", "Contraseña"]
combobox_regex = ttk.Combobox(validator_frame, textvariable=validator_type_var, values=validator_types, state="readonly", width=30)
combobox_regex.pack(pady=5)
combobox_regex.bind("<<ComboboxSelected>>", update_validator_ui)

tk.Label(validator_frame, textvariable=regex_pattern_var, wraplength=500, fg="#7f8c8d", font=("Consolas", 9)).pack(pady=10)

f_entry = tk.Frame(validator_frame, bg="#f0f0f0")
f_entry.pack(pady=10, fill="x", padx=20)
tk.Label(f_entry, text="Texto a validar:", bg="#f0f0f0").pack(side="left", padx=5)
ttk.Entry(f_entry, textvariable=validator_input_var, width=40).pack(side="left", padx=5, expand=True, fill="x")
tk.Button(f_entry, text="Validar Ahora", command=validate_with_regex, bg="#3498db", fg="white", padx=10).pack(side="left", padx=5)

lbl_resultado_regex = tk.Label(validator_frame, textvariable=validation_regex_result_var, font=("Arial", 12, "bold"), bg="white")
lbl_resultado_regex.pack(pady=30)

tk.Button(validator_frame, text="Generar AFD Equivalente", state="disabled", bg="#95a5a6").pack(pady=10)

# --- PESTAÑA 6: CONVERTIR EN ER ---
tab_regex = tk.Frame(notebook, bg="white")
notebook.add(tab_regex, text=" Convertir a ER ")

f_control_er = tk.Frame(tab_regex, bg="white")
f_control_er.pack(fill="x", padx=10, pady=10)

btn_convertir_er = tk.Button(f_control_er, text="Convertir AFD a ER", 
                            command=lambda: ejecutar_conversion_er(), 
                            bg="#f39c12", fg="white", font=("Arial", 10, "bold"))
btn_convertir_er.pack(anchor="center")

txt_output_er = scrolledtext.ScrolledText(tab_regex, height=20, width=90, font=("Courier New", 10))
txt_output_er.pack(padx=15, pady=10, fill="both", expand=True)

lbl_er_final = tk.Label(tab_regex, text=": ", font=("Arial", 12, "bold"), bg="white")
lbl_er_final.pack(side="bottom", pady=20)

def ejecutar_conversion_er():
    if not mi_afd.states:
        messagebox.showwarning("Atención", "No hay un autómata cargado.")
        return

    reporte_texto, er_final = mi_afd.conversion_er_reporte()

    txt_output_er.config(state="normal")  # Habilitar para escribir
    txt_output_er.delete("1.0", tk.END)   # Limpiar contenido previo
    txt_output_er.insert(tk.END, reporte_texto) # Insertar el nuevo texto
    txt_output_er.config(state="disabled") # Bloquear para que el usuario no edite
    
    lbl_er_final.config(text=f"Expresion final es: {er_final}")

#------- PESTAÑA 7: GRAMÁTICAS ---

def cargar_gramatica_archivo():
    """Carga un archivo .jff y traslada las reglas al editor de texto manual."""
    ruta = filedialog.askopenfilename(
        title="Seleccionar JFLAP", 
        filetypes=(("Archivos JFLAP", "*.jff"), ("Todos", "*.*"))
    )
    if ruta:
        try:
            # Parsear el archivo usando el módulo externo
            dict_p = gramaticas.parse_jflap_grammar(ruta)
            
            # Limpiar editor y volcar las reglas cargadas
            txt_input_manual.delete("1.0", tk.END)
            for var, rules in dict_p.items():
                linea = f"{var} -> {' | '.join([r if r != '' else 'lambda' for r in rules])}\n"
                txt_input_manual.insert(tk.END, linea)
                
            messagebox.showinfo("Éxito", "Gramática cargada en el editor manual.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")

def procesar_gramatica_total(tipo):
    """Lee el texto del editor y realiza la conversión solicitada (CNF o GNF)."""
    contenido = txt_input_manual.get("1.0", tk.END).strip()
    if not contenido:
        messagebox.showwarning("Atención", "Escribe o carga una gramática primero.")
        return

    try:
        # 1. Parsear el texto manual a un diccionario de Python
        dict_manual = {}
        for linea in contenido.split("\n"):
            if "->" in linea:
                izq, der = linea.split("->")
                var = izq.strip()
                # Separar opciones por pipe '|' y manejar el símbolo lambda
                opts = {o.strip() for o in der.split("|")}
                opts = {"" if o.lower() in ["lambda", "l", "λ"] else o for o in opts}
                
                if var not in dict_manual:
                    dict_manual[var] = set()
                dict_manual[var].update(opts)

        # 2. Crear instancia de la clase Grammar
        g = gramaticas.Grammar(dict_manual)
        
        if tipo == "CNF":
            txt_output_cnf.config(state="normal")
            txt_output_cnf.delete("1.0", tk.END)
            
            # Proceso paso a paso para el reporte
            res = "--- PROCESO DE SIMPLIFICACIÓN (CNF) ---\n"
            g.remove_lambda(); res += f"1. Eliminar producciones Λ:\n{g}\n\n"
            g.remove_unit_productions(); res += f"2. Eliminar producciones unitarias:\n{g}\n\n"
            g.remove_useless_symbols(); res += f"3. Eliminar símbolos inútiles:\n{g}\n\n"
            g.to_cnf(); res += f"--- RESULTADO FINAL FNC ---\n{g}"
            
            txt_output_cnf.insert(tk.END, res)
            txt_output_cnf.config(state="disabled")
            messagebox.showinfo("FNC", "Conversión a Chomsky finalizada.")
        
        elif tipo == "GNF":
            txt_output_gnf.config(state="normal")
            txt_output_gnf.delete("1.0", tk.END)
            
            # GNF requiere limpieza previa y pasar por CNF
            g.remove_lambda()
            g.remove_unit_productions()
            g.remove_useless_symbols()
            g.to_cnf()
            g.to_gnf() 
            
            res_gnf = f"--- RESULTADO FINAL FNG ---\n{g}"
            txt_output_gnf.insert(tk.END, res_gnf)
            txt_output_gnf.config(state="disabled")
            messagebox.showinfo("FNG", "Conversión a Greibach finalizada.")

    except Exception as e:
        messagebox.showerror("Error", f"Error en el procesamiento: {str(e)}")
# --- PESTAÑA 7: GRAMÁTICAS ---
tab_gramaticas = tk.Frame(notebook, bg="#f5f6fa")
notebook.add(tab_gramaticas, text=" Gramáticas (CNF/GNF) ")

# --- ÁREA DE ENTRADA (Editor) ---
f_input_top = ttk.LabelFrame(tab_gramaticas, text=" Editor de Gramática ")
f_input_top.pack(fill="x", padx=10, pady=5)

f_btns_input = tk.Frame(f_input_top)
f_btns_input.pack(fill="x", padx=5, pady=5)

btn_cargar_gram = tk.Button(f_btns_input, text="Cargar JFLAP (.jff)", 
                            command=cargar_gramatica_archivo, 
                            bg="#3498db", fg="white", font=("Arial", 9, "bold"))
btn_cargar_gram.pack(side="left", padx=5)

tk.Label(f_input_top, text="Edita tus reglas aquí (Formato: Variable -> Derivación1 | Derivación2):", 
         font=("Arial", 9, "italic")).pack(anchor="w", padx=10)

txt_input_manual = tk.Text(f_input_top, height=6, font=("Consolas", 10))
txt_input_manual.pack(fill="x", padx=10, pady=5)
txt_input_manual.insert("1.0", "S -> aA | b\nA -> aA | lambda") 

# --- PANEL DE RESULTADOS DUAL ---
f_resultados_dual = tk.Frame(tab_gramaticas)
f_resultados_dual.pack(fill="both", expand=True, padx=10, pady=5)

f_cnf = ttk.LabelFrame(f_resultados_dual, text=" Forma Normal de Chomsky (FNC) ")
f_cnf.pack(side="left", fill="both", expand=True, padx=5)

btn_proc_cnf = tk.Button(f_cnf, text="Convertir a FNC", 
                         command=lambda: procesar_gramatica_total("CNF"), 
                         bg="#27ae60", fg="white", font=("Arial", 9, "bold"))
btn_proc_cnf.pack(pady=5)

txt_output_cnf = scrolledtext.ScrolledText(f_cnf, font=("Courier New", 10), bg="#eef9f1", state="disabled")
txt_output_cnf.pack(fill="both", expand=True, padx=5, pady=5)

f_gnf = ttk.LabelFrame(f_resultados_dual, text=" Forma Normal de Greibach (FNG) ")
f_gnf.pack(side="left", fill="both", expand=True, padx=5)

btn_proc_gnf = tk.Button(f_gnf, text="Convertir a FNG", 
                         command=lambda: procesar_gramatica_total("GNF"), 
                         bg="#8e44ad", fg="white", font=("Arial", 9, "bold"))
btn_proc_gnf.pack(pady=5)

txt_output_gnf = scrolledtext.ScrolledText(f_gnf, font=("Courier New", 10), bg="#f4eef9", state="disabled")
txt_output_gnf.pack(fill="both", expand=True, padx=5, pady=5)



root.mainloop()