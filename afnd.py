import json
import xml.etree.ElementTree as ET

class State:
    def __init__(self, name, is_initial=False, is_final=False):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final

    def __repr__(self):
        return self.name

class AFN:
    def __init__(self):
        self.states = []
        self.alphabet = set()
        self.transitions = {} # (estado, simbolo) -> [lista de estados]
        self.initial_state = None
        self.final_states = []

    def get_state_by_name(self, name):
        for state in self.states:
            if state.name == name:
                return state
        return None

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

    def add_transition(self, from_name, symbol, to_name):
        from_s = self.get_state_by_name(from_name)
        to_s = self.get_state_by_name(to_name)
        
        if from_s and to_s:
            key = (from_s, symbol)
            if key not in self.transitions:
                self.transitions[key] = []
            self.transitions[key].append(to_s)
            if symbol != '': 
                self.alphabet.add(symbol)
            return True
        return False
    
    # IMPORTANTE: Este método DEBE estar indentado dentro de la clase AFN
    def validate_string_afn(self, input_string):
        if not self.initial_state:
            return False, [{"paso": 0, "estados": [], "leer": "Error", "info": "No hay estado inicial"}]

        # Empezamos con un conjunto de estados actuales
        current_states = {self.initial_state}
        steps = []
        
        steps.append({
            "paso": 0,
            "estados": [s.name for s in current_states],
            "leer": "Inicio",
            "info": f"Iniciando en: {[s.name for s in current_states]}"
        })

        for i, symbol in enumerate(input_string):
            next_states = set()
            detalles = []
            
            for s in current_states:
                destinos = self.transitions.get((s, symbol), [])
                for d in destinos:
                    next_states.add(d)
                    detalles.append(f"δ({s.name}, {symbol}) -> {d.name}")
            
            # Si no hay a dónde ir, el camino muere
            if not next_states:
                steps.append({
                    "paso": i + 1,
                    "estados": ["Ø"],
                    "leer": symbol,
                    "info": "Bloqueo: No hay transiciones posibles."
                })
                return False, steps

            current_states = next_states
            steps.append({
                "paso": i + 1,
                "estados": [s.name for s in current_states],
                "leer": symbol,
                "info": " | ".join(detalles)
            })

        # Es válido si AL MENOS UNO de los estados en los que terminamos es final
        valido = any(s in self.final_states for s in current_states)
        return valido, steps