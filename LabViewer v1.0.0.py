import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt5 import uic
from PyQt5 import  QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime, timedelta

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

class DataGenerationThread(QThread):
    # Señal para enviar los datos generados al hilo principal
    data_generated_signal = pyqtSignal(list)

    def run(self):
        while True:
            # Generar datos aleatorios para la tabla
            data = [generar_dato_aleatorio() for _ in range(30)]   # 5 filas x 3 columnas de números aleatorios
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
            self.tabla.setItem(row,0,QTableWidgetItem(str(self.data[row]["Caso"])))
            self.tabla.setItem(row,1,QTableWidgetItem(str(self.data[row]["Serial"])))
            self.tabla.setItem(row,2,QTableWidgetItem(str(self.data[row]["Componente"])))
            self.tabla.setItem(row,3,QTableWidgetItem(str(self.data[row]["Ingeniero"])))
            self.tabla.setItem(row,4,QTableWidgetItem(str(self.data[row]["Date"])))
            self.tabla.setItem(row,5,QTableWidgetItem(str(self.data[row]["RutaActual"])))
            self.tabla.setItem(row,6,QTableWidgetItem(str(self.data[row]["SiguienteRuta"])))
            self.tabla.setItem(row,7,QTableWidgetItem(str(self.data[row]["Comentarios"])))
    
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
