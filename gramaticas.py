import xml.etree.ElementTree as ET

def parse_jflap_grammar(file_path):
    """Lee un archivo .jff y devuelve un diccionario de producciones."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        productions = {}
        # JFLAP guarda las gramáticas en la etiqueta <structure> tipo 'grammar'
        for prod in root.findall(".//production"):
            lhs_node = prod.find("left")
            rhs_node = prod.find("right")
            
            lhs = lhs_node.text if lhs_node is not None and lhs_node.text else ""
            rhs = rhs_node.text if rhs_node is not None and rhs_node.text else ""
            
            if lhs not in productions:
                productions[lhs] = set()
            productions[lhs].add(rhs) # Si rhs es "", se interpreta como lambda
            
        return productions
    except Exception as e:
        raise Exception(f"Error al leer el archivo JFLAP: {str(e)}")

class Grammar:
    def __init__(self, productions):
        self.productions = {k: set(v) for k, v in productions.items()}
        self.variables = set(self.productions.keys())

    def __str__(self):
        lineas = []
        for var in sorted(self.productions.keys()):
            reglas = " | ".join([r if r != "" else "λ" for r in self.productions[var]])
            lineas.append(f"  {var} -> {reglas}")
        return "\n".join(lineas)

    def remove_lambda(self):
        nullable = {v for v, rules in self.productions.items() if "" in rules}
        for v in self.productions:
            self.productions[v].discard("")
            
        new_prods = {v: set(rules) for v, rules in self.productions.items()}
        for var, rules in self.productions.items():
            for rule in rules:
                for n in nullable:
                    if n in rule:
                        new_r = rule.replace(n, "", 1)
                        if new_r or var == 'S': # Mantener si es S -> lambda
                            new_prods[var].add(new_r)
        self.productions = new_prods

    def remove_unit_productions(self):
        unit_exists = True
        while unit_exists:
            unit_exists = False
            for var in list(self.productions.keys()):
                for rule in list(self.productions[var]):
                    if len(rule) == 1 and rule.isupper():
                        unit_exists = True
                        self.productions[var].remove(rule)
                        if rule in self.productions:
                            self.productions[var].update(self.productions[rule])

    def get_generative_symbols(self):
        generative = set()
        changed = True
        while changed:
            changed = False
            for var, rules in self.productions.items():
                if var in generative: continue
                for rule in rules:
                    if all(not c.isupper() or c in generative for c in rule):
                        generative.add(var)
                        changed = True
                        break
        return generative

    def get_reachable_symbols(self):
        reachable = {'S'}
        queue = ['S']
        seen = {'S'}
        while queue:
            curr = queue.pop(0)
            if curr in self.productions:
                for rule in self.productions[curr]:
                    for c in rule:
                        if c.isupper() and c not in seen:
                            reachable.add(c); seen.add(c); queue.append(c)
        return reachable

    def remove_useless_symbols(self):
        gen = self.get_generative_symbols()
        self.productions = {v: {r for r in rs if all(not c.isupper() or c in gen for c in r)} 
                           for v, rs in self.productions.items() if v in gen}
        reach = self.get_reachable_symbols()
        self.productions = {v: rs for v, rs in self.productions.items() if v in reach}

    def to_cnf(self):
        # Implementación simplificada de Chomsky
        terminals_map = {}
        new_vars_count = 1
        cnf_prods = {}
        
        # Primero procesar terminales
        for var, rules in self.productions.items():
            cnf_prods[var] = set()
            for rule in rules:
                if len(rule) == 1:
                    cnf_prods[var].add(rule)
                else:
                    new_rule = []
                    for c in rule:
                        if not c.isupper():
                            if c not in terminals_map:
                                t_var = f"T{c}"
                                terminals_map[c] = t_var
                                cnf_prods[t_var] = {c}
                            new_rule.append(terminals_map[c])
                        else:
                            new_rule.append(c)
                    
                    while len(new_rule) > 2:
                        aux = f"X{new_vars_count}"
                        new_vars_count += 1
                        cnf_prods[aux] = {"".join(new_rule[:2])}
                        new_rule = [aux] + new_rule[2:]
                    cnf_prods[var].add("".join(new_rule))
        self.productions = cnf_prods

    def to_gnf(self):
        # Aquí iría tu lógica de Greibach (sustitución y eliminación de recursión izq)
        # Por ahora lo dejamos como marcador para que no truene el main
        pass

    def __str__(self):
        lineas = []
        # Intentamos que 'S' siempre salga primero para orden académico
        keys = sorted(self.productions.keys())
        if 'S' in keys:
            keys.insert(0, keys.pop(keys.index('S')))
            
        for var in keys:
            reglas = " | ".join([r if r != "" else "λ" for r in self.productions[var]])
            lineas.append(f"  {var} -> {reglas}")
        return "\n".join(lineas)