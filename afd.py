import json
import xml.etree.ElementTree as ET
from graphviz import Digraph
class State:
    def __init__(self, name, is_initial=False, is_final=False):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final

    def __repr__(self):
        return self.name

class AFD:
    def __init__(self):
        self.states = []
        self.alphabet = set()
        self.initial_state = None
        self.final_states = []
        self.transitions = {}

    def add_state(self, name, is_initial=False, is_final=False):
        if any(s.name == name for s in self.states):
            return None
        new_state = State(name, is_initial, is_final)
        self.states.append(new_state)
        if is_initial:
            self.initial_state = new_state
        if is_final:
            self.final_states.append(new_state)
        return new_state

    def add_transition(self, from_state_name, symbol, to_state_name):
        from_s = self.get_state_by_name(from_state_name)
        to_s = self.get_state_by_name(to_state_name)
        
        if from_s and to_s:
            if symbol != '':
                self.alphabet.add(symbol)
            self.transitions[(from_s, symbol)] = to_s
            return True
        return False

    def get_state_by_name(self, name):
        for state in self.states:
            if state.name == name:
                return state
        return None

    def validate_string(self, input_string):
        if not self.initial_state:
            return False, "No hay estado inicial"

        current_state = self.initial_state
        path = [current_state.name]

        for symbol in input_string:
            if (current_state, symbol) not in self.transitions:
                return False, f"Bloqueado en {current_state.name} con '{symbol}'"
            current_state = self.transitions[(current_state, symbol)]
            path.append(current_state.name)

        es_valido = current_state in self.final_states
        return es_valido, " -> ".join(path)
 
    def minimizar_y_reportar(self):
        reporte = "=== PROCESO DE MINIMIZACIÓN ===\n\n"
        finales = [s.name for s in self.final_states]
        no_finales = [s.name for s in self.states if s not in self.final_states]
        grupos = []
        if no_finales: grupos.append(no_finales)
        if finales: grupos.append(finales)
        reporte += f"Paso 0: Partición inicial (Finales vs No Finales)\n"
        reporte += f"  Grupos: {grupos}\n\n"
        cambio = True
        paso = 1
        while cambio:
            nuevos_grupos = []
            cambio = False
            reporte += f"=== Refinamiento Paso {paso} ===\n"
            for grupo in grupos:
                if len(grupo) <= 1:
                    nuevos_grupos.append(grupo)
                    continue
                comportamiento = {}
                for s_name in grupo:
                    clave = []
                    for simbolo in sorted(list(self.alphabet)):
                        destino = self.transitions.get((self.get_state_by_name(s_name), simbolo))
                        if destino:
                            for idx, g in enumerate(grupos):
                                if destino.name in g:
                                    clave.append(idx)
                                    break
                                else:
                                    clave.append(-1) # No hay transición
                                    clave_tuple = tuple(clave)
                                    if clave_tuple not in comportamiento:
                                        comportamiento[clave_tuple] = []
                                        comportamiento[clave_tuple].append(s_name)
                                        if len(comportamiento) > 1:
                                            cambio = True
                                            for g_div in comportamiento.values():
                                                nuevos_grupos.append(g_div)
                                                reporte += f"  Estado(s) {g_div} forman nuevo subgrupo por transiciones idénticas.\n"

                                            else:
                                                nuevos_grupos.append(grupo)
                                                reporte += f"  Grupo {grupo} se mantiene estable.\n"
                                                grupos = nuevos_grupos
                                                reporte += f"  Partición actual: {grupos}\n\n"
                                                paso += 1
                                                if paso > 10: break
                                                reporte += "=== AFD MINIMIZADO ===\n"
                                                reporte += f"Estados finales combinados: {grupos}\n"
                                                return reporte

    def to_dict(self):
        return {
            "states": [{"name": s.name, "is_initial": s.is_initial, "is_final": s.is_final} for s in self.states],
            "transitions": [
                {"from": f.name, "symbol": s, "to": t.name} 
                for (f, s), t in self.transitions.items()
            ]
        }
    
    def conversion_er_reporte(self):
        if not self.initial_state or not self.final_states:
            return "Error: Falta estado inicial o final.", ""

        # 1. Diccionario inicial de transiciones
        er_trans = {}
        nombres_estados = [s.name for s in self.states]
        
        for u_n in nombres_estados:
            for v_n in nombres_estados:
                er_trans[(u_n, v_n)] = "∅"

        for (u, simb), v in self.transitions.items():
            etiqueta = simb if simb != "" else "λ"
            actual = er_trans[(u.name, v.name)]
            if actual == "∅":
                er_trans[(u.name, v.name)] = etiqueta
            else:
                er_trans[(u.name, v.name)] = f"({actual}+{etiqueta})"

        reporte = "=== AFD Original ===\n\n"
        reporte += f"Estados: {nombres_estados}\n"
        reporte += f"Estado inicial: {self.initial_state.name}\n"
        reporte += f"Estados finales: {[s.name for s in self.final_states]}\n\n"
        reporte += "Transiciones:\n"
        for (u, v), val in er_trans.items():
            if val != "∅":
                reporte += f"  {u} --{val}--> {v}\n"

        # 2. Eliminación de estados
        estados_elim = [s.name for s in self.states if not s.is_initial and not s.is_final]

        for q_elim in estados_elim:
            reporte += f"\n=== Eliminando estado {q_elim} ===\n"
            
            # Identificar Entrantes, Salientes y Bucle
            entrantes = [(u, val) for (u, v), val in er_trans.items() if v == q_elim and u != q_elim and val != "∅"]
            salientes = [(v, val) for (u, v), val in er_trans.items() if u == q_elim and v != q_elim and val != "∅"]
            bucle_val = er_trans.get((q_elim, q_elim), "∅")

            reporte += f"  Estados entrantes: {[f'{u} ({v})' for u, v in entrantes]}\n"
            reporte += f"  Estados salientes: {[f'{u} ({v})' for u, v in salientes]}\n"
            reporte += f"  Bucle en el estado: " + (f"({bucle_val})*" if bucle_val != "∅" else "No hay") + "\n"

            # Actualizar todos los caminos u -> v que pasan por q_elim
            for u in nombres_estados:
                if u == q_elim: continue
                for v in nombres_estados:
                    if v == q_elim: continue
                    
                    r_uq = er_trans[(u, q_elim)]
                    r_qv = er_trans[(q_elim, v)]
                    r_qq = er_trans[(q_elim, q_elim)]
                    r_uv = er_trans[(u, v)]

                    if r_uq != "∅" and r_qv != "∅":
                        star = f"({r_qq})*" if r_qq != "∅" else ""
                        nuevo_camino = f"{r_uq}{star}{r_qv}"
                        
                        if r_uv == "∅":
                            er_trans[(u, v)] = nuevo_camino
                        else:
                            er_trans[(u, v)] = f"({r_uv}+{nuevo_camino})"
            
            # Limpiar el estado eliminado
            for s in nombres_estados:
                er_trans.pop((s, q_elim), None)
                er_trans.pop((q_elim, s), None)

        # 3. Construcción del resultado finals
        q0 = self.initial_state.name
        resultados_finales = []
        
        for f_state in self.final_states:
            f = f_state.name
            # Si solo quedan inicial y final
            r_00 = er_trans.get((q0, q0), "∅")
            r_0f = er_trans.get((q0, f), "∅")
            r_ff = er_trans.get((f, f), "∅")
            r_f0 = er_trans.get((f, q0), "∅")

            if q0 == f:
                resultados_finales.append(f"({r_00})*")
            else:
                # Fórmula estándar para 2 estados: (r00 + r0f(rff)*rf0)* r0f(rff)*
                term_f = f"({r_ff})*" if r_ff != "∅" else ""
                if r_f0 == "∅":
                    prefix = f"({r_00})*" if r_00 != "∅" else ""
                    resultados_finales.append(f"{prefix}{r_0f}{term_f}")
                else:
                    # Caso completo
                    resultados_finales.append(f"({r_00}+{r_0f}{term_f}{r_f0})*{r_0f}{term_f}")

        expresion_final = "+".join(resultados_finales) if resultados_finales else "∅"
        # Limpieza básica de lambdas y vacíos en el string final
        expresion_final = expresion_final.replace("(∅)*", "").replace("∅+", "").replace("+∅", "")
        
        return reporte, expresion_final
    def generar_grafo(self, nombre_archivo="automata_vis"):
        dot = Digraph(comment='Autómata', format='png')
        dot.attr(rankdir='LR')  

        # Crear los estados
        for s in self.states:
            shape = 'doublecircle' if s.is_final else 'circle'
            color = 'gold' if s.is_initial else 'white'
            dot.node(s.name, s.name, shape=shape, style='filled', fillcolor=color)

        # Crear un nodo invisible para la flecha de inicio
        dot.node('', '', shape='none', width='0')
        dot.edge('', self.initial_state.name)

        # Añadir transiciones
        for (u, simb), v in self.transitions.items():
            label = simb if simb != "" else "λ"
            dot.edge(u.name, v.name, label=label)

        # Guardar y renderizar
        dot.render(nombre_archivo, view=False)
        return f"{nombre_archivo}.png"
    
    @classmethod
    def from_dict(cls, data):
        nuevo_afd = cls()
        for s in data["states"]:
            nuevo_afd.add_state(s["name"], s["is_initial"], s["is_final"])
        for t in data["transitions"]:
            nuevo_afd.add_transition(t["from"], t["symbol"], t["to"])
        return nuevo_afd

    @classmethod
    def from_jff_format(cls, jff_content):
        afd = cls()
        root = ET.fromstring(jff_content)
        id_to_state = {}
        for state_elem in root.findall(".//state"):
            s_id = state_elem.get("id")
            s_name = state_elem.get("name", f"q{s_id}")
            is_initial = state_elem.find("initial") is not None
            is_final = state_elem.find("final") is not None
            nuevo_estado = afd.add_state(s_name, is_initial, is_final)
            id_to_state[s_id] = nuevo_estado

        for trans_elem in root.findall(".//transition"):
            from_id = trans_elem.find("from").text
            to_id = trans_elem.find("to").text
            read_elem = trans_elem.find("read")
            symbol = read_elem.text if read_elem is not None and read_elem.text else ""
            from_state = id_to_state.get(from_id)
            to_state = id_to_state.get(to_id)
            if from_state and to_state:
                afd.add_transition(from_state.name, symbol, to_state.name)
        return afd

    def obtener_estados_accesibles(self):
        if not self.initial_state:
            return set()
        accesibles = set()
        pila = [self.initial_state]
        accesibles.add(self.initial_state)
        
        while pila:
            actual = pila.pop()
            for (estado_origen, simbolo), estado_destino in self.transitions.items():
                if estado_origen == actual and estado_destino not in accesibles:
                    accesibles.add(estado_destino)
                    pila.append(estado_destino)
        return accesibles

    def minimizar_y_reportar(self):
        reporte = "=== PROCESO DE MINIMIZACIÓN ===\n"
        
        # 1. Eliminar inaccesibles
        accesibles = self.obtener_estados_accesibles()
        inaccesibles = [s.name for s in self.states if s not in accesibles]
        reporte += f"1. Estados Inaccesibles eliminados: {inaccesibles if inaccesibles else 'Ninguno'}\n"
        
        estados_limpios = list(accesibles)
        nombres_limpios = [s.name for s in estados_limpios]
        
        # 2. Partición Inicial (Finales vs No Finales)
        finales = sorted([s.name for s in estados_limpios if s.is_final])
        no_finales = sorted([s.name for s in estados_limpios if s not in self.final_states])
        
        grupos = []
        if no_finales: grupos.append(tuple(no_finales))
        if finales: grupos.append(tuple(finales))
        
        reporte += f"2. Partición inicial (Clases de equivalencia):\n   G1 (No Finales): {no_finales}\n   G2 (Finales): {finales}\n\n"

        # 3. Refinamiento de Clases
        iteracion = 1
        while True:
            nuevos_grupos = []
            for grupo in grupos:
                if len(grupo) <= 1:
                    nuevos_grupos.append(grupo)
                    continue
                
                # Mapa de comportamiento: (id_grupo_destino_simbolo1, id_grupo_destino_simbolo2...) -> [estados]
                divisiones = {}
                for s_name in grupo:
                    comportamiento = []
                    estado_obj = self.get_state_by_name(s_name)
                    for simb in sorted(list(self.alphabet)):
                        destino = self.transitions.get((estado_obj, simb))
                        # Encontrar a qué grupo pertenece el destino
                        encontrado = False
                        if destino:
                            for idx, g in enumerate(grupos):
                                if destino.name in g:
                                    comportamiento.append(idx)
                                    encontrado = True
                                    break
                        if not encontrado:
                            comportamiento.append(-1) # Estado de error / Muerto
                    
                    clave = tuple(comportamiento)
                    if clave not in divisiones:
                        divisiones[clave] = []
                    divisiones[clave].append(s_name)
                
                for g_dividido in divisiones.values():
                    nuevos_grupos.append(tuple(sorted(g_dividido)))
            
            nuevos_grupos = sorted(nuevos_grupos)
            if set(nuevos_grupos) == set(grupos):
                break
            grupos = nuevos_grupos
            reporte += f"Paso {iteracion} de refinamiento: {grupos}\n"
            iteracion += 1

        # 4. Construcción del AFD Mínimo
        reporte += f"\n3. AFD MINIMIZADO FINAL:\n"
        reporte += f"   - Grupos resultantes: {grupos}\n"
        reporte += f"   - Reducción de estados: {len(self.states)} -> {len(grupos)}\n"
        
        # Crear tabla de transiciones para el reporte
        reporte += "\nTabla de Transiciones del AFD Mínimo:\n"
        reporte += f"{'Estado (Grupo)':<20} | {'Símbolo':<10} | {'Destino (Grupo)':<20}\n"
        reporte += "-"*60 + "\n"
        
        for g in grupos:
            rep_estado = self.get_state_by_name(g[0])
            nombre_grupo = "{" + ",".join(g) + "}"
            for simb in sorted(list(self.alphabet)):
                destino = self.transitions.get((rep_estado, simb))
                if destino:
                    # Buscar a qué grupo pertenece el destino
                    nombre_destino_grupo = "Error"
                    for g_dest in grupos:
                        if destino.name in g_dest:
                            nombre_destino_grupo = "{" + ",".join(g_dest) + "}"
                            break
                    reporte += f"{nombre_grupo:<20} | {simb:<10} | {nombre_destino_grupo:<20}\n"
        
        return reporte