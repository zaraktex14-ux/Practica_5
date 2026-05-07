#Práctica 5 — Transformación de Gramáticas y Visualización de Autómatas


Esta práctica implementa la transformación de Gramáticas Independientes del Contexto (GIC) a:

- Forma Normal de Chomsky (FNC)
- Forma Normal de Greibach (FNG)

Es software interactivo desarrollado en prácticas anteriores para permitir la:

- visualización gráfica de autómatas
- simulación interactiva
- análisis visual de recorridos y transiciones

---

## Parte 1 — Transformación de Gramáticas

- Ingresar gramáticas independientes del contexto en JFLAP
- Transformar gramáticas a:
  - Forma Normal de Chomsky
  - Forma Normal de Greibach
- Verificar el funcionamiento de las gramáticas transformadas

---

## Parte 2 — Visualización de Autómatas

- Integrar visualización gráfica de autómatas
- Simular recorridos de cadenas
- Mostrar transiciones y estados activos
- Permitir carga y análisis de autómatas

---

##  Interfaz Gráfica

La aplicación cuenta con una interfaz intuitiva desarrollada en:

- Tkinter

Funciones principales:

- Creación de estados
- Definición de transiciones
- Selección de estado inicial
- Selección de estados finales
- Visualización automática del autómata

---

## Simulación de Autómatas

El sistema permite:

- Simulación paso a paso
- Validación de cadenas
- Visualización de recorridos
- Seguimiento de estados

Durante la simulación se muestra:

- Estado actual
- Símbolo leído
- Transición aplicada
- Cadena restante
- Resultado final

---

## Visualización Gráfica

La aplicación integra Graphviz para:

- Dibujar automáticamente los autómatas
- Mostrar estados y transiciones
- Resaltar estados finales
- Visualizar recorridos de simulación

---

# Transformación de Gramáticas

## Forma Normal de Chomsky (FNC)

La aplicación permite:

- eliminación de producciones λ
- eliminación de producciones unitarias
- simplificación de producciones
- conversión a reglas binarias

---

## Forma Normal de Greibach (FNG)

Se implementan transformaciones para:

- iniciar producciones con terminales
- reorganizar variables
- validar derivaciones

---


# Instalación

## Requisitos

- Python 3.8 o superior
- JFLAP

---

## Instalar dependencias

```bash
pip install graphviz
```bash
pip install customtkinter networkx matplotlib
