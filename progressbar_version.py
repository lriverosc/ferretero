import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading

# Conexión a la base de datos
def conectar():
    return sqlite3.connect('inventario.db')

# Crear la tabla en la base de datos
def crear_base_datos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                      codigo INTEGER PRIMARY KEY,
                      nombre TEXT NOT NULL,
                      descripcion TEXT,
                      precio INTEGER NOT NULL,
                      cantidad INTEGER NOT NULL,
                      categoria TEXT
                  )''')
    
    # Insertar productos de ejemplo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos = [
            (1, "Martillo", "Martillo de acero", 5000, 20, "Herramientas"),
            (2, "Taladro", "Taladro de 500W", 15000, 15, "Herramientas"),
            (3, "Clavos", "Caja de 100 clavos", 2000, 50, "Materiales"),
            (4, "Pintura", "Galón de pintura blanca", 10000, 10, "Pinturas"),
            (5, "Tornillos", "Paquete de tornillos", 500, 100, "Materiales"),
            (6, "Lija", "Lija fina", 300, 30, "Herramientas"),
            (7, "Sierra", "Sierra manual", 7000, 8, "Herramientas"),
            (8, "Cemento", "Bolsa de cemento 50kg", 12000, 5, "Materiales")
        ]
        cursor.executemany("INSERT INTO productos (codigo, nombre, descripcion, precio, cantidad, categoria) VALUES (?, ?, ?, ?, ?, ?)", productos)
    
    conn.commit()
    conn.close()

# Funciones CRUD
def agregar_producto(codigo, nombre, descripcion, precio, cantidad, categoria):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (codigo, nombre, descripcion, precio, cantidad, categoria) VALUES (?, ?, ?, ?, ?, ?)",
                   (codigo, nombre, descripcion, precio, cantidad, categoria))
    conn.commit()
    conn.close()
    mostrar_productos()
    messagebox.showinfo("Éxito", "Producto agregado exitosamente")

def editar_producto(codigo_producto, nombre, descripcion, precio, cantidad, categoria):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET nombre=?, descripcion=?, precio=?, cantidad=?, categoria=? WHERE codigo=?",
                   (nombre, descripcion, precio, cantidad, categoria, codigo_producto))
    conn.commit()
    conn.close()
    mostrar_productos()
    messagebox.showinfo("Éxito", "Producto actualizado exitosamente")

def eliminar_producto(codigo_producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE codigo=?", (codigo_producto,))
    conn.commit()
    conn.close()
    mostrar_productos()
    messagebox.showinfo("Éxito", "Producto eliminado exitosamente")

def buscar_producto(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + nombre + '%',))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def obtener_productos_bajo_stock():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE cantidad <= 10")
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# Función para centrar ventanas
def centrar_ventana(ventana, ancho, alto):
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# Interfaz gráfica
def mostrar_productos():
    for item in tree.get_children():
        tree.delete(item)
    productos = obtener_productos()
    for producto in productos:
        tree.insert("", "end", values=producto)

def agregar_producto_gui():
    agregar_producto(len(obtener_productos()) + 1, entry_nombre.get(), entry_descripcion.get(), int(entry_precio.get()), int(entry_cantidad.get()), entry_categoria.get())
    limpiar_campos()

def editar_producto_gui():
    selected = tree.focus()
    if selected:
        codigo_producto = tree.item(selected, 'values')[0]
        editar_producto(codigo_producto, entry_nombre.get(), entry_descripcion.get(), int(entry_precio.get()), int(entry_cantidad.get()), entry_categoria.get())
        limpiar_campos()
    else:
        messagebox.showwarning("Advertencia", "Selecciona un producto para editar")

def eliminar_producto_gui():
    selected = tree.focus()
    if selected:
        codigo_producto = tree.item(selected, 'values')[0]
        eliminar_producto(codigo_producto)
    else:
        messagebox.showwarning("Advertencia", "Selecciona un producto para eliminar")

def buscar_producto_gui():
    nombre = entry_buscar.get()
    resultados = buscar_producto(nombre)
    for item in tree.get_children():
        tree.delete(item)
    for producto in resultados:
        tree.insert("", "end", values=producto)

def revisar_existencias():
    # Crear una ventana de progreso
    progreso = tk.Toplevel(root)
    progreso.title("Buscando...")
    centrar_ventana(progreso, 300, 100)  # Centrar ventana de progreso
    tk.Label(progreso, text="Buscando existencias...", font=('Arial', 12)).pack(pady=10)
    
    # Barra de progreso
    barra = ttk.Progressbar(progreso, orient="horizontal", length=250, mode="indeterminate")
    barra.pack(pady=10)
    barra.start()
    
    # Usar un hilo separado para buscar productos bajo stock
    threading.Thread(target=buscar_y_mostrar_productos_bajo_stock, args=(barra, progreso)).start()

def buscar_y_mostrar_productos_bajo_stock(barra, progreso):
    # Simular tiempo de búsqueda
    time.sleep(5)  # Simular búsqueda de 5 segundos
    productos_bajo_stock = obtener_productos_bajo_stock()
    barra.stop()
    progreso.destroy()  # Cerrar ventana de progreso

    # Mostrar resultados en la interfaz principal
    mostrar_resultados_productos_bajo_stock(productos_bajo_stock)

def mostrar_resultados_productos_bajo_stock(productos_bajo_stock):
    # Mostrar resultados
    if productos_bajo_stock:
        ventana_productos_bajo_stock = tk.Toplevel(root)
        ventana_productos_bajo_stock.title("Productos con Bajo Stock")
        centrar_ventana(ventana_productos_bajo_stock, 1258, 431)  # Centrar ventana de productos bajo stock
        
        tree_bajo_stock = ttk.Treeview(ventana_productos_bajo_stock, columns=columns, show='headings')
        for col in columns:
            tree_bajo_stock.heading(col, text=col)
        tree_bajo_stock.pack(fill="both", expand=True)

        for producto in productos_bajo_stock:
            tree_bajo_stock.insert("", "end", values=producto)

        tk.Label(ventana_productos_bajo_stock, text="Productos con 10 o menos unidades", font=('Arial', 12)).pack(pady=10)
    else:
        messagebox.showinfo("Información", "Todos los productos están en stock.")

def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_descripcion.delete(0, tk.END)
    entry_precio.delete(0, tk.END)
    entry_cantidad.delete(0, tk.END)
    entry_categoria.delete(0, tk.END)

# Función para mostrar alerta al inicio
def mostrar_alerta_bajo_stock():
    productos_bajo_stock = obtener_productos_bajo_stock()
    if productos_bajo_stock:
        messagebox.showwarning("¡Atención!", "Productos en baja de stock")

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Gestión de Inventario para Ferretería")
root.geometry("1281x632")  # Tamaño de la ventana
root.configure(bg="#F0F4F8")  # Color de fondo

# Crear la tabla de productos
columns = ("Código", "Nombre", "Descripción", "Precio (CLP)", "Cantidad", "Categoría")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("#0", text="")  # Ocultar columna 0
for col in columns:
    tree.heading(col, text=col)
tree.pack(fill="both", expand=True)

# Crear frame de control
frame_control = tk.Frame(root, bg="#F0F4F8")
frame_control.pack(pady=10)

# Campos de entrada
tk.Label(frame_control, text="Nombre", bg="#F0F4F8").grid(row=0, column=0)
entry_nombre = tk.Entry(frame_control)
entry_nombre.grid(row=0, column=1)

tk.Label(frame_control, text="Descripción", bg="#F0F4F8").grid(row=0, column=2)
entry_descripcion = tk.Entry(frame_control)
entry_descripcion.grid(row=0, column=3)

tk.Label(frame_control, text="Precio", bg="#F0F4F8").grid(row=1, column=0)
entry_precio = tk.Entry(frame_control)
entry_precio.grid(row=1, column=1)

tk.Label(frame_control, text="Cantidad", bg="#F0F4F8").grid(row=1, column=2)
entry_cantidad = tk.Entry(frame_control)
entry_cantidad.grid(row=1, column=3)

tk.Label(frame_control, text="Categoría", bg="#F0F4F8").grid(row=2, column=0)
entry_categoria = tk.Entry(frame_control)
entry_categoria.grid(row=2, column=1)

# Botones
tk.Button(frame_control, text="Agregar", command=agregar_producto_gui).grid(row=2, column=2)
tk.Button(frame_control, text="Editar", command=editar_producto_gui).grid(row=2, column=3)
tk.Button(frame_control, text="Eliminar", command=eliminar_producto_gui).grid(row=1, column=4)
tk.Button(frame_control, text="Buscar", command=buscar_producto_gui).grid(row=0, column=4)
tk.Button(frame_control, text="Revisar Existencias", command=revisar_existencias).grid(row=0, column=5)

# Campo de búsqueda
tk.Label(frame_control, text="Buscar Producto", bg="#F0F4F8").grid(row=1, column=5)
entry_buscar = tk.Entry(frame_control)
entry_buscar.grid(row=1, column=6)

# Crear la base de datos
crear_base_datos()
# Mostrar productos al inicio
mostrar_productos()
# Mostrar alerta si hay productos en bajo stock
mostrar_alerta_bajo_stock()

# Ejecutar la aplicación
root.mainloop()
