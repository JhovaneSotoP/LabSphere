import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class DataGenerationThread(QThread):
    # Señal para enviar los datos generados al hilo principal
    data_generated_signal = pyqtSignal(list)

    def run(self):
        while True:
            # Generar datos aleatorios para la tabla
            data = [[random.randint(0, 100) for _ in range(3)] for _ in range(5)]  # 5 filas x 3 columnas de números aleatorios
            self.data_generated_signal.emit(data)  # Emitir la señal con los datos generados
            self.sleep(10)  # Esperar 10 segundos antes de generar nuevos datos


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Interfaz/interfazLabView.ui", self)  # Cargar interfaz .ui

        # Configurar la tabla
        self.tabla = self.findChild(QTableWidget, "tabla")
        self.tabla.setRowCount(5)  # Número de filas
        self.tabla.setColumnCount(3)  # Número de columnas
        self.tabla.setHorizontalHeaderLabels(["Columna 1", "Columna 2", "Columna 3"])

        # Inicializar el hilo de generación de datos
        self.data_thread = DataGenerationThread()
        self.data_thread.data_generated_signal.connect(self.update_table)  # Conectar la señal al método que actualiza la tabla
        self.data_thread.start()  # Iniciar el hilo

        # Mostrar la ventana en pantalla completa
        self.showFullScreen()

    def update_table(self, data):
        # Llenar la tabla con los datos generados por el hilo
        for row in range(len(data)):
            for col in range(len(data[row])):
                self.tabla.setItem(row, col, QTableWidgetItem(str(data[row][col])))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()  # Volver al tamaño normal al presionar Escape
        super().keyPressEvent(event)


# Configurar la aplicación y mostrar la ventana
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
