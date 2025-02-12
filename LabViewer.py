import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap
from PyQt5 import uic
from PyQt5 import  QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime, timedelta
import sqlite3
import copy
import json

with open("User data/general_data.json","r") as file:
    generalData=json.load(file)


tiempoCambio=generalData["updateTimeViewer"]
#Tiempo que dura en cambiar de elemnto

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

flujosProhibidos=generalData["forbiddenRoutes"]
#-------------------------------------------------------
def queryFlujosProhibidos():
    salida=""
    for n in flujosProhibidos:
        salida+="'"+n+"',"
    salida=salida[:len(salida)-1]
    salida="("+salida+")"
    return salida


def extraerData():
    conexion=sqlite3.connect("User Data/data.db")
    cursor=conexion.cursor()
    data=cursor.execute(f"SELECT SERIAL, COMPONENT,FLOW_CUR,FLOW_CUR_STATUS,NEXT_FLOW,ON_HOLD,PRIORITY,COMMENTS,ID FROM SAMPLES WHERE FLOW_CUR NOT IN {queryFlujosProhibidos()};")
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


        consultaSerial=cursor.execute(f"SELECT CASE_NAME FROM CASES WHERE SERIAL=?",(muestra[0],))
        
       
        temp["Caso"]=consultaSerial.fetchall()[0][0]

        consultaMovimiento=cursor.execute(f"SELECT DATE, USER FROM SAMPLES_CHANGES WHERE SAMPLE=? ORDER BY DATE DESC LIMIT 1;",(muestra[8],))
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
        font = QFont("Verdana", 12)  # Cambia la fuente y tamaño según lo necesites


        self.setStyleSheet("""QMainWindow{
        background:#101010;}""")
        self.logo=self.findChild(QLabel,"logo")
        pixmap=QPixmap("User Data/ingrasysLogo_2.png")
        self.logo.setPixmap(pixmap.scaled(200, 70, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.logo.setStyleSheet("""
            QLabel{
            padding:20px;
            }
        """)
        self.logo.mousePressEvent=self.on_click
        
        titulo=self.findChild(QLabel,"titulo")
        titulo.setText("Laboratory Tracking")
        fontTitulo= QFont("Verdana", 20)
        titulo.setFont(fontTitulo)
        titulo.setStyleSheet("""
            QLabel{
                color:white;

            }
        """)

        self.contador=self.findChild(QLabel,"contador")
        self.contador.setStyleSheet("""
            QLabel{
                color:white;
                padding:20px;
            }
        """)
        self.contador.setFont(font)
        self.contador.setText("No. of samples: 0")

        self.tabla = self.findChild(QTableWidget, "tabla")
        self.tabla.setRowCount(0)  # Número de filas
        self.tabla.setColumnCount(8)  # Número de columnas
        self.tabla.setHorizontalHeaderLabels(["Case", "Serial", "Component","Engineer","Date","Route","Next Route","Comments"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.setFont(font)

        self.tabla.setStyleSheet("""
    QTableWidget {
        background-color: #262626;  /* Color de fondo de la tabla */
        border: 1px solid #151515;   /* Borde de la tabla */
        gridline-color: #101010;     /* Color de las líneas de la cuadrícula */
    }
    
    QTableWidget::item {
        color: white;                /* Color del texto */
        padding: 10px;               /* Espaciado dentro de las celdas
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

        self.indices=[]
    
    def mostrarData(self):
        self.tabla.setRowCount(self.filas_visibles())

        self.contador.setText(f"No. of samples: {len(self.data)}")

        for pos,row in enumerate(self.indices):
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
            if(self.data[row]["Pausa"]==1):
                item_ruta_actual.setBackground(QBrush(QColor(128,128,128)))
            elif(self.data[row]["EstatusRuta"]=="IN"):
                item_ruta_actual.setBackground(QBrush(QColor(119,217,120)))
            elif((self.data[row]["EstatusRuta"]=="OUT")):
                item_ruta_actual.setBackground(QBrush(QColor(224,80,76)))
            # Añadir los ítems a la tabla
            self.tabla.setItem(pos, 0, item_caso)
            self.tabla.setItem(pos, 1, item_serial)
            self.tabla.setItem(pos, 2, item_componente)
            self.tabla.setItem(pos, 3, item_ingeniero)
            self.tabla.setItem(pos, 4, item_date)
            self.tabla.setItem(pos, 5, item_ruta_actual)
            self.tabla.setItem(pos, 6, item_siguiente_ruta)
            self.tabla.setItem(pos, 7, item_comentarios)

            
    def moverIndice(self):
        if(len(self.data)>0):
            if self.filas_visibles()>len(self.data):
                
                self.indices=[]
                for indice,n in enumerate(self.data):
                    self.indices.append(indice)
                
                print("Ingreso a filas es menor que la cantidad de datos")
            else:
                
                if len(self.indices)>0:
                    
                    temp=self.indices[0]+1
                    self.indices=[]
                    for n in range(self.filas_visibles()):
                        if n>len(self.data):
                            temp=0
                        self.indices.append(temp)
                        temp+=1
                    print("Ingreso a indices es mayor a 0")
                else:
                    self.indices=[]
                    for indice in range(self.filas_visibles()):
                        self.indices.append(indice) 

                    print(self.indices)
                    print("Ingreso a indices es menor a 0")
        else:
            self.indices=[]
        self.mostrarData()


    def update_data(self, data):
        self.data=data
        #self.mostrarData()

    def filas_visibles(self):
        return 32

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()  # Volver al tamaño normal al presionar Escape
        super().keyPressEvent(event)
    
    def on_click(self, event):
        # Llamar a showFullScreen desde aquí
        self.showFullScreen()


# Configurar la aplicación y mostrar la ventana
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
