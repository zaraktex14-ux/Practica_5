# herramientas.py

def obtener_subcadenas(cadena):
    """Calcula prefijos, sufijos y subcadenas de un texto."""
    prefijos = [cadena[:i] for i in range(len(cadena) + 1)]
    sufijos = [cadena[i:] for i in range(len(cadena) + 1)]
    subcadenas = set()
    for i in range(len(cadena)):
        for j in range(i + 1, len(cadena) + 1):
            subcadenas.add(cadena[i:j])
    
    # Agregamos la cadena vacía a las subcadenas
    subcadenas.add("λ (vaca)") 
    return prefijos, sufijos, sorted(list(subcadenas))

def generar_strings_recursivo(alfabeto, actual, longitud, resultado):
    """Función auxiliar recursiva para Kleene."""
    if longitud == 0:
        resultado.append(actual)
        return
    for char in alfabeto:
        generar_strings_recursivo(alfabeto, actual + char, longitud - 1, resultado)

def calcular_kleene_logic(alfabeto_input, max_length):
    """Lógica pura para calcular Kleene Star y Plus."""
    # Limpiar el alfabeto (quitar espacios y duplicados)
    alfabeto = sorted(list(set(alfabeto_input.replace(" ", ""))))
    
    kleene_star = ["λ"] # Representación de cadena vacía
    for length in range(1, max_length + 1):
        generar_strings_recursivo(alfabeto, "", length, kleene_star)
    
    kleene_plus = [s for s in kleene_star if s != "λ"]
    return kleene_star, kleene_plus

# Añade esto a herramientas.py

def obtener_analisis_cadena(cadena):
    """Calcula prefijos, sufijos y subcadenas."""
    if not cadena:
        return [], [], []

    # Prefijos: desde el inicio hasta cada posición
    prefijos = [cadena[:i] for i in range(len(cadena) + 1)]
    
    # Sufijos: desde cada posición hasta el final
    sufijos = [cadena[i:] for i in range(len(cadena) + 1)]
    
    # Subcadenas: todas las combinaciones posibles
    subcadenas = set()
    for i in range(len(cadena)):
        for j in range(i + 1, len(cadena) + 1):
            subcadenas.add(cadena[i:j])
    
    # En teoría de la computación, la cadena vacía (λ) siempre es subcadena, prefijo y sufijo
    return prefijos, sufijos, sorted(list(subcadenas), key=len)