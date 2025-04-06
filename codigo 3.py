import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from PIL import Image, ImageTk

# Colores y estilo mejorados
BG_COLOR = "#2C3E50"
FG_COLOR = "#ECF0F1"
BTN_COLOR = "#3498DB"
BTN_ACTIVE_COLOR = "#2980B9"
FONT_TITLE = ("Helvetica", 18, "bold")
FONT_LABEL = ("Helvetica", 12)
FONT_BUTTON = ("Helvetica", 12, "bold")

# Variable global para el gráfico
canvas = None

def biseccion(funcion, a, b, tol=1e-6, max_iter=100):
    x = sp.symbols('x')
    f = sp.lambdify(x, funcion)
    
    if f(a) * f(b) >= 0:
        return None, 0, []
    
    iteraciones = 0
    datos_iteracion = []
    
    while (b - a) / 2 > tol and iteraciones < max_iter:
        c = (a + b) / 2
        fc = f(c)
        datos_iteracion.append((iteraciones, a, b, c, fc))
        
        if fc == 0:
            return c, iteraciones, datos_iteracion
        elif f(a) * fc < 0:
            b = c
        else:
            a = c
        
        iteraciones += 1
    
    return (a + b) / 2, iteraciones, datos_iteracion

def secante(funcion, x0, x1, tol=1e-6, max_iter=100):
    x = sp.symbols('x')
    f = sp.lambdify(x, funcion)
    
    iteraciones = 0
    datos_iteracion = []
    
    while abs(x1 - x0) > tol and iteraciones < max_iter:
        fx0 = f(x0)
        fx1 = f(x1)
        x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        datos_iteracion.append((iteraciones, x0, x1, x2, f(x2)))
        x0, x1 = x1, x2
        iteraciones += 1
    
    return x1, iteraciones, datos_iteracion

def newton_raphson(funcion, x0, tol=1e-6, max_iter=100):
    x = sp.symbols('x')
    f = sp.lambdify(x, funcion)
    df = sp.lambdify(x, sp.diff(funcion, x))
    
    iteraciones = 0
    datos_iteracion = []
    
    while abs(f(x0)) > tol and iteraciones < max_iter:
        x1 = x0 - f(x0) / df(x0)
        datos_iteracion.append((iteraciones, x0, None, x1, f(x1)))
        x0 = x1
        iteraciones += 1
    
    return x0, iteraciones, datos_iteracion

def graficar(funcion, a, b, raiz=None):
    global canvas
    
    x_vals = np.linspace(a - 1, b + 1, 400)
    f = sp.lambdify(sp.symbols('x'), funcion, "numpy")
    y_vals = f(x_vals)
    
    fig, ax = plt.subplots(figsize=(5, 4)) # reducir el figsize
    ax.plot(x_vals, y_vals, label=f'f(x) = {funcion}', color='#FFC300')  # Amarillo dorado
    ax.set_facecolor("#1E1E1E")
    ax.grid(color='gray', linestyle='--', linewidth=0.5)
    ax.axhline(0, color='white', linewidth=1)
    ax.axvline(0, color='white', linewidth=1)
    
    if raiz is not None:
        ax.scatter(raiz, f(raiz), color='#FF5733', label=f'Raíz: {raiz:.6f}')  # Rojo anaranjado
    
    ax.legend(facecolor="#34495E", edgecolor="white", labelcolor="white")
    
    cursor = Cursor(ax, useblit=True, color='white', linewidth=1)
    
    if canvas:
        canvas.get_tk_widget().destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def calcular_raiz():
    try:
        funcion_str = entrada_funcion.get()
        metodo = metodo_var.get()
        
        x = sp.symbols('x')
        funcion = sp.sympify(funcion_str)
        
        if metodo == "Bisección":
            a = float(entrada_a.get())
            b = float(entrada_b.get())
            
            if a >= b:
                messagebox.showerror("Error", "El valor de 'a' debe ser menor que 'b'.")
                return
            
            raiz, iteraciones, datos_iteracion = biseccion(funcion, a, b)
            
        elif metodo == "Secante":
            x0 = float(entrada_a.get())
            x1 = float(entrada_b.get())
            
            raiz, iteraciones, datos_iteracion = secante(funcion, x0, x1)
            
        elif metodo == "Newton-Raphson":
            x0 = float(entrada_a.get())
            
            raiz, iteraciones, datos_iteracion = newton_raphson(funcion, x0)
            
        else:
            messagebox.showerror("Error", "Método no válido.")
            return
        
        for row in tabla.get_children():
            tabla.delete(row)
        
        if raiz is not None:
            messagebox.showinfo("Resultado", f"Raíz encontrada: {raiz:.6f}\nIteraciones: {iteraciones}")
            etiqueta_iteraciones.config(text=f"Iteraciones: {iteraciones}")
            for dato in datos_iteracion:
                tabla.insert("", "end", values=(dato[0], f"{dato[1]:.6f}", f"{dato[2]:.6f}" if dato[2] is not None else "N/A", f"{dato[3]:.6f}", f"{dato[4]:.6e}"))
            
            # Ajustar el gráfico según el método
            if metodo == "Newton-Raphson":
                graficar(funcion, raiz - 1, raiz + 1, raiz)
            else:
                graficar(funcion, float(entrada_a.get()), float(entrada_b.get()), raiz)
                
        else:
            messagebox.showerror("Error", "No se encontró raíz dentro de las iteraciones permitidas.")
            etiqueta_iteraciones.config(text="Iteraciones: N/A")
            
    except Exception as e:
        messagebox.showerror("Error", f"Entrada inválida: {e}")
# Crear interfaz mejorada
root = tk.Tk()
root.title("Calculadora de Raíces - Métodos Numéricos")
root.configure(bg=BG_COLOR)
root.geometry("800x600")

frame_principal = tk.Frame(root, bg=BG_COLOR)
frame_principal.pack(pady=20, padx=20, fill="both", expand=True)

# Imagen del logo
imagen = Image.open("LOGO.png")
imagen = imagen.resize((120, 120))
imagen_tk = ImageTk.PhotoImage(imagen)
label_imagen = tk.Label(frame_principal, image=imagen_tk, bg=BG_COLOR)
label_imagen.pack(pady=10)

# Título
titulo = tk.Label(frame_principal, text="Calculadora de Raíces", font=FONT_TITLE, fg=FG_COLOR, bg=BG_COLOR)
titulo.pack(pady=10)

frame_entrada = tk.Frame(frame_principal, bg=BG_COLOR)
frame_entrada.pack(pady=10, fill="x")

# Etiquetas y entradas
tk.Label(frame_entrada, text="Función f(x):", font=FONT_LABEL, fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="e")
entrada_funcion = tk.Entry(frame_entrada, width=40, font=FONT_LABEL)
entrada_funcion.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

tk.Label(frame_entrada, text="Intervalo [a, b] / Valor inicial:", font=FONT_LABEL, fg=FG_COLOR, bg=BG_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="e")
entrada_a = tk.Entry(frame_entrada, width=10, font=FONT_LABEL)
entrada_a.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
entrada_b = tk.Entry(frame_entrada, width=10, font=FONT_LABEL)
entrada_b.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

# Menú desplegable
metodos = ["Bisección", "Secante", "Newton-Raphson"]
metodo_var = tk.StringVar(root)
metodo_var.set(metodos[0])
metodo_menu = tk.OptionMenu(frame_entrada, metodo_var, *metodos)
metodo_menu.config(bg=BTN_COLOR, fg=FG_COLOR, font=FONT_BUTTON, activebackground=BTN_ACTIVE_COLOR)
metodo_menu.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

# Botón calcular
boton_calcular = tk.Button(frame_entrada, text="Calcular Raíz", bg=BTN_COLOR, fg=FG_COLOR, font=FONT_BUTTON, activebackground=BTN_ACTIVE_COLOR, command=calcular_raiz)
boton_calcular.grid(row=2, column=2, pady=10, sticky="ew")

# Etiqueta iteraciones
etiqueta_iteraciones = tk.Label(frame_entrada, text="Iteraciones: ", font=FONT_LABEL, fg=FG_COLOR, bg=BG_COLOR)
etiqueta_iteraciones.grid(row=3, columnspan=3, pady=5, sticky="ew")

# Tabla
frame_tabla = tk.Frame(frame_principal, bg=BG_COLOR)
frame_tabla.pack(pady=10, fill="both", expand=True)

columnas = ("Iteración", "a/x0", "b/x1", "c/x2", "f(c/x2)")
estilo_tabla = ttk.Style()
estilo_tabla.configure("Treeview.Heading", background="#34495E", foreground=FG_COLOR, font=FONT_LABEL)
estilo_tabla.configure("Treeview", background="#2C3E50", foreground=FG_COLOR, font=FONT_LABEL)
estilo_tabla.map('Treeview', background=[('selected', '#3498DB')])

tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
for col in columnas:
    tabla.heading(col, text=col)
    if col == "Iteración":
        tabla.column(col, anchor="center", width=10)
    elif col == "f(c/x2)":
        tabla.column(col, anchor="center", width=10)
    else:
        tabla.column(col, anchor="center", width=10)
tabla.pack(fill="both", expand=True)

# Gráfico
frame_grafico = tk.Frame(frame_principal, bg=BG_COLOR)
frame_grafico.pack(pady=10, fill="both", expand=True)

# Leyenda
frame_info = tk.Frame(root, bg=BG_COLOR)
frame_info.pack(pady=10, fill="x", side="bottom")

informacion = "Braulio Gonzalez Tinoco\nMT4A\nINSTITUTO TECNOLOGICO DE TUXTLA GUTIERREZ"
etiqueta_info = tk.Label(frame_info, text=informacion, fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 10, "italic"))
etiqueta_info.pack()

root.mainloop()