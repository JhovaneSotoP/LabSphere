import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont
from PyQt5 import uic
from PyQt5 import  QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime, timedelta
import sqlite3
import copy

tiempoCambio=2 #Tiempo que dura en cambiar de elemnto

elementoBase={"Caso":"",
              "Serial":"",
              "Componente":"",
              "Date":"",
              "RutaActual":"",
              "SiguienteRuta":"",
              "Ingeniero":"",
              "Comentarios":"",
              "EstatusRuta":"",
              "Pausa":0,
              "Prioridad":0}

# Lista de valores posibles para cada campo
componentes = ["Resistor", "Capacitor", "Microchip", "Diodo", "Transistor"]
rutas = ["Inspección", "Ensamblaje", "Pruebas", "Empaque", "Almacenaje"]
ingenieros = ["Juan Pérez", "Ana Gómez", "Carlos Torres", "Laura Ramírez", "José Fernández"]
comentarios_posibles = ["Sin comentarios", "Requiere revisión", "Pendiente de aprobación", "Completado", "Error detectado"]
estatus_ruta = ["En proceso", "Completo", "Pendiente", "Pausado"]

# Generador de datos aleatorios-----------------------------------------
def generar_dato_aleatorio():
    # Crear una fecha aleatoria
    date_in = datetime.now() - timedelta(days=random.randint(0, 30))
    date_out = date_in + timedelta(days=random.randint(1, 5))
    
    return {
        "Caso": f"C{random.randint(1000, 9999)}",
        "Serial": f"S{random.randint(100000, 999999)}",
        "Componente": random.choice(componentes),
        "Date": date_in.strftime("%Y-%m-%d"),
        "RutaActual": random.choice(rutas),
        "SiguienteRuta": random.choice(rutas),
        "Ingeniero": random.choice(ingenieros),
        "Comentarios": random.choice(comentarios_posibles),
        "EstatusRuta": random.choice(estatus_ruta),
        "Pausa": random.randint(0, 1),
        "Prioridad": random.randint(0, 1)
    }

#-------------------------------------------------------

def extraerData():
    conexion=sqlite3.connect("User Data/data.db")
    cursor=conexion.cursor()
    data=cursor.execute("SELECT SERIAL, COMPONENT,FLOW_CUR,FLOW_CUR_STATUS,NEXT_FLOW,ON_HOLD,PRIORITY,COMMENTS,ID FROM SAMPLES WHERE FLOW_CUR NOT IN ('END', 'Completo');")
    salida=[]
    for muestra in data.fetchall():
        temp=copy.deepcopy(elementoBase)
        temp["Serial"]=muestra[0]
        temp["Componente"]=muestra[1]
        temp["RutaActual"]=muestra[2]
        temp["SiguienteRuta"]=muestra[4]
        temp["Comentarios"]=muestra[7]
        temp["EstatusRuta"]=muestra[3]
        temp["Pausa"]=muestra[5]
        temp["Prioridad"]=muestra[6]

        consultaSerial=cursor.execute(f"SELECT CASE_NAME FROM CASES WHERE SERIAL={muestra[0]}")
        temp["Caso"]=consultaSerial.fetchall()[0][0]

        consultaMovimiento=cursor.execute(f"SELECT DATE, USER FROM SAMPLES_CHANGES WHERE SAMPLE={muestra[8]} ORDER BY DATE DESC LIMIT 1;")
        movimiento=consultaMovimiento.fetchall()[0]
        temp["Date"]=movimiento[0]
        temp["Ingeniero"]=movimiento[1]

        salida.append(temp)
    conexion.close()
    return salida

# {"Caso":"",
#               "Serial":"",-----------
#               "Componente":"",----------
#               "Date":"",
#               "RutaActual":"",----------
#               "SiguienteRuta":"",--------
#               "Ingeniero":"",
#               "Comentarios":"",--------
#               "EstatusRuta":"",-------
#               "Pausa":0,----------
#               "Prioridad":0}--------

class DataGenerationThread(QThread):
    # Señal para enviar los datos generados al hilo principal
    data_generated_signal = pyqtSignal(list)

    def run(self):
        while True:
            # Generar datos aleatorios para la tabla
            data = extraerData()
            self.data_generated_signal.emit(data)  # Emitir la señal con los datos generados
            prioridad_cero = sum(1 for dato in data if dato["Prioridad"] == 0)

            self.sleep(prioridad_cero*tiempoCambio)  # Esperar 10 segundos antes de generar nuevos datos

class timer(QThread):
    girar=pyqtSignal()

    def run(self):
        while(1):
            self.sleep(tiempoCambio)
            self.girar.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Interfaz/interfazLabView.ui", self)  # Cargar interfaz .ui
        # Configurar la tabla
        self.tabla = self.findChild(QTableWidget, "tabla")
        self.tabla.setRowCount(0)  # Número de filas
        self.tabla.setColumnCount(8)  # Número de columnas
        self.tabla.setHorizontalHeaderLabels(["Case", "Serial", "Component","Engineer","Date","Route","Next Route","Comments"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        font = QFont("Verdana", 12)  # Cambia la fuente y tamaño según lo necesites
        self.tabla.setFont(font)

        self.tabla.setStyleSheet("""
    QTableWidget {
        background-color: #262626;  /* Color de fondo de la tabla */
        border: 1px solid #000000;   /* Borde de la tabla */
        gridline-color: #cccccc;     /* Color de las líneas de la cuadrícula */
    }
    QTableWidget::item {
        background-color: #262626;  /* Color de fondo de las celdas */
        color: white;                /* Color del texto */
        padding: 10px;               /* Espaciado dentro de las celdas */
    }
    QTableWidget::item:selected {
        background-color: #007bff;   /* Color de fondo cuando un ítem está seleccionado */
        color: white;                /* Color del texto cuando un ítem está seleccionado */
    }
""")
        self.tabla.horizontalHeader().setStyleSheet("""
    QHeaderView::section {
        background-color: #202020;  /* Fondo verde */
        color: white;               /* Color blanco para el texto */
        font-size: 14px;            /* Tamaño de fuente */
        padding: 10px;              /* Espaciado en los encabezados */
    }
""")

        self.tabla.horizontalHeader().setStretchLastSection(True)

        #Deshabilitar el scroll
        self.tabla.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Desactivar la barra de desplazamiento horizontal
        self.tabla.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Desactivar la barra de desplazamiento vertical

        #Ocultar header de las filas
        self.tabla.verticalHeader().setVisible(False)

        self.data=[]
        # Inicializar el hilo de generación de datos
        self.data_thread = DataGenerationThread()
        self.data_thread.data_generated_signal.connect(self.update_data)  # Conectar la señal al método que actualiza la tabla
        self.data_thread.start()  # Iniciar el hilo

        #hilo de rotacion
        self.rotarThread=timer()
        self.rotarThread.girar.connect(self.moverIndice)
        self.rotarThread.start()
        # Mostrar la ventana en pantalla completa
        self.showFullScreen()
    
    def mostrarData(self):
        self.tabla.setRowCount(len(self.data))
        # Llenar la tabla con los datos generados por el hilo
        for row in range(len(self.data)):
            item_caso = QTableWidgetItem(str(self.data[row]["Caso"]))
            item_serial = QTableWidgetItem(str(self.data[row]["Serial"]))
            item_componente = QTableWidgetItem(str(self.data[row]["Componente"]))
            item_ingeniero = QTableWidgetItem(str(self.data[row]["Ingeniero"]))
            item_date = QTableWidgetItem(str(self.data[row]["Date"]))
            item_ruta_actual = QTableWidgetItem(str(self.data[row]["RutaActual"]))
            item_siguiente_ruta = QTableWidgetItem(str(self.data[row]["SiguienteRuta"]))
            item_comentarios = QTableWidgetItem(str(self.data[row]["Comentarios"]))

            # Centrar los ítems
            item_caso.setTextAlignment(Qt.AlignCenter)
            item_serial.setTextAlignment(Qt.AlignCenter)
            item_componente.setTextAlignment(Qt.AlignCenter)
            item_ingeniero.setTextAlignment(Qt.AlignCenter)
            item_date.setTextAlignment(Qt.AlignCenter)
            item_ruta_actual.setTextAlignment(Qt.AlignCenter)
            item_siguiente_ruta.setTextAlignment(Qt.AlignCenter)
            item_comentarios.setTextAlignment(Qt.AlignCenter)

            #editar
            # Añadir los ítems a la tabla
            self.tabla.setItem(row, 0, item_caso)
            self.tabla.setItem(row, 1, item_serial)
            self.tabla.setItem(row, 2, item_componente)
            self.tabla.setItem(row, 3, item_ingeniero)
            self.tabla.setItem(row, 4, item_date)
            self.tabla.setItem(row, 5, item_ruta_actual)
            self.tabla.setItem(row, 6, item_siguiente_ruta)
            self.tabla.setItem(row, 7, item_comentarios)

            
    def moverIndice(self):
        if(len(self.data)>0 and self.filas_visibles()<len(self.data)):
            cont=0
            while cont<len(self.data):
                if(self.data[cont]["Prioridad"]==0):
                    temp=self.data[cont]
                    self.data.pop(cont)
                    self.data.append(temp)
                    break
                else:
                    cont+=1
        self.mostrarData()


    def update_data(self, data):
        self.data=data
        self.mostrarData()

    def filas_visibles(self):
    # Altura total del área visible
        altura_visible = self.tabla.viewport().height()
        
        # Altura promedio de una fila
        if self.tabla.rowCount() > 0:
            altura_fila = self.tabla.rowHeight(0)  # Asume que todas las filas tienen la misma altura
        else:
            return 0  # No hay filas
        
        # Número de filas que caben en el área visible
        return altura_visible // altura_fila

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()  # Volver al tamaño normal al presionar Escape
        super().keyPressEvent(event)


# Configurar la aplicación y mostrar la ventana
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
