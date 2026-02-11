import tkinter.ttk as ttk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from CapaNegocio import claseSistema as sistema
from CapaNegocio import claseValidaciones as val
from Entidades.clasePersona import clasePersona
import pandas as pd


# Tema oscuro usando customtkinter :D
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

##Clase para la ventana
class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de IMC")
        self.geometry("980x540")
        self.resizable(False, False)
        self._restoring_selection = False
        self._closing = False
        self._after_id = None
        self.filtro_id = None
        self.construirMenu()
        self.construirFormulario()
        self.construirTabla()
        self.bind("<Escape>", self._on_escape)
        self.protocol("WM_DELETE_WINDOW", self.SalirTOTAL)
        self.refrescarTabla()
        
    def construirMenu(self):
        barra = ctk.CTkFrame(self, fg_color=("gray10"))
        barra.pack(fill="x")

        estilo_btn = {
            "height": 30,
            "fg_color": "transparent",
            "hover_color": "#1f2633",
            "text_color": "white",
        }

        ctk.CTkButton(barra, text="Configuración de sistema",
                      command=self.configuracionSistema, width=190, **estilo_btn).pack(side="left", padx=4, pady=6)
        ctk.CTkButton(barra, text="Guardar información en archivos",
                      command=self.guardarArchivos, width=210, **estilo_btn).pack(side="left", padx=4, pady=6)
        ctk.CTkButton(barra, text="Cargar desde respaldo",
                      command=self.cargarRespaldo, width=190, **estilo_btn).pack(side="left", padx=4, pady=6)
        ctk.CTkButton(barra, text="Salir",
                      command=self.SalirTOTAL, width=90, **estilo_btn).pack(side="right", padx=6, pady=6)
        
##Se contruyen los labels y los textbox
    def construirFormulario(self):
        marco = ctk.CTkFrame(self, fg_color=("gray12"))
        marco.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(marco, text="Tipo ID").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.tipo_var = ctk.StringVar(value="Nacional")
        ctk.CTkOptionMenu(
            marco,
            variable=self.tipo_var,
            values=["Nacional", "Residente", "Pasaporte"],
            width=140,
        ).grid(row=0, column=1, padx=5, pady=8)

        ctk.CTkLabel(marco, text="ID").grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.id_var = ctk.StringVar()
        self.id_entry = ctk.CTkEntry(marco, textvariable=self.id_var, width=160)
        self.id_entry.grid(row=0, column=3, padx=5, pady=8)

        ctk.CTkLabel(marco, text="Nombre").grid(row=0, column=4, padx=5, pady=8, sticky="e")
        self.nombre_var = ctk.StringVar()
        ctk.CTkEntry(marco, textvariable=self.nombre_var, width=190).grid(row=0, column=5, padx=5, pady=8)

        ctk.CTkLabel(marco, text="Edad").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.edad_var = ctk.StringVar()
        ctk.CTkEntry(marco, textvariable=self.edad_var, width=90).grid(row=1, column=1, padx=5, pady=8)

        ctk.CTkLabel(marco, text="Género").grid(row=1, column=2, padx=5, pady=8, sticky="e")
        self.genero_var = ctk.StringVar(value="Masculino")
        ctk.CTkOptionMenu(
            marco,
            variable=self.genero_var,
            values=["Masculino", "Femenino"],
            width=140,
        ).grid(row=1, column=3, padx=5, pady=8)

        ctk.CTkLabel(marco, text="Peso (kg)").grid(row=1, column=4, padx=5, pady=8, sticky="e")
        self.peso_var = ctk.StringVar()
        ctk.CTkEntry(marco, textvariable=self.peso_var, width=120).grid(row=1, column=5, padx=5, pady=8)

        ctk.CTkLabel(marco, text="Estatura (m)").grid(row=1, column=6, padx=5, pady=8, sticky="e")
        self.estatura_var = ctk.StringVar()
        ctk.CTkEntry(marco, textvariable=self.estatura_var, width=120).grid(row=1, column=7, padx=5, pady=8)

        self.msg_var = ctk.StringVar(value="")
        ctk.CTkLabel(marco, textvariable=self.msg_var, text_color="lightgreen").grid(
            row=2, column=0, columnspan=8, sticky="w", padx=5, pady=(4, 0)
        )

##Constructor de tabla
    def construirTabla(self):
        contenedor = ctk.CTkFrame(self, fg_color=("gray12"))
        contenedor.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columnas = ("id", "nombre", "edad", "genero", "peso", "estatura", "imc", "estado")
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=15)

        encabezados = [
            ("id", "ID", 130),
            ("nombre", "Nombre", 170),
            ("edad", "Edad", 60),
            ("genero", "Género", 90),
            ("peso", "Peso (kg)", 85),
            ("estatura", "Estatura (m)", 95),
            ("imc", "IMC", 70),
            ("estado", "Estado", 130),
        ]
        for col, texto, ancho in encabezados:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center")

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_y.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Barra inferior de acciones
        barra = ctk.CTkFrame(self, fg_color=("gray12"))
        barra.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(barra, text="Guardar", command=self.guardar, width=140).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(barra, text="Borrar seleccionado", command=self.borrar, width=170).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(barra, text="Filtrar por ID", command=self.filtrar, width=140).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(barra, text="Reportes", command=self.abrirReportes, width=140).pack(side="right", padx=6, pady=8)

        # Bind de seleccioon
        self.tabla.bind("<<TreeviewSelect>>", self._on_select)

#Funcion para boton guardar
    def guardar(self):
        seleccion = self.tabla.selection()
        id_editar = seleccion[0] if seleccion else None

        tipo = self.tipo_var.get()
        id_valor = self.id_var.get().strip()
        nombre = self.nombre_var.get().strip()
        edad_txt = self.edad_var.get().strip()
        genero = self.genero_var.get().strip()
        peso_txt = self.peso_var.get().strip()
        estatura_txt = self.estatura_var.get().strip()

        validaciones = [
            val.validarID(id_valor, tipo),
            val.validarNombre(nombre),
            val.validarEdad(edad_txt),
            val.validarGenero(genero),
            val.validarPeso(peso_txt),
            val.validarEstaturaMetros(estatura_txt),
        ]
        errores = [msg for msg in validaciones if msg]

        if errores:
            messagebox.showerror("Datos inválidos", "\n".join(errores))
            return

        edad = int(edad_txt)
        peso = float(peso_txt)
        estatura = float(estatura_txt)
        imc = round(sistema.calcularIMC(peso, estatura), 2)
        estado = sistema.estadoIMC(genero, edad, estatura, peso, genero, imc)

        persona = clasePersona(id_valor, nombre, edad, genero, peso, estatura, imc, estado)

        ##Editar existentes porID
        if id_editar:

            if not messagebox.askyesno("Confirmar edición", f"El usuario {id_valor} ya existe. ¿Desea modificarlo?"):
                return
            for i, p in enumerate(sistema.listaPersonas):
                if str(p.id) == str(id_editar):
                    sistema.listaPersonas[i] = persona
                    break
        else:
            # si el ID ya existe y no hay seleccion
            existe = next((p for p in sistema.listaPersonas if str(p.id) == str(id_valor)), None)
            if existe:
                if not messagebox.askyesno("Usuario existente", f"El usuario {id_valor} ya existe. ¿Desea modificarlo?"):
                    return
                for i, p in enumerate(sistema.listaPersonas):
                    if str(p.id) == str(id_valor):
                        sistema.listaPersonas[i] = persona
                        break
            else:
                sistema.listaPersonas.append(persona)

        self.limpiarFormulario()
        self.msg_var.set("Persona guardada.")
        self.refrescarTabla()

##Refresca la tabla
    def refrescarTabla(self):
        if self._closing:
            return
        seleccion_prev = self.tabla.selection()
        id_prev = seleccion_prev[0] if seleccion_prev else None

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        registros = sistema.listaPersonas
        if self.filtro_id:
            registros = [p for p in registros if str(p.id) == str(self.filtro_id)]

        for p in registros:
            iid = str(p.id)
            self.tabla.insert(
                "",
                "end",
                iid=iid,
                values=(
                    p.id,
                    p.nombre,
                    p.edad,
                    p.genero,
                    f"{p.peso:.1f}",
                    f"{p.estatura:.2f}",
                    f"{p.imcCalculado:.2f}",
                    p.estado,
                ),
            )
        if id_prev and id_prev in self.tabla.get_children():
            self._restoring_selection = True
            self.tabla.selection_set(id_prev)
            # libera el flag del evento de seleccion
            self.after_idle(self.limpiarSeleccion)
        if not self._closing and self.winfo_exists():
            self._after_id = self.after(1500, self.refrescarTabla)


    def limpiarFormulario(self):
        self.id_var.set("")
        self.nombre_var.set("")
        self.edad_var.set("")
        self.genero_var.set("")
        self.peso_var.set("")
        self.estatura_var.set("")
        self.tabla.selection_remove(self.tabla.selection())
        self.id_entry.configure(state="normal")

    def borrar(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Sin selección", "Seleccione un registro para borrar.")
            return
        item_id = seleccionado[0]
        id_borrar = item_id
        if not messagebox.askyesno("Confirmar eliminación", f"¿Eliminar al usuario {id_borrar}?"):
            return
        sistema.listaPersonas = [p for p in sistema.listaPersonas if str(p.id) != str(id_borrar)]
        self.tabla.delete(item_id)
        self.msg_var.set("Registro eliminado.")
        self.limpiarFormulario()

    def _on_select(self, _event):
        if self._restoring_selection:
            return
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        item_id = seleccion[0]
        valores = self.tabla.item(item_id, "values")
        if not valores:
            return
        self.id_var.set(valores[0])
        self.nombre_var.set(valores[1])
        self.edad_var.set(valores[2])
        self.genero_var.set(valores[3] if valores[3] else "Masculino")
        self.peso_var.set(valores[4])
        self.estatura_var.set(valores[5])
        # Bloquear ID en modo edición
        self.id_entry.configure(state="disabled")

    def _on_escape(self, _event=None):
        # limpiar filtro y formulario
        self.filtro_id = None
        self.msg_var.set("")
        self.limpiarFormulario()

    def SalirTOTAL(self):
        self._closing = True
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        self.cancelarTodosCallbacks()
        self.destroy()

##Cancela todos los callbacks asi logro evitar errores si se cierra y esta esperando
    def cancelarTodosCallbacks(self):
        try:
            pending = self.tk.splitlist(self.tk.call("after", "info"))
        except Exception:
            return
        for aid in pending:
            try:
                self.after_cancel(aid)
            except Exception:
                pass

    def filtrar(self):
        id_buscar = simpledialog.askstring("Filtrar por ID", "Ingrese el ID a buscar:", parent=self)
        if id_buscar is None or id_buscar.strip() == "":
            return
        self.filtro_id = id_buscar.strip()
        self.msg_var.set(f"Filtro activo: ID {self.filtro_id}")
        self.refrescarTabla()

    def abrirReportes(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Reportes")
        ventana.geometry("800x520")
        ventana.resizable(True, True)
        # traer al frente al abrir
        ventana.lift()
        ventana.focus_force()
        ventana.attributes("-topmost", True)
        ventana.after(200, lambda: ventana.attributes("-topmost", False))

        btns = ctk.CTkFrame(ventana, fg_color=("gray12"))
        btns.pack(fill="x", padx=10, pady=10)

        canvas_frame = ctk.CTkFrame(ventana, fg_color=("gray12"))
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def render(df: pd.DataFrame, titulo: str, label_col: str):
            for child in canvas_frame.winfo_children():
                child.destroy()
            if df is None or df.empty:
                ctk.CTkLabel(canvas_frame, text="Sin datos para mostrar").pack(pady=20)
                return
            fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
            ax.bar(df[label_col], df["imc_promedio"], color="#4f8cff")
            for i, row in df.iterrows():
                ax.text(i, row["imc_promedio"] + 0.05, f"n={row['cantidad']}", ha="center", va="bottom", fontsize=8)
            ax.set_ylabel("IMC promedio")
            ax.set_xlabel(label_col.replace("_", " ").title())
            ax.set_title(titulo)
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        ctk.CTkButton(btns, text="Categoría IMC", width=160,
                      command=lambda: render(sistema.reporteCategoriaIMC(), "Reporte por categoría IMC", "estado")).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(btns, text="Grupo de edades", width=160,
                      command=lambda: render(sistema.reporteGrupoEdad(), "Reporte por grupo de edades", "grupo_edad")).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(btns, text="Género", width=160,
                      command=lambda: render(sistema.reporte_por_genero(), "Reporte por género", "genero")).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(btns, text="Cerrar", width=120, command=ventana.destroy).pack(side="right", padx=6, pady=8)


    def limpiarSeleccion(self):
        self._restoring_selection = False

    # Acciones de menuu
    def configuracionSistema(self):
        self.abrirConfiguracionSistema()
    def guardarArchivos(self):
        messagebox.showinfo("Guardar información", "Guardar información en archivos (pendiente de implementación).")

    def cargarRespaldo(self):
        messagebox.showinfo("Cargar desde respaldo", "Cargar datos desde un respaldo (pendiente de implementación).")


    def abrirConfiguracionSistema(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Configuracion del sistema")
        ventana.geometry("400x320")
        ventana.resizable(True, False)
        # traer al frente al abrir
        ventana.lift()
        ventana.focus_force()
        ventana.attributes("-topmost", True)
        ventana.after(200, lambda: ventana.attributes("-topmost", False))

        btns = ctk.CTkFrame(ventana, fg_color=("gray12"))
        btns.pack(fill="x", padx=10, pady=10)

        canvas_frame = ctk.CTkFrame(ventana, fg_color=("gray12"))
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def render(df: pd.DataFrame, titulo: str, label_col: str):
            for child in canvas_frame.winfo_children():
                child.destroy()
            

            canvas = FigureCanvasTkAgg(master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        ctk.CTkButton(btns, text="Configuración de sistema",
                      command=self.configuracionSistema, width=190).pack(side="left", padx=4, pady=6)
        ctk.CTkButton(btns, text="Cerrar", width=120, command=ventana.destroy).pack(side="right", padx=6, pady=8)

if __name__ == "__main__":
    VentanaPrincipal().mainloop()
