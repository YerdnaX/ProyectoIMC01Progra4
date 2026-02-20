import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from datetime import date, datetime
import threading
from queue import Queue, Empty
import customtkinter as ctk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from CapaNegocio import claseSistema as sistema
from CapaNegocio import claseValidaciones as val
from Entidades.clasePersona import clasePersona
from Entidades.claseHiloIMC import HiloIMC
import pandas as pd


# Tema oscuro usando customtkinter :D
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

##Clase para la ventana principal 
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
        self._ventana_calc = None
        self.ruta_label_var = ctk.StringVar(value=sistema.obtenerRutaSistema() or "Ruta no configurada")
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
        # Botón nuevo REQ3: abre ventana de cálculo de IMC
        ctk.CTkButton(barra, text="Calcular IMC",
                      command=self.abrirCalculoIMC, width=140, **estilo_btn).pack(side="left", padx=4, pady=6)
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

        ctk.CTkLabel(marco, text="Fecha nacimiento").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.fecha_nac_var = ctk.StringVar()
        self.fecha_nac_entry = DateEntry(
            marco,
            textvariable=self.fecha_nac_var,
            date_pattern="yyyy-mm-dd",
            width=12,
            background="#1f2633",
            foreground="white",
            borderwidth=1
        )
        self.fecha_nac_entry.grid(row=1, column=1, padx=5, pady=8)

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
        fecha_nac_txt = self.fecha_nac_var.get().strip()
        genero = self.genero_var.get().strip()
        peso_txt = self.peso_var.get().strip()
        estatura_txt = self.estatura_var.get().strip()

        validaciones = [
            val.validarID(id_valor, tipo),
            val.validarNombre(nombre),
            val.validarFechaNacimiento(fecha_nac_txt),
            val.validarGenero(genero),
            val.validarPeso(peso_txt),
            val.validarEstaturaMetros(estatura_txt),
        ]
        errores = [msg for msg in validaciones if msg]

        if errores:
            messagebox.showerror("Datos inválidos", "\n".join(errores))
            return

        edad = sistema.calcularEdadDesdeFecha(fecha_nac_txt) or 0
        peso = float(peso_txt)
        estatura = float(estatura_txt)
        # REQ1: registrar sin calcular IMC
        imc = None
        estado = "Sin calcular"

        persona = clasePersona(id_valor, nombre, edad, genero, peso, estatura, imc, estado, fecha_nacimiento=fecha_nac_txt)

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
            imc_txt = f"{p.imcCalculado:.2f}" if p.imcCalculado is not None else "Sin calcular"
            estado_txt = p.estado if p.estado not in [None, ""] else "Sin calcular"
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
                    imc_txt,
                    estado_txt,
                ),
            )
        if id_prev and id_prev in self.tabla.get_children():
            self._restoring_selection = True
            self.tabla.selection_set(id_prev)
            # libera el flag del evento de seleccion
            self.after_idle(self.limpiarSeleccion)
        if not self._closing and self.winfo_exists():
            self._after_id = self.after(1500, self.refrescarTabla)

    ##Limpia campos del formulario de la ventana principal
    def limpiarFormulario(self):
        self.id_var.set("")
        self.nombre_var.set("")
        try:
            self.fecha_nac_entry.set_date(date.today())
            self.fecha_nac_var.set(self.fecha_nac_entry.get_date().strftime("%Y-%m-%d"))
        except Exception:
            self.fecha_nac_var.set("")
        self.genero_var.set("Masculino")
        self.peso_var.set("")
        self.estatura_var.set("")
        self.tabla.selection_remove(self.tabla.selection())
        self.id_entry.configure(state="normal")

    ##Borra a partir de seleccion en tabla
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

    ##Funcion al seleccionar registro
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
        self.genero_var.set(valores[3] if valores[3] else "Masculino")
        self.peso_var.set(valores[4])
        self.estatura_var.set(valores[5])
        persona_obj = next((p for p in sistema.listaPersonas if str(p.id) == str(item_id)), None)
        if persona_obj and persona_obj.fecha_nacimiento:
            try:
                self.fecha_nac_entry.set_date(datetime.fromisoformat(persona_obj.fecha_nacimiento))
                self.fecha_nac_var.set(persona_obj.fecha_nacimiento)
            except Exception:
                pass
        # Bloquear ID en modo edición
        self.id_entry.configure(state="disabled")

    ## Funcion para limpiar filtro al presionar escape
    def _on_escape(self, _event=None):
        self.filtro_id = None
        self.msg_var.set("")
        self.limpiarFormulario()

    ##Para Salir total, cancela refresco y callbacks para evitar errores al cerrar mientras esta esperando algo
    def SalirTOTAL(self):
        if self._closing:
            return
        self._closing = True
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        try:
            self.cancelarTodosCallbacks()
        except Exception:
            pass
        # Intento de cierre seguro; ignoro errores de Tcl si ya se destruyeron comandos
        try:
            super().destroy()
        except Exception:
            try:
                self.quit()
            except Exception:
                pass

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

    ##Filtra por seleccion de ID
    def filtrar(self):
        idBuscar = simpledialog.askstring("Filtrar por ID", "Ingrese el ID a buscar:", parent=self)
        if idBuscar is None or idBuscar.strip() == "":
            return
        self.filtro_id = idBuscar.strip()
        self.msg_var.set(f"Filtro activo: ID {self.filtro_id}")
        self.refrescarTabla()

    ##Contruccion de ventana reportes
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

        ruta_frame = ctk.CTkFrame(canvas_frame, fg_color=("gray12"))
        ruta_frame.pack(fill="x", padx=6, pady=(0, 12))
        ctk.CTkLabel(ruta_frame, text="Ruta actual:", width=100).pack(side="left", padx=4)
        ctk.CTkLabel(ruta_frame, textvariable=self.ruta_label_var, text_color="lightgreen", anchor="w").pack(side="left", padx=4)

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

##Ventana para calculo de IMC, con hilos y consola de logs
    def abrirCalculoIMC(self):
        if self._ventana_calc and self._ventana_calc.winfo_exists():
            self._ventana_calc.lift()
            self._ventana_calc.focus_force()
            return
        if not sistema.listaPersonas:
            messagebox.showinfo("Sin registros", "No hay personas para calcular IMC.")
            return
        self._ventana_calc = VentanaCalculoIMC(self)

    def limpiarSeleccion(self):
        self._restoring_selection = False

    # Acciones de menuu
    def configuracionSistema(self):
        self.abrirConfiguracionSistema()
    
    ##Funcion para guardar archivos JSON-XML, muestra mensaje con rutas o error
    def guardarArchivos(self):
        try:
            archivo_json, archivo_xml = sistema.guardarInformacionArchivos()
            self.msg_var.set("Respaldo guardado.")
            messagebox.showinfo("Respaldo generado",
                                f"Archivos creados:\nJSON: {archivo_json}\nXML: {archivo_xml}")
        except ValueError as e:
            messagebox.showwarning("Ruta no configurada", str(e))
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el respaldo.\nDetalle: {e}")

     ## Carga desde respaldo XML
    def cargarRespaldo(self):
        try:
            cantidad = sistema.cargarDesdeRespaldo()
            self.msg_var.set(f"Respaldo cargado ({cantidad} registros).")
            self.refrescarTabla()
            messagebox.showinfo("Respaldo cargado", f"Se cargaron {cantidad} registros desde el XML.")
        except FileNotFoundError as e:
            messagebox.showwarning("Respaldo no encontrado", str(e))
        except ValueError as e:
            messagebox.showwarning("Ruta o datos inválidos", str(e))
        except Exception as e:
            messagebox.showerror("Error al cargar", f"No se pudo cargar el respaldo.\nDetalle: {e}")

    ##Contuctor de ventana de cong sistema
    def abrirConfiguracionSistema(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Configuración del sistema")
        ventana.geometry("480x200")
        ventana.resizable(False, False)
        ventana.lift()
        ventana.focus_force()
        ventana.attributes("-topmost", True)
        ventana.after(200, lambda: ventana.attributes("-topmost", False))

        cuerpo = ctk.CTkFrame(ventana, fg_color=("gray12"))
        cuerpo.pack(fill="both", expand=True, padx=16, pady=16)

        # refrescar label con valor actual del XML
        self.ruta_label_var.set(sistema.obtenerRutaSistema() or "Ruta no configurada")

        ruta_frame = ctk.CTkFrame(cuerpo, fg_color=("gray12"))
        ruta_frame.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(ruta_frame, text="Ruta actual:", width=110).pack(side="left", padx=4)
        ctk.CTkLabel(ruta_frame, textvariable=self.ruta_label_var,
                     text_color="lightgreen", anchor="w").pack(side="left", padx=4)

        botones = ctk.CTkFrame(cuerpo, fg_color=("gray12"))
        botones.pack(fill="x")
        ctk.CTkButton(botones, text="Seleccionar ruta del sistema para respaldos",
                      command=self.seleccionRutaSistema, width=260).pack(side="left", padx=6, pady=6)
        ctk.CTkButton(botones, text="Cerrar", width=120, command=ventana.destroy).pack(side="right", padx=6, pady=6)
    
    ##Funcon para seleccion ruta, guarda en XML
    def seleccionRutaSistema(self):
        ruta = filedialog.askdirectory(title="Seleccionar carpeta para archivos de respaldo del sistema", parent=self)
        if ruta:
            sistema.establecerRutaSistema(ruta)
            self.ruta_label_var.set(ruta)
            messagebox.showinfo("Ruta seleccionada", f"Ruta del sistema establecida en:\n{ruta}")
        else:
            messagebox.showwarning("Sin selección", "No se seleccionó ninguna carpeta. La ruta del sistema no se ha cambiado.")
        
# Ventana cálculo de IMC con hilos y consola de logs
class VentanaCalculoIMC(ctk.CTkToplevel):
    def __init__(self, master: VentanaPrincipal):
        super().__init__(master)
        self.master = master
        self.title("Calcular IMC - Consola de logs")
        self.geometry("620x420")
        self.resizable(False, False)
        self.log_queue: Queue[str] = Queue()
        self.threads: list[threading.Thread] = []
        self._poll_after_id = None
        self._monitor_after_id = None
        self.en_progreso = False

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.construir_ui()

    def construir_ui(self):
        cont = ctk.CTkFrame(self, fg_color="gray12")
        cont.pack(fill="both", expand=True, padx=10, pady=10)

        fila = ctk.CTkFrame(cont, fg_color="gray12")
        fila.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(fila, text="Cantidad de hilos:").pack(side="left", padx=(0, 6))
        self.hilos_var = ctk.StringVar(value=str(min(4, max(1, len(sistema.listaPersonas)))))
        self.hilos_entry = ctk.CTkEntry(fila, textvariable=self.hilos_var, width=80)
        self.hilos_entry.pack(side="left", padx=(0, 10))
        self.btn_iniciar = ctk.CTkButton(fila, text="Iniciar cálculo", command=self.iniciar_calculo, width=140)
        self.btn_iniciar.pack(side="left")

        self.log_text = ScrolledText(cont, height=16, state="disabled", wrap="word", background="#1f2633", foreground="white")
        self.log_text.pack(fill="both", expand=True)

        self._log("Iniciando ventana de cálculo...")

    def _log(self, msg: str):
        self.log_queue.put(msg)
        self._poll_queue()


##CALCULO DE IMC CON HILOS, divide el trabajo en segmentos según cantidad de hilos
    def iniciar_calculo(self):
        if self.en_progreso:
            return
        total = len(sistema.listaPersonas)
        try:
            n_hilos = int(self.hilos_var.get())
        except Exception:
            messagebox.showerror("Valor inválido", "Ingrese un número de hilos válido.")
            return
        if n_hilos <= 0:
            messagebox.showerror("Valor inválido", "La cantidad de hilos debe ser mayor a 0.")
            return
        if total == 0:
            messagebox.showinfo("Sin datos", "No hay registros para procesar.")
            return
        if n_hilos > total:
            n_hilos = total
            self.hilos_var.set(str(n_hilos))
            messagebox.showinfo("Ajuste de hilos", f"Se ajustó la cantidad de hilos a {n_hilos} (cantidad de registros).")

##El residuo se pasa al ultimo
        base = total // n_hilos
        residuo = total % n_hilos
        segmentos = []
        inicio = 0
        for i in range(n_hilos):
            fin = inicio + base
            if i == n_hilos - 1:
                fin += residuo
            segmentos.append(range(inicio, fin))
            inicio = fin

        self._log(f"Iniciando cálculo... registros: {total}, hilos: {n_hilos}")
        self._log("Creando hilos...")
        self.threads = []
        for idx, seg in enumerate(segmentos, start=1):
            hilo = HiloIMC(
                seg,
                self.log_queue,
                sistema.listaPersonas,
                sistema.calcularIMC,
                sistema.estadoIMC,
                lock=sistema.imc_lock,
                nombre=f"Hilo {idx}",
            )
            self.threads.append(hilo)
        for hilo in self.threads:
            hilo.start()

        self.en_progreso = True
        self.btn_iniciar.configure(state="disabled")
        self._poll_queue()
        self._monitor_threads()

    def _poll_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", msg + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except Empty:
            pass
        if (self.en_progreso or not self.log_queue.empty()) and self.winfo_exists():
            self._poll_after_id = self.after(30, self._poll_queue)

    def _monitor_threads(self):
        vivos = any(t.is_alive() for t in self.threads)
        if vivos:
            self._monitor_after_id = self.after(150, self._monitor_threads)
            return
        # finalizó
        self.en_progreso = False
        self.btn_iniciar.configure(state="normal")
        self._log("Todos los hilos finalizaron.")
        self._log("Proceso completado.")
        try:
            self.master.refrescarTabla()
        except Exception:
            pass

    def _on_close(self):
        if self.en_progreso:
            messagebox.showwarning("Cálculo en curso", "Espere a que finalice el cálculo antes de cerrar.")
            return
        if self._poll_after_id:
            try:
                self.after_cancel(self._poll_after_id)
            except Exception:
                pass
        if self._monitor_after_id:
            try:
                self.after_cancel(self._monitor_after_id)
            except Exception:
                pass
        self.destroy()


if __name__ == "__main__":
    VentanaPrincipal().mainloop()
